
import socket
import subprocess
import platform
from datetime import datetime


def check_network(host="google.com"):
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host": host,
        "dns_status": "Failed",
        "ip_address": "Unavailable",
        "ping_status": "Not tested",
        "response": "Unavailable"
    }

    # Check DNS resolution
    try:
        ip_address = socket.gethostbyname(host)
        result["dns_status"] = "Success"
        result["ip_address"] = ip_address
    except socket.gaierror:
        result["dns_status"] = "Failed"
        return result

    # Check reachability using the system ping command
    flag = "-n" if platform.system() == "Windows" else "-c"

    try:
        completed = subprocess.run(
            ["ping", flag, "1", host],
            capture_output=True,
            text=True,
            timeout=5
        )

        if completed.returncode == 0:
            result["ping_status"] = "Reachable"
            result["response"] = "Ping reply received"
        else:
            result["ping_status"] = "No reply"
            result["response"] = "Host may be unreachable"
    except (subprocess.TimeoutExpired, OSError):
        result["ping_status"] = "Error"
        result["response"] = "Ping command failed or timed out"

    return result


if __name__ == "__main__":
    report = check_network()

    print("\n===== NETWORK DIAGNOSTICS REPORT =====")
    for key, value in report.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
