from flask import Flask, jsonify
import time

app = Flask(__name__)

SHIPYARD = {"lat": 40.752029, "lng": -74.0235}
PATH_STATION = {"lat": 40.735, "lng": -74.027}

trip_start_time = time.time()
trip_duration = 600

def get_bus_position():
    elapsed = time.time() - trip_start_time
    percent = elapsed / trip_duration
    percent = min(1.0, percent)

    current_lat = SHIPYARD["lat"] + (PATH_STATION["lat"] - SHIPYARD["lat"]) * percent
    current_lng = SHIPYARD["lng"] + (PATH_STATION["lng"] - SHIPYARD["lng"]) * percent

    return {"lat": current_lat, "lng": current_lng, "percent": percent}

@app.route("/")
def home():
    return "Shuttle tracker backend is running"

@app.route("/api/bus-location")
def bus_location():
    data = get_bus_position()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)