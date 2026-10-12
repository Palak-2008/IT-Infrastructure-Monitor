
from flask import Flask, render_template_string, Response
import csv
import io
import ast
import re

from monitor import get_system_health
from network_check import check_network
from alerts import generate_alerts
from database import init_db, save_snapshot, get_recent_history
from service_check import check_tcp_service


app = Flask(__name__)
init_db()


def format_alerts(value):
    """Display saved alerts without Python list brackets or quotes."""
    if value is None or value == "":
        return "No alerts"

    if isinstance(value, list):
        items = value
    else:
        text = str(value).strip()

        try:
            parsed = ast.literal_eval(text)
            items = parsed if isinstance(parsed, list) else [parsed]
        except (ValueError, SyntaxError):
            # Clean old or unexpectedly formatted database values.
            text = text.strip("[]")
            text = text.replace("', '", "; ")
            text = text.replace('", "', "; ")
            text = text.strip("'\" ")
            return text or "No alerts"

    # Handle a list containing another list or list-like string.
    cleaned = []
    for item in items:
        if isinstance(item, list):
            cleaned.extend(str(part) for part in item)
        else:
            item_text = str(item).strip()
            if item_text.startswith("[") and item_text.endswith("]"):
                try:
                    nested = ast.literal_eval(item_text)
                    if isinstance(nested, list):
                        cleaned.extend(str(part) for part in nested)
                        continue
                except (ValueError, SyntaxError):
                    pass
            cleaned.append(item_text)

    return "; ".join(cleaned) if cleaned else "No alerts"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IT Infrastructure Monitoring Dashboard</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 25px;
            font-family: Arial, sans-serif;
            background: #0b1f3a;
            color: #ffffff;
        }

        .container {
            width: 100%;
            max-width: 1250px;
            margin: 0 auto;
        }

        header {
            margin-bottom: 25px;
        }

        h1 {
            color: #60a5fa;
            margin-bottom: 8px;
        }

        h2 {
            color: #93c5fd;
            margin-top: 0;
            font-size: 20px;
        }

        .subtitle,
        .label {
            color: #cbd5e1;
        }

        .label {
            font-size: 14px;
        }

        .actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0;
        }

        .button {
            display: inline-block;
            padding: 11px 16px;
            border-radius: 7px;
            background: #2563eb;
            color: #ffffff;
            text-decoration: none;
            font-weight: bold;
        }

        .button:hover {
            background: #1d4ed8;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(
                auto-fit, minmax(250px, 1fr)
            );
            gap: 18px;
        }

        .card {
            background: #132b4f;
            padding: 22px;
            border-radius: 12px;
            border: 1px solid #29476f;
            margin-bottom: 20px;
            min-width: 0;
        }

        .metric {
            font-size: 28px;
            font-weight: bold;
            margin: 12px 0;
        }

        .status {
            color: #86efac;
            font-weight: bold;
        }

        .warning {
            color: #fca5a5;
            font-weight: bold;
        }

        /* Severity-based alerts */
        .alert-item {
            background: #3b1d2a;
            border-left: 4px solid #ef4444;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #fecaca;
        }

        .warning-item {
            background: #422d13;
            border-left: 4px solid #f59e0b;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #fde68a;
        }

        .success-item {
            background: #123a35;
            border-left: 4px solid #22c55e;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #bbf7d0;
        }

        /* Performance charts */
        .chart-container {
            position: relative;
            width: 100%;
            height: 280px;
            margin: 25px 0;
        }

        /* History table */
        .table-wrapper {
            display: block;
            width: 100%;
            max-width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
            overscroll-behavior-x: contain;
        }

        table {
            width: 1400px !important;
            min-width: 1400px !important;
            border-collapse: collapse;
            margin-top: 15px;
            table-layout: fixed;
        }

        thead th {
            color: #93c5fd;
            background: #102442;
            font-weight: bold;
        }

        table th,
        table td {
            text-align: left;
            padding: 14px 12px;
            border-bottom: 1px solid #29476f;
            font-size: 13px;
            vertical-align: middle;

            /* Prevent headings and values from breaking mid-word */
            white-space: nowrap !important;
            word-break: normal !important;
            overflow-wrap: normal !important;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Column widths */
        table th:nth-child(1),
        table td:nth-child(1) {
            width: 175px;
        }

        table th:nth-child(2),
        table td:nth-child(2) {
            width: 150px;
        }

        table th:nth-child(3),
        table td:nth-child(3) {
            width: 100px;
        }

        table th:nth-child(4),
        table td:nth-child(4) {
            width: 120px;
        }

        table th:nth-child(5),
        table td:nth-child(5) {
            width: 100px;
        }

        table th:nth-child(6),
        table td:nth-child(6) {
            width: 140px;
        }

        table th:nth-child(7),
        table td:nth-child(7) {
            width: 120px;
        }

        table th:nth-child(8),
        table td:nth-child(8) {
            width: 130px;
        }

        table th:nth-child(9),
        table td:nth-child(9) {
            width: 365px;
        }

        table td.alert-cell {
            white-space: normal !important;
            word-break: normal !important;
            overflow-wrap: anywhere !important;
            text-overflow: clip;
            line-height: 1.5;
        }

        tbody tr:hover {
            background: #19365c;
        }

        footer {
            text-align: center;
            color: #94a3b8;
            margin-top: 25px;
            font-size: 13px;
        }

        @media (max-width: 600px) {
            body {
                padding: 14px;
            }

            .card {
                padding: 16px;
            }

            .metric {
                font-size: 24px;
            }

            .chart-container {
                height: 230px;
            }
        }
    </style>
</head>

<body>
<div class="container">

    <header>
        <h1>IT Infrastructure Monitoring Dashboard</h1>
        <p class="subtitle">
            Monitor system health, network connectivity,
            service availability and performance trends.
        </p>

        <div class="actions">
            <a class="button" href="/">Refresh Monitoring</a>
            <a class="button" href="/export">Download CSV Report</a>
        </div>
    </header>

    <!-- System overview -->
    <div class="grid">

        <div class="card">
            <h2>System Health</h2>

            <p class="label">Computer</p>
            <p>{{ system.computer }}</p>

            <p class="label">Operating System</p>
            <p>{{ system.os }}</p>

            <p class="label">CPU Usage</p>
            <div class="metric">{{ system.cpu_percent }}%</div>

            <p class="label">Memory Usage</p>
            <div class="metric">{{ system.memory_percent }}%</div>

            <p class="label">Available Memory</p>
            <p>{{ system.memory_available_gb }} GB</p>

            <p class="label">Disk Usage (C:)</p>
            <div class="metric">{{ system.disk_percent }}%</div>

            <p class="label">Free Disk Space</p>
            <p>{{ system.disk_free_gb }} GB</p>
        </div>

        <div class="card">
            <h2>Network Diagnostics</h2>

            <p class="label">Target Host</p>
            <p>{{ network.host }}</p>

            <p class="label">Resolved IP Address</p>
            <p>{{ network.ip_address or "Unavailable" }}</p>

            <p class="label">DNS Status</p>
            <p class="{% if network.dns_status == 'Success' %}
                status{% else %}warning{% endif %}">
                {{ network.dns_status }}
            </p>

            <p class="label">Ping Status</p>
            <p class="{% if network.ping_status == 'Reachable' %}
                status{% else %}warning{% endif %}">
                {{ network.ping_status }}
            </p>

            <p class="label">Details</p>
            <p>{{ network.response }}</p>
        </div>

        <div class="card">
            <h2>HTTPS Service Check</h2>

            <p class="label">Service</p>
            <p>Google HTTPS</p>

            <p class="label">Host and Port</p>
            <p>google.com:443</p>

            <p class="label">Connection Status</p>
            <p class="{% if service.status == 'Reachable' %}
                status{% else %}warning{% endif %}">
                {{ service.status }}
            </p>

            <p class="label">Details</p>
            <p>{{ service.message }}</p>
        </div>

    </div>

    <!-- Performance charts -->
    <div class="card">
        <h2>System Performance Trends</h2>
        <p class="label">
            Historical CPU, memory and disk usage from recent snapshots.
        </p>

        {% if history %}
            <div class="chart-container">
                <canvas id="cpuChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="memoryChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="diskChart"></canvas>
            </div>
        {% else %}
            <p>No history available to display charts yet.</p>
        {% endif %}
    </div>

    <!-- Current alerts -->
    <div class="card">
        <h2>System Alerts</h2>

        {% if alerts %}
            {% for alert in alerts %}
                {% if alert.startswith("CRITICAL:") %}
                    <div class="alert-item">{{ alert }}</div>
                {% elif alert.startswith("WARNING:") %}
                    <div class="warning-item">{{ alert }}</div>
                {% else %}
                    <div class="success-item">{{ alert }}</div>
                {% endif %}
            {% endfor %}
        {% else %}
            <div class="success-item">No alerts detected.</div>
        {% endif %}
    </div>

    <!-- Monitoring history -->
    <div class="card">
        <h2>Recent Monitoring History</h2>

        {% if history %}
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Computer</th>
                            <th>CPU (%)</th>
                            <th>Memory (%)</th>
                            <th>Disk (%)</th>
                            <th>Host</th>
                            <th>DNS Status</th>
                            <th>Ping Status</th>
                            <th>Alerts</th>
                        </tr>
                    </thead>

                    <tbody>
                        {% for row in history %}
                        <tr>
                            <td>{{ row.timestamp }}</td>
                            <td>{{ row.computer }}</td>
                            <td>{{ row.cpu_percent }}</td>
                            <td>{{ row.memory_percent }}</td>
                            <td>{{ row.disk_percent }}</td>
                            <td>{{ row.host }}</td>
                            <td>{{ row.dns_status }}</td>
                            <td>{{ row.ping_status }}</td>
                            <td class="alert-cell">{{ format_alerts(row.alerts) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p>No monitoring history available yet.</p>
        {% endif %}
    </div>

    <footer>
        IT Infrastructure Monitoring Project |
        Python | Flask | SQLite | Chart.js
    </footer>

</div>

<script>
    const historyData = {{ history | tojson }};
    const chronologicalData = [...historyData].reverse();
    const labels = chronologicalData.map(row => row.timestamp);

    function createUsageChart(canvasId, label, field) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const values = chronologicalData.map(
            row => Number(row[field])
        );

        new Chart(canvas, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: label + " (%)",
                    data: values,
                    borderColor: "#60a5fa",
                    backgroundColor: "rgba(96, 165, 250, 0.15)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: "index"
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0,
                        max: 100,
                        ticks: { color: "#cbd5e1" },
                        grid: { color: "#29476f" }
                    },
                    x: {
                        ticks: {
                            color: "#cbd5e1",
                            maxRotation: 45,
                            autoSkip: true
                        },
                        grid: { color: "#29476f" }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: "#ffffff" }
                    }
                }
            }
        });
    }

    if (historyData.length > 0) {
        createUsageChart("cpuChart", "CPU Usage", "cpu_percent");
        createUsageChart(
            "memoryChart", "Memory Usage", "memory_percent"
        );
        createUsageChart("diskChart", "Disk Usage", "disk_percent");
    }
