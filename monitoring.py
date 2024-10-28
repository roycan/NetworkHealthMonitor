import threading
import time
from ping3 import ping
from datetime import datetime
import statistics

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

    def _collect_detailed_metrics(self, ip_address, num_pings=5):
        ping_results = []
        packet_loss = 0

        for _ in range(num_pings):
            try:
                response_time = ping(ip_address, timeout=2)
                if response_time is not None:
                    ping_results.append(response_time)
                else:
                    packet_loss += 1
            except Exception:
                packet_loss += 1
            time.sleep(0.2)  # Small delay between pings

        metrics = {
            'response_time': -1,
            'min_rtt': -1,
            'max_rtt': -1,
            'avg_rtt': -1,
            'jitter': -1,
            'packet_loss': (packet_loss / num_pings) * 100,
            'status': False
        }

        if ping_results:
            metrics.update({
                'response_time': ping_results[-1],
                'min_rtt': min(ping_results),
                'max_rtt': max(ping_results),
                'avg_rtt': statistics.mean(ping_results),
                'jitter': statistics.stdev(ping_results) if len(ping_results) > 1 else 0,
                'status': True
            })

        return metrics

    def _monitoring_loop(self):
        while self.running:
            devices = self.database.get_devices()
            for device in devices:
                metrics = self._collect_detailed_metrics(device['ip_address'])
                self.database.add_monitoring_record(
                    device['id'],
                    metrics['response_time'],
                    metrics['status'],
                    metrics['min_rtt'],
                    metrics['max_rtt'],
                    metrics['avg_rtt'],
                    metrics['jitter'],
                    metrics['packet_loss']
                )
            time.sleep(60)  # Monitor every minute

    def check_device(self, ip_address):
        metrics = self._collect_detailed_metrics(ip_address)
        return metrics['status'], metrics['response_time']
