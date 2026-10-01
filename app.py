from flask import Flask, jsonify  
app = Flask(__name__)

@app.route("/")
def home ():
    return "Shuttle tracker backend is running"

@app.route("/api/bus-location")
def bus_location():
    data = {
        "lat": 40.752029,
        "lng": -74.0235,
        "status": "on_time"
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)

