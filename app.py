from flask import Flask, jsonify
import time

app = Flask(__name__)

SHIPYARD = {"lat": 40.752029, "lng": -74.0235}
PATH_STATION = {"lat": 40.735, "lng": -74.027}

trip_start_time = time.time()
trip_duration = 10 * 60        # 10 minutes, in seconds

STALL_START = 4 * 60           # bus gets stuck 4 minutes in
STALL_LENGTH = 5 * 60          # and stays stuck for 5 minutes
LATE_THRESHOLD_MIN = 4         # flag "delayed" at 4+ minutes behind schedule

def get_bus_position():
    elapsed = time.time() - trip_start_time

    if elapsed < STALL_START:
        moving_time = elapsed
    elif elapsed < STALL_START + STALL_LENGTH:
        moving_time = STALL_START
    else:
        moving_time = elapsed - STALL_LENGTH

    percent = moving_time / trip_duration
    percent = min(1.0, percent)

    current_lat = SHIPYARD["lat"] + (PATH_STATION["lat"] - SHIPYARD["lat"]) * percent
    current_lng = SHIPYARD["lng"] + (PATH_STATION["lng"] - SHIPYARD["lng"]) * percent

    expected_percent = elapsed / trip_duration
    actual_percent = percent_from_gps(current_lat)
    minutes_late = (expected_percent - actual_percent) * trip_duration / 60

    if percent >= 1.0:
        status = "arrived"
    elif minutes_late >= LATE_THRESHOLD_MIN:
        status = "delayed"
    else:
        status = "on_time"

    return {"lat": current_lat, "lng": current_lng, "percent": percent, "status": status}

def percent_from_gps(current_lat):
    percent = (current_lat - SHIPYARD["lat"]) / (PATH_STATION["lat"] - SHIPYARD["lat"])
    percent = max(0.0, min(1.0, percent))
    return percent

@app.route("/")
def home():
    return "Shuttle tracker backend is running"

@app.route("/api/bus-location")
def bus_location():
    data = get_bus_position()
    return jsonify(data)

@app.route("/map")
def map_page():
    return app.send_static_file("map.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)