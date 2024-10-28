import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('PGHOST'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            port=os.getenv('PGPORT')
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Devices table with thresholds
            cur.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(15) NOT NULL,
                    description TEXT,
                    tags TEXT[],
                    device_type VARCHAR(50),
                    response_time_threshold FLOAT,
                    packet_loss_threshold FLOAT,
                    jitter_threshold FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add threshold columns to existing table if they don't exist
            cur.execute('''
                DO $$ 
                BEGIN
                    BEGIN
                        ALTER TABLE devices ADD COLUMN device_type VARCHAR(50);
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                    BEGIN
                        ALTER TABLE devices ADD COLUMN response_time_threshold FLOAT;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                    BEGIN
                        ALTER TABLE devices ADD COLUMN packet_loss_threshold FLOAT;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                    BEGIN
                        ALTER TABLE devices ADD COLUMN jitter_threshold FLOAT;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                END $$;
            ''')
            
            # Monitoring history table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_history (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES devices(id),
                    response_time FLOAT,
                    status BOOLEAN,
                    min_rtt FLOAT,
                    max_rtt FLOAT,
                    avg_rtt FLOAT,
                    jitter FLOAT,
                    packet_loss FLOAT,
                    threshold_violations TEXT[],
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add threshold_violations column if it doesn't exist
            cur.execute('''
                DO $$ 
                BEGIN
                    BEGIN
                        ALTER TABLE monitoring_history ADD COLUMN threshold_violations TEXT[];
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                END $$;
            ''')
        self.conn.commit()

    def add_device(self, ip_address, description, tags, device_type=None, 
                  response_time_threshold=None, packet_loss_threshold=None, 
                  jitter_threshold=None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO devices 
                (ip_address, description, tags, device_type, 
                response_time_threshold, packet_loss_threshold, jitter_threshold)
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                RETURNING id
                """,
                (ip_address, description, tags, device_type,
                response_time_threshold, packet_loss_threshold, jitter_threshold)
            )
            device_id = cur.fetchone()[0]
        self.conn.commit()
        return device_id

    def get_devices(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM devices ORDER BY created_at DESC")
            return cur.fetchall()

    def update_device(self, device_id, ip_address, description, tags, device_type=None,
                     response_time_threshold=None, packet_loss_threshold=None,
                     jitter_threshold=None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE devices 
                SET ip_address = %s, description = %s, tags = %s,
                    device_type = %s, response_time_threshold = %s,
                    packet_loss_threshold = %s, jitter_threshold = %s
                WHERE id = %s
                """,
                (ip_address, description, tags, device_type,
                 response_time_threshold, packet_loss_threshold,
                 jitter_threshold, device_id)
            )
        self.conn.commit()

    def delete_device(self, device_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        self.conn.commit()

    def add_monitoring_record(self, device_id, response_time, status, min_rtt=-1, max_rtt=-1, 
                            avg_rtt=-1, jitter=-1, packet_loss=100):
        # Check for threshold violations
        violations = []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
            device = cur.fetchone()
            
            if device:
                if (device['response_time_threshold'] is not None and 
                    response_time > device['response_time_threshold']):
                    violations.append('response_time')
                
                if (device['packet_loss_threshold'] is not None and 
                    packet_loss > device['packet_loss_threshold']):
                    violations.append('packet_loss')
                
                if (device['jitter_threshold'] is not None and 
                    jitter > device['jitter_threshold']):
                    violations.append('jitter')

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring_history 
                (device_id, response_time, status, min_rtt, max_rtt, 
                avg_rtt, jitter, packet_loss, threshold_violations)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (device_id, response_time, status, min_rtt, max_rtt, 
                avg_rtt, jitter, packet_loss, violations if violations else None)
            )
        self.conn.commit()

    def get_device_history(self, device_id, limit=100):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM monitoring_history 
                WHERE device_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
                """,
                (device_id, limit)
            )
            return cur.fetchall()

    def get_device_trends(self, device_id, hours=24):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    date_trunc('hour', timestamp) as time_bucket,
                    AVG(response_time) as avg_response_time,
                    AVG(packet_loss) as avg_packet_loss,
                    AVG(jitter) as avg_jitter,
                    COUNT(*) FILTER (WHERE status = true)::float / COUNT(*)::float * 100 as availability
                FROM monitoring_history 
                WHERE device_id = %s 
                AND timestamp >= NOW() - interval %s hour
                GROUP BY time_bucket
                ORDER BY time_bucket DESC
                """,
                (device_id, hours)
            )
            return cur.fetchall()
