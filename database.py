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
            # Devices table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(15) NOT NULL,
                    description TEXT,
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Monitoring history table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_history (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES devices(id),
                    response_time FLOAT,
                    status BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        self.conn.commit()

    def add_device(self, ip_address, description, tags):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO devices (ip_address, description, tags) VALUES (%s, %s, %s) RETURNING id",
                (ip_address, description, tags)
            )
            device_id = cur.fetchone()[0]
        self.conn.commit()
        return device_id

    def get_devices(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM devices ORDER BY created_at DESC")
            return cur.fetchall()

    def update_device(self, device_id, ip_address, description, tags):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE devices SET ip_address = %s, description = %s, tags = %s WHERE id = %s",
                (ip_address, description, tags, device_id)
            )
        self.conn.commit()

    def delete_device(self, device_id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        self.conn.commit()

    def add_monitoring_record(self, device_id, response_time, status):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO monitoring_history (device_id, response_time, status) VALUES (%s, %s, %s)",
                (device_id, response_time, status)
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
