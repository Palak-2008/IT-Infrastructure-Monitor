
import socket
from datetime import datetime


def check_tcp_service(host, port, timeout=3):
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host": host,
        "port": port,
        "status": "Unknown",
        "message": ""
    }

    try:
        with socket.create_connection(
            (host, port), timeout=timeout
        ):
            result["status"] = "Open"
            result["message"] = "TCP connection successful"

    except (socket.timeout, TimeoutError):
        result["status"] = "No response"
        result["message"] = "Connection timed out"

    except ConnectionRefusedError:
        result["status"] = "Closed"
        result["message"] = "Connection refused"

    except OSError as error:
        result["status"] = "Error"
        result["message"] = str(error)

    return result


if __name__ == "__main__":
    # Test a standard HTTPS service.
    result = check_tcp_service("google.com", 443)

    print("\n===== TCP SERVICE CHECK =====")
    for key, value in result.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
