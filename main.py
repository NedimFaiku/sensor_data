from flask import Flask, request
import csv
import os

app = Flask(__name__)
CSV_FILE = 'weather_data.csv'

# Create CSV file and write header if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['temperature_F', 'humidity', 'pressure_inHg', 'wind_dir', 'wind_speed_mph', 'solar_radiation', 'uv_index'])

@app.route('/ecowitt', methods=['GET'])  # changed from POST to GET
def receive_data():
    data = request.args.to_dict()  # changed from request.form to request.args

    # Extract relevant fields
    row = [
        data.get('tempf'),
        data.get('humidity'),
        data.get('baromrelin'),
        data.get('winddir'),
        data.get('windspeedmph'),
        data.get('solarradiation'),
        data.get('uv')
    ]

    # Append data to CSV file
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
