# modules/system_monitor.py
# UPDATED TO USE THEIR METRICS COLLECTOR

import sys
import os

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

# Add system_prediction to path
sys.path.insert(0, os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    'system_prediction'
))

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None
import time

class SystemMonitor:

    def __init__(self):
        self.available = psutil is not None
        if not self.available:
            self.last_sent = 0
            self.last_recv = 0
            self.last_time = time.time()
            self.prev_net = None
            self.prev_time = time.time()
            return

        net              = psutil.net_io_counters()
        self.last_sent   = net.bytes_sent
        self.last_recv   = net.bytes_recv
        self.last_time   = time.time()
        self.prev_net    = net
        self.prev_time   = time.time()

    def collect_metrics(self):

        if not self.available:
            print("psutil is not installed; returning zero metrics.")
            return {
                "CPU": 0,
                "Memory": 0,
                "Disk": 0,
                "Network": 0,
                "Processes": 0,
                "cpu": 0,
                "memory": 0,
                "disk": 0,
                "network": 0,
                "processes": 0,
                "network_sent": 0,
                "network_recv": 0,
                "network_speed_up": 0,
                "network_speed_down": 0,
                "process_count": 0,
                "top_processes": []
            }

        # CPU Memory Disk
        cpu    = psutil.cpu_percent(interval=0.2)
        memory = psutil.virtual_memory().percent
        disk   = psutil.disk_usage('/').percent

        # Process Count
        processes = len(psutil.pids())

        # Network (their method - normalized 0-100)
        current      = psutil.net_io_counters()
        current_time = time.time()

        bytes_now  = (current.bytes_sent +
                      current.bytes_recv)
        bytes_prev = (self.prev_net.bytes_sent +
                      self.prev_net.bytes_recv)

        elapsed = max(
            current_time - self.prev_time,
            0.1
        )
        bytes_per_sec = (
            (bytes_now - bytes_prev) / elapsed
        )

        # Normalized network 0-100
        network = min(
            (bytes_per_sec / (1024 * 1024)) * 10,
            100
        )

        # Raw speeds for dashboard display
        upload_speed = round(
            (current.bytes_sent -
             self.last_sent) / elapsed / 1024,
            2
        )
        download_speed = round(
            (current.bytes_recv -
             self.last_recv) / elapsed / 1024,
            2
        )

        self.prev_net  = current
        self.prev_time = current_time
        self.last_sent = current.bytes_sent
        self.last_recv = current.bytes_recv
        self.last_time = current_time

        # Top 5 processes
        top_processes = []
        try:
            all_procs = []
            for proc in psutil.process_iter(
                ['name', 'cpu_percent',
                 'memory_percent']
            ):
                try:
                    all_procs.append({
                        "name"   : proc.info['name'],
                        "cpu"    : proc.info[
                            'cpu_percent'
                        ],
                        "memory" : round(
                            proc.info[
                                'memory_percent'
                            ], 2
                        )
                    })
                except:
                    pass

            top_processes = sorted(
                all_procs,
                key=lambda x: x['cpu'],
                reverse=True
            )[:5]
        except:
            top_processes = []

        # Print terminal output
        print("\n==============================")
        print(f"CPU Usage      : {cpu}%")
        print(f"Memory Usage   : {memory}%")
        print(f"Disk Usage     : {disk}%")
        print(f"Network        : {round(network, 2)}%")
        print(f"Upload Speed   : {upload_speed} KB/s")
        print(f"Download Speed : {download_speed} KB/s")
        print(f"Running Procs  : {processes}")

        for p in top_processes:
            print(
                f"{p['name']:<30} | "
                f"CPU {p['cpu']}% | "
                f"MEM {p['memory']}%"
            )

        # Return both formats
        # their format (uppercase)
        # our format (lowercase)
        return {
            # Their format
            "CPU"       : round(cpu, 2),
            "Memory"    : round(memory, 2),
            "Disk"      : round(disk, 2),
            "Network"   : round(network, 2),
            "Processes" : processes,

            # Our format
            "cpu"                : round(cpu, 2),
            "memory"             : round(memory, 2),
            "disk"               : round(disk, 2),
            "network"            : round(network, 2),
            "processes"          : processes,
            "network_sent"       : current.bytes_sent,
            "network_recv"       : current.bytes_recv,
            "network_speed_up"   : upload_speed,
            "network_speed_down" : download_speed,
            "process_count"      : processes,
            "top_processes"      : top_processes
        }