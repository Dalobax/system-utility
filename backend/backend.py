from flask import Flask, request, jsonify, send_file
import sqlite3
import time
import csv
from io import StringIO

app = Flask(__name__)
DB_FILE = "system_status.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_id TEXT,
            timestamp REAL,
            disk_encryption TEXT,
            os_update_current TEXT,
            os_update_latest TEXT,
            antivirus TEXT,
            inactivity_sleep INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/report', methods=['POST'])
def report():
    data = request.get_json()
    machine_id = data.get("machine_id")
    state = data.get("state")
    timestamp = data.get("timestamp", time.time())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO system_reports (
            machine_id, timestamp, disk_encryption,
            os_update_current, os_update_latest,
            antivirus, inactivity_sleep
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        machine_id, timestamp,
        state.get("disk_encryption"),
        state.get("os_update", {}).get("current"),
        state.get("os_update", {}).get("latest"),
        state.get("antivirus"),
        state.get("inactivity_sleep")
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/machines', methods=['GET'])
def list_machines():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT machine_id, MAX(timestamp) as latest
        FROM system_reports
        GROUP BY machine_id
    ''')
    machines = [{"machine_id": row[0], "latest_timestamp": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(machines)

@app.route('/api/status/<machine_id>', methods=['GET'])
def get_latest_status(machine_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM system_reports
        WHERE machine_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (machine_id,))
    row = c.fetchone()
    conn.close()
    if row:
        keys = ["id", "machine_id", "timestamp", "disk_encryption",
                "os_update_current", "os_update_latest",
                "antivirus", "inactivity_sleep"]
        return jsonify(dict(zip(keys, row)))
    return jsonify({"error": "Machine not found"}), 404

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM system_reports')
    rows = c.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "machine_id", "timestamp", "disk_encryption",
                     "os_update_current", "os_update_latest",
                     "antivirus", "inactivity_sleep"])
    writer.writerows(rows)

    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="system_reports.csv"
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
