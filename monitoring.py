import threading
import time
from ping3 import ping
from datetime import datetime

class NetworkMonitor:
    def __init__(self, database):
        self.database = database
        self.running = False
        self.monitor_thread = None

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitoring_loop(self):
        while self.running:
            devices = self.database.get_devices()
            for device in devices:
                try:
                    response_time = ping(device['ip_address'], timeout=2)
                    status = response_time is not None
                    if response_time is None:
                        response_time = -1
                except Exception:
                    response_time = -1
                    status = False
                
                self.database.add_monitoring_record(
                    device['id'],
                    response_time,
                    status
                )
            time.sleep(60)  # Monitor every minute

    def check_device(self, ip_address):
        try:
            response_time = ping(ip_address, timeout=2)
            return response_time is not None, response_time if response_time else -1
        except Exception:
            return False, -1
