import requests
from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import os
import traceback

app = Flask(__name__)

# --- Config ---
API_URL = (
    "https://api.ecowitt.net/api/v3/device/real_time?"
    "application_key=759C4F506AB26D40A6428181584B4CB8"
    "&api_key=a77111f4-470b-4117-909f-019759cfe839"
    "&mac=3C:8A:1F:34:FD:33"
    "&call_back=all"
)

DB_CONFIG = {
    'host':               '185.182.158.65',
    'port':               3306,
    'user':               'upzmysql',
    'password':           'Y2Q64YoK8Szwj07KVcGn',
    'database':           'UPzMysql',
    'connection_timeout': 10,
    'use_pure':           True       # ← force pure‑Python driver
}
# --- Data Fetch Function ---
def fetch_ecowitt_data():
    print("Fetching data from Ecowitt API...")
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    result = response.json()

    if result.get('code') != 0:
        raise ValueError("Invalid response from Ecowitt API")

    data = result.get('data', {})

    def safe_get(path, default=0.0):
        current = data
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        try:
            return float(current)
        except (TypeError, ValueError):
            return default

    record = {
        'indoor_temperature': safe_get(['indoor', 'temperature', 'value']),
        'indoor_humidity': safe_get(['indoor', 'humidity', 'value']),
        'pressure_relative': safe_get(['pressure', 'relative', 'value']),
        'pressure_absolute': safe_get(['pressure', 'absolute', 'value']),
    }

    print("Data fetched:", record)
    return record

def insert_to_mysql(record):
    conn = None
    cursor = None
    try:
        print("🔌 Attempting DB connection...")
        print(DB_CONFIG, " nedim nedim")
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected!")

        cursor = conn.cursor()
        insert_query = """
            INSERT INTO Ecowitt_data (indoor_temperature, indoor_humidity, pressure_relative, pressure_absolute)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            record['indoor_temperature'],
            record['indoor_humidity'],
            record['pressure_relative'],
            record['pressure_absolute']
        ))
        conn.commit()
        print("✅ Data inserted successfully.")

    except Exception as e:
        print("❌ Exception caught:", str(e))
        traceback.print_exc()

    # finally:
    #     try:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()
    #             print("🔒 MySQL connection closed.")
    #     except Exception as close_err:
    #         print("⚠️ Error during cleanup:", str(close_err))



# --- Flask Route ---
@app.route('/fetch-ecowitt', methods=['GET'])
def fetch_and_save():
    try:
        print("\n--- Starting fetch-and-save operation ---")
        data = fetch_ecowitt_data()
        print(data)
        insert_to_mysql(data)
        print("\n--- Data saved ---")
        # Optional: print into browser-friendly HTML
        html = "<h2>✅ Data fetched and saved:</h2><ul>"
        for key, value in data.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"

        return html, 200

    except Exception as e:
        print("❌ Error in fetch-and-save:", str(e))
        return f"<h2>❌ Error:</h2><pre>{str(e)}</pre>", 500

@app.route('/', methods=['GET'])
def test():
    try:
        print("\n--- Fetching data from Ecowitt API ---")
        data = fetch_ecowitt_data()

        print("\n--- Data saved ---")
        # Format as HTML to show in the browser
        html = "<h2>🌡️ Ecowitt Sensor Data</h2><ul>"
        for key, value in data.items():
            html += f"<li><strong>{key.replace('_',.0, ' ').title()}:</strong> {value}</li>" 
        html += "</ul>"

        return html, 200

    except Exception as e:
        print("❌ Error fetching data:", str(e))
        return f"<h2>❌ Error:</h2><pre>{str(e)}</pre>", 500

# --- Start Flask ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port)
