import psutil
import time

# Store previous network values
_previous = psutil.net_io_counters()
_previous_time = time.time()


def get_system_metrics():
    global _previous, _previous_time

    # CPU (%)
    cpu = psutil.cpu_percent(interval=0.2)

    # Memory (%)
    memory = psutil.virtual_memory().percent

    # Disk Usage (%)
    disk = psutil.disk_usage("/").percent

    # Process Count
    processes = len(psutil.pids())

    # ---------- Network Usage ----------
    current = psutil.net_io_counters()
    current_time = time.time()

    bytes_now = current.bytes_sent + current.bytes_recv
    bytes_prev = _previous.bytes_sent + _previous.bytes_recv

    bytes_per_sec = (bytes_now - bytes_prev) / max(
        current_time - _previous_time,
        0.1
    )

    # Normalize between 0 and 100
    network = min((bytes_per_sec / (1024 * 1024)) * 10, 100)

    _previous = current
    _previous_time = current_time

    return {
        "CPU": round(cpu, 2),
        "Memory": round(memory, 2),
        "Disk": round(disk, 2),
        "Network": round(network, 2),
        "Processes": processes
    }


if __name__ == "__main__":
    while True:
        print(get_system_metrics())
        time.sleep(2)