from functools import wraps

from flask import Flask, jsonify, request
import requests
from datetime import datetime
import time

app = Flask(__name__)

API_TOKEN = "supersecrettoken123"
GOOGLE_API_KEY = ""


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        # Fallback to URL query parameter
        if not token:
            token = request.args.get("token")

        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated

@app.route('/api/time/<city>', methods=['GET'])
@token_required
def get_time(city):
    if not city:
        return jsonify({"error": "City name is required"}), 400

    # Get coordinates
    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
    geo_response = requests.get(geo_url)
    geo_data = geo_response.json()

    if geo_response.status_code != 200 or not geo_data.get("results"):
        return jsonify({"error": f"Could not find coordinates for city '{city}'"}), 404

    location = geo_data["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]

    # Get timezone
    timestamp = int(time.time())
    tz_url = f"https://maps.googleapis.com/maps/api/timezone/json?location={lat},{lng}&timestamp={timestamp}&key={GOOGLE_API_KEY}"
    tz_response = requests.get(tz_url)
    tz_data = tz_response.json()

    if tz_response.status_code != 200 or tz_data.get("status") != "OK":
        return jsonify({"error": "Failed to retrieve time zone info", "details": tz_data}), 500

    offset_sec = tz_data["rawOffset"] + tz_data["dstOffset"]
    local_time = datetime.utcfromtimestamp(timestamp + offset_sec).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "city": city.title(),
        "local_time": local_time,
        "utc_offset_hours": offset_sec / 3600
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host="34.121.28.86", port=5000, debug=True)
