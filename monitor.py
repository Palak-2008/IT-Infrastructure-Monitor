
import platform
import psutil
from datetime import datetime


def get_system_health():
    # Collect system information
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")

    health = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "computer": platform.node(),
        "operating_system": platform.system(),
        "os_version": platform.release(),
        "cpu_percent": cpu_usage,
        "memory_percent": memory.percent,
        "memory_available_gb": round(
            memory.available / (1024 ** 3), 2
        ),
        "disk_percent": disk.percent,
        "disk_free_gb": round(
            disk.free / (1024 ** 3), 2
        ),
    }

    return health


if __name__ == "__main__":
    results = get_system_health()

    print("\n===== IT INFRASTRUCTURE HEALTH REPORT =====")
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
