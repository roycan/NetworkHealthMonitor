import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('network_monitor.db', check_same_thread=False)
        # Enable dictionary cursor by default
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Devices table with thresholds
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address VARCHAR(15) NOT NULL,
                    description TEXT,
                    tags TEXT,
                    device_type VARCHAR(50),
                    response_time_threshold FLOAT,
                    packet_loss_threshold FLOAT,
                    jitter_threshold FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Monitoring history table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER REFERENCES devices(id),
                    response_time FLOAT,
                    status INTEGER,
                    min_rtt FLOAT,
                    max_rtt FLOAT,
                    avg_rtt FLOAT,
                    jitter FLOAT,
                    packet_loss FLOAT,
                    threshold_violations TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
                )
            ''')

    def add_device(self, ip_address, description, tags, device_type=None, 
                  response_time_threshold=None, packet_loss_threshold=None, 
                  jitter_threshold=None):
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO devices 
                (ip_address, description, tags, device_type, 
                response_time_threshold, packet_loss_threshold, jitter_threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?) 
                """,
                (ip_address, description, ','.join(tags), device_type,
                float(response_time_threshold) if response_time_threshold is not None else None,
                float(packet_loss_threshold) if packet_loss_threshold is not None else None,
                float(jitter_threshold) if jitter_threshold is not None else None)
            )
            return cursor.lastrowid

    def get_devices(self):
        cursor = self.conn.execute("SELECT * FROM devices ORDER BY created_at DESC")
        devices = []
        for row in cursor:
            device = dict(row)
            # Convert tags string to list
            device['tags'] = device['tags'].split(',') if device['tags'] else []
            devices.append(device)
        return devices

    def update_device(self, device_id, ip_address, description, tags, device_type=None,
                     response_time_threshold=None, packet_loss_threshold=None,
                     jitter_threshold=None):
        with self.conn:
            self.conn.execute(
                """
                UPDATE devices 
                SET ip_address = ?, description = ?, tags = ?,
                    device_type = ?, response_time_threshold = ?,
                    packet_loss_threshold = ?, jitter_threshold = ?
                WHERE id = ?
                """,
                (ip_address, description, ','.join(tags), device_type,
                 float(response_time_threshold) if response_time_threshold is not None else None,
                 float(packet_loss_threshold) if packet_loss_threshold is not None else None,
                 float(jitter_threshold) if jitter_threshold is not None else None,
                 int(device_id))
            )

    def delete_device(self, device_id):
        with self.conn:
            self.conn.execute("DELETE FROM devices WHERE id = ?", (int(device_id),))

    def add_monitoring_record(self, device_id, response_time, status, min_rtt=-1, max_rtt=-1, 
                            avg_rtt=-1, jitter=-1, packet_loss=100):
        # Check for threshold violations
        violations = []
        cursor = self.conn.execute("SELECT * FROM devices WHERE id = ?", (int(device_id),))
        device = cursor.fetchone()
        
        if device:
            if (device['response_time_threshold'] is not None and 
                float(response_time) > float(device['response_time_threshold'])):
                violations.append('response_time')
            
            if (device['packet_loss_threshold'] is not None and 
                float(packet_loss) > float(device['packet_loss_threshold'])):
                violations.append('packet_loss')
            
            if (device['jitter_threshold'] is not None and 
                float(jitter) > float(device['jitter_threshold'])):
                violations.append('jitter')

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO monitoring_history 
                (device_id, response_time, status, min_rtt, max_rtt, 
                avg_rtt, jitter, packet_loss, threshold_violations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (int(device_id), float(response_time), 1 if status else 0,
                float(min_rtt), float(max_rtt), float(avg_rtt),
                float(jitter), float(packet_loss),
                ','.join(violations) if violations else None)
            )

    def get_device_history(self, device_id, limit=100):
        query = """
            SELECT * FROM monitoring_history 
            WHERE device_id = ? 
            ORDER BY timestamp DESC
        """
        params = [int(device_id)]
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(int(limit))
            
        cursor = self.conn.execute(query, params)
        history = []
        for row in cursor:
            record = dict(row)
            # Convert threshold_violations string to list
            record['threshold_violations'] = (
                record['threshold_violations'].split(',') 
                if record['threshold_violations'] else []
            )
            # Convert status to boolean
            record['status'] = bool(record['status'])
            # Ensure numeric fields are float
            for field in ['response_time', 'min_rtt', 'max_rtt', 'avg_rtt', 'jitter', 'packet_loss']:
                record[field] = float(record[field])
            history.append(record)
        return history

    def get_device_trends(self, device_id, hours=24):
        cursor = self.conn.execute(
            """
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as time_bucket,
                AVG(response_time) as avg_response_time,
                AVG(packet_loss) as avg_packet_loss,
                AVG(jitter) as avg_jitter,
                CAST(SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
                CAST(COUNT(*) AS FLOAT) * 100 as availability
            FROM monitoring_history 
            WHERE device_id = ? 
            AND timestamp >= datetime('now', ?)
            GROUP BY time_bucket
            ORDER BY time_bucket DESC
            """,
            (int(device_id), f'-{int(hours)} hours')
        )
        return [dict(row) for row in cursor]
