
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("monitoring.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                computer TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                host TEXT,
                dns_status TEXT,
                ping_status TEXT,
                alerts TEXT
            )
        """)


def save_snapshot(system, network, alerts):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO monitoring_history (
                timestamp, computer, cpu_percent,
                memory_percent, disk_percent, host,
                dns_status, ping_status, alerts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system["timestamp"],
            system["computer"],
            system["cpu_percent"],
            system["memory_percent"],
            system["disk_percent"],
            network["host"],
            network["dns_status"],
            network["ping_status"],
            str(alerts)
        ))


def get_recent_history(limit=10):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM monitoring_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print("Database exists:", DB_PATH.exists())
    print("Database path:", DB_PATH)

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("monitoring.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                computer TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                host TEXT,
                dns_status TEXT,
                ping_status TEXT,
                alerts TEXT
            )
        """)


def save_snapshot(system, network, alerts):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO monitoring_history (
                timestamp, computer, cpu_percent,
                memory_percent, disk_percent, host,
                dns_status, ping_status, alerts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system["timestamp"],
            system["computer"],
            system["cpu_percent"],
            system["memory_percent"],
            system["disk_percent"],
            network["host"],
            network["dns_status"],
            network["ping_status"],
            str(alerts)
        ))


def get_recent_history(limit=10):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM monitoring_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print("Database exists:", DB_PATH.exists())
    print("Database path:", DB_PATH)

