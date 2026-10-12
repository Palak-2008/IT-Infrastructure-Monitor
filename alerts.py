
def generate_alerts(system, network):
    """
    Generate severity-based alerts for system and network health.

    Severity levels:
    HEALTHY  - No threshold violations
    WARNING  - Resource usage is elevated
    CRITICAL - Resource usage is dangerously high
    """

    alerts = []

    # CPU usage thresholds
    cpu = float(system.get("cpu_percent", 0))

    if cpu >= 90:
        alerts.append(
            f"CRITICAL: CPU usage is very high at {cpu}%."
        )
    elif cpu >= 80:
        alerts.append(
            f"WARNING: CPU usage is elevated at {cpu}%."
        )

    # Memory usage thresholds
    memory = float(system.get("memory_percent", 0))

    if memory >= 95:
        alerts.append(
            f"CRITICAL: Memory usage is very high at {memory}%."
        )
    elif memory >= 85:
        alerts.append(
            f"WARNING: Memory usage is elevated at {memory}%."
        )

    # Disk usage thresholds
    disk = float(system.get("disk_percent", 0))

    if disk >= 95:
        alerts.append(
            f"CRITICAL: Disk usage is very high at {disk}%."
        )
    elif disk >= 90:
        alerts.append(
            f"WARNING: Disk usage is elevated at {disk}%."
        )

    # DNS availability
    if network.get("dns_status") != "Success":
        alerts.append(
            "CRITICAL: DNS resolution failed."
        )

    # Network connectivity
    if network.get("ping_status") != "Reachable":
        alerts.append(
            "WARNING: The target host did not respond to ping."
        )

    # Healthy status
    if not alerts:
        alerts.append(
            "HEALTHY: No threshold violations detected."
        )

    return alerts