</script>

</body>
</html>
"""


@app.route("/")
def dashboard():
    system = get_system_health()
    network = check_network()

    service_result = check_tcp_service("google.com", 443)

    if isinstance(service_result, dict):
        service_status = service_result.get(
            "status",
            service_result.get("ping_status", "Unknown")
        )
        service_message = service_result.get(
            "message",
            service_result.get("response", str(service_result))
        )
    else:
        service_status = (
            "Reachable" if service_result else "Unreachable"
        )
        service_message = str(service_result)

    service = {
        "status": service_status,
        "message": service_message
    }

    alerts = generate_alerts(system, network)

    save_snapshot(system, network, alerts)
    history = get_recent_history(10)

    return render_template_string(
        HTML_TEMPLATE,
        system=system,
        network=network,
        service=service,
        alerts=alerts,
        history=history,
        format_alerts=format_alerts
    )


@app.route("/export")
def export_csv():
    history = get_recent_history(1000)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Timestamp",
        "Computer",
        "CPU Usage (%)",
        "Memory Usage (%)",
        "Disk Usage (%)",
        "Host",
        "DNS Status",
        "Ping Status",
        "Alerts"
    ])

    for row in history:
        writer.writerow([
            row.get("timestamp", ""),
            row.get("computer", ""),
            row.get("cpu_percent", ""),
            row.get("memory_percent", ""),
            row.get("disk_percent", ""),
            row.get("host", ""),
            row.get("dns_status", ""),
            row.get("ping_status", ""),
            format_alerts(row.get("alerts", ""))
        ])

    response = Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8"
    )
    response.headers["Content-Disposition"] = (
        "attachment; filename=monitoring_report.csv"
    )

    return response


if __name__ == "__main__":
    app.run(debug=False)
