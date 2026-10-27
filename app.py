from flask import Flask, jsonify, request
import math
import time

app = Flask(__name__)

# The route in driving order, one (latitude, longitude) pair per corner
ROUTE = [
    (40.751586, -74.024239),    # Shuttle pickup, in front of North Independence
    (40.751474, -74.023686),    # Independence Ct and Sinatra Dr N
    (40.749437, -74.023980),    # Sinatra Dr N and 11th St
    (40.749752, -74.025992),    # 11th St and Hudson St
    (40.736470, -74.030193),    # PATH stop, 78 Hudson St
]

trip_start_time = time.time()
demo_speed = 1                 # 1 = real time, 5 = five times faster
trip_duration = 10 * 60        # 10 minutes, in seconds

STALL_START = 4 * 60           # bus gets stuck 4 minutes in
STALL_LENGTH = 5 * 60          # and stays stuck for 5 minutes
LATE_THRESHOLD_MIN = 4         # flag "delayed" at 4+ minutes behind schedule

def segment_length(a, b):
    """Distance in meters between two (lat, lng) points."""
    mid_lat = math.radians((a[0] + b[0]) / 2)
    dy = (b[0] - a[0]) * 111000
    dx = (b[1] - a[1]) * 111000 * math.cos(mid_lat)
    return math.hypot(dx, dy)

SEGMENT_LENGTHS = []
for i in range(len(ROUTE) - 1):
    SEGMENT_LENGTHS.append(segment_length(ROUTE[i], ROUTE[i + 1]))
TOTAL_LENGTH = sum(SEGMENT_LENGTHS)

def position_on_route(percent):
    distance_left = percent * TOTAL_LENGTH
    for i in range(len(SEGMENT_LENGTHS)):
        if distance_left <= SEGMENT_LENGTHS[i]:
            fraction = distance_left / SEGMENT_LENGTHS[i]
            start = ROUTE[i]
            end = ROUTE[i + 1]
            lat = start[0] + (end[0] - start[0]) * fraction
            lng = start[1] + (end[1] - start[1]) * fraction
            return lat, lng
        distance_left -= SEGMENT_LENGTHS[i]
    return ROUTE[-1]

def get_bus_position():
    elapsed = (time.time() - trip_start_time) * demo_speed

    if elapsed < STALL_START:
        moving_time = elapsed
    elif elapsed < STALL_START + STALL_LENGTH:
        moving_time = STALL_START
    else:
        moving_time = elapsed - STALL_LENGTH

    percent = moving_time / trip_duration
    percent = min(1.0, percent)

    current_lat, current_lng = position_on_route(percent)

    # The simulation knows the bus's percent directly. With a real tracker,
    # this will have to be worked out from the GPS coordinates.
    expected_percent = elapsed / trip_duration
    minutes_late = (expected_percent - percent) * trip_duration / 60

    if percent >= 1.0:
        status = "arrived"
    elif minutes_late >= LATE_THRESHOLD_MIN:
        status = "delayed"
    else:
        status = "on_time"

    return {"lat": current_lat, "lng": current_lng, "percent": percent, "status": status}

@app.route("/")
def home():
    return "Shuttle tracker backend is running"

@app.route("/api/bus-location")
def bus_location():
    data = get_bus_position()
    return jsonify(data)

@app.route("/api/route")
def route():
    return jsonify(ROUTE)

@app.route("/api/restart", methods=["POST"])
def restart():
    global trip_start_time, demo_speed
    speed = request.args.get("speed", 1, type=int)
    demo_speed = speed if speed in (1, 5, 10) else 1
    trip_start_time = time.time()
    return jsonify({"speed": demo_speed})

@app.route("/map")
def map_page():
    return app.send_static_file("map.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)