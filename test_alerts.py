
from alerts import generate_alerts


def run_test(test_name, system, network, expected_severity):
    alerts = generate_alerts(system, network)

    print(f"\nTest: {test_name}")
    for alert in alerts:
        print(f"  {alert}")

    if any(
        alert.startswith(expected_severity + ":")
        for alert in alerts
    ):
        print("Result: PASSED")
    else:
        print(f"Result: FAILED - Expected {expected_severity}")


# Normal system conditions
healthy_system = {
    "cpu_percent": 30,
    "memory_percent": 60,
    "disk_percent": 70
}

healthy_network = {
    "dns_status": "Success",
    "ping_status": "Reachable"
}

run_test(
    "Healthy System",
    healthy_system,
    healthy_network,
    "HEALTHY"
)


# Elevated CPU usage
warning_system = {
    "cpu_percent": 82,
    "memory_percent": 60,
    "disk_percent": 70
}

run_test(
    "CPU Warning",
    warning_system,
    healthy_network,
    "WARNING"
)


# Critical CPU usage
critical_system = {
    "cpu_percent": 95,
    "memory_percent": 60,
    "disk_percent": 70
}

run_test(
    "CPU Critical",
    critical_system,
    healthy_network,
    "CRITICAL"
)


# Critical memory usage
critical_memory = {
    "cpu_percent": 30,
    "memory_percent": 97,
    "disk_percent": 70
}

run_test(
    "Memory Critical",
    critical_memory,
    healthy_network,
    "CRITICAL"
)


# Disk warning
disk_warning = {
    "cpu_percent": 30,
    "memory_percent": 60,
    "disk_percent": 92
}

run_test(
    "Disk Warning",
    disk_warning,
    healthy_network,
    "WARNING"
)


# DNS failure
dns_failure = {
    "dns_status": "Failed",
    "ping_status": "Reachable"
}

run_test(
    "DNS Failure",
    healthy_system,
    dns_failure,
    "CRITICAL"
)


# Ping failure
ping_failure = {
    "dns_status": "Success",
    "ping_status": "No reply"
}

run_test(
    "Ping Failure",
    healthy_system,
    ping_failure,
    "WARNING"
)
