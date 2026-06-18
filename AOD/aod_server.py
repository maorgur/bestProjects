import os
from dotenv import load_dotenv

load_dotenv()

import flask
import time
import httpx
import os
from geopy import distance 
import numpy as np
import unicodedata
import json



from werkzeug.middleware.proxy_fix import ProxyFix
app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

USER_AGENT = "Plane display"
httpx_headers = {"User-Agent": USER_AGENT}

CURRENT_LOCATION = {"lat": float(os.getenv("LATITUDE", 0.0)), "lon": float(os.getenv("LONGITUDE", 0.0)), "elev": int(os.getenv("ELEVATION", 0))}

AIRCRAFT_DB = "/path/to/aircraft.json"
aircraft_info = {}
try:
    with open(AIRCRAFT_DB, "r") as f:
        aircraft_info = json.load(f)
except FileNotFoundError:
    print("Aircraft database not found, the db will be empty")

def get_distance(lat1, lon1, lat2, lon2) -> float:
    '''calculate the distance between two points in kilometers'''
    return distance.distance([lat1, lon1], [lat2, lon2]).km

def get_direction(lat1, lon1, lat2, lon2) -> float:
    '''finds the direction from point 1 to point 2 in degrees (0-360)'''
    delta_lon = np.radians(lon2 - lon1)
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    x = np.sin(delta_lon) * np.cos(lat2)
    y = np.cos(lat1) * np.sin(lat2) - (np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon))

    initial_bearing = np.arctan2(x, y)
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def direction_to_letters(bearing) -> str:
    """
    Convert a bearing (in degrees) to a compass direction with 3-letter accuracy (e.g., N, SSW, ENE).
    """
    if bearing is None:
        return None
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    idx = int((bearing + 11.25) // 22.5) % 16
    return directions[idx]


def rssi_to_quality(rssi) -> int:
    """Convert RSSI value to signal quality percentage.
    """
    if rssi >= 0:
        return 100
    if rssi <= -45:
        return 0
    return int((rssi + 45) / 45 * 100)

def feet_to_meters(feet) -> float:
    if feet == None:
        return None
    return feet * 0.3048


@app.route("/timestamp", methods=["GET"])
def get_timestamp():
    return str(int(time.time()))

MAX_DISTANCE_KM = 50 #if a plane is too far don't show cuz it's not interesting
AIRCRAFT_URL = os.getenv("AIRCRAFT_URL", "http://localhost/data")

priority_planes = {"C5M": 0, "U2": 0, "F35": 0, "F15": 0, "F16": 0,"EUFI": 1, "B52": 0, "B2": 0, "B1": 0, "R135": 1, "K35R": 2, "E3TF": 1, "E3CF": 1, "P8": 1, "C130": 1, "C17": 1, "B703": 1}

@app.route("/aircraft", methods=["GET"])
def get_closest_aircraft():
    with httpx.Client(verify=False, headers=httpx_headers) as client:
        response = client.get(AIRCRAFT_URL, headers=httpx_headers)
        if response.status_code != 200:
            return f"tar1090 responded with {response.status_code}", 500
        data = response.json()["aircraft"]
        if not data:
            return "No aircraft found", 404

    closest_distance = float("inf")
    closest_message = None

    best_priority_level = None
    best_priority_distance = float("inf")
    best_priority_message = None

    for aircraft in data:
        # get all of the data possible, and cut if critical data missing
        lat = aircraft.get("lat", None)
        lon = aircraft.get("lon", None)
        if lat is None or lon is None:
            continue

        distance_km = get_distance(CURRENT_LOCATION["lat"], CURRENT_LOCATION["lon"], lat, lon)
        if distance_km > MAX_DISTANCE_KM:
            continue

        elevation = aircraft.get("alt_geom", aircraft.get("alt_baro", 0))
        elevation = feet_to_meters(elevation) if isinstance(elevation, int) else 0  # elevation can be "ground"
        if elevation < 500:
            continue  # planes that are on ground are boring

        category = aircraft.get("category", None)
        if category and category.startswith("C"):
            continue  # ignore surface vehicles

        formatted_distance = f"{distance_km:.2f}KM"
        plane_hex = aircraft.get("hex", None)
        plane_hex = plane_hex.upper() if plane_hex else "No ICAO"
        flight = aircraft.get("flight", "").strip()  # sometimes its something like "    "

        # Prefer your DB mapping, but fall back to the tar1090 type code if available
        plane_type = aircraft_info.get(plane_hex, None)
        plane_type = plane_type.strip().upper() if isinstance(plane_type, str) else None

        formatted_plane_data = plane_type if plane_type else (flight if flight else (category if category else plane_hex))
        direction = direction_to_letters(get_direction(CURRENT_LOCATION["lat"], CURRENT_LOCATION["lon"], lat, lon))

        message = f"{formatted_plane_data}, {elevation:.0f}m\n{direction}, {formatted_distance}"
        message += f"\n{plane_type}" if plane_type else "\n"  # for buzzer thingy, it needs to know plane type

        # Track closest valid plane (always)
        if distance_km < closest_distance:
            closest_distance = distance_km
            closest_message = message

        # Track best priority plane (level 0 > 1 > 2), break ties by distance
        if plane_type in priority_planes:
            level = priority_planes.get(plane_type)
            if isinstance(level, int) and level in (0, 1, 2):
                if (
                    best_priority_level is None
                    or level < best_priority_level
                    or (level == best_priority_level and distance_km < best_priority_distance)
                ):
                    best_priority_level = level
                    best_priority_distance = distance_km
                    best_priority_message = message

    if closest_message is None:
        return "No aircraft found", 404

    # Only override with a priority plane if there are no valid planes within 5km of us
    if closest_distance > 5 and best_priority_message is not None:
        return best_priority_message, 200

    return closest_message, 200

WEBSITE_URL = os.getenv("WEBSITE_URL", "http://example.com")
TEST_URL = os.getenv("TEST_URL", "http://example.com")
MIN_TIME_BETWEEN_UPDATES = 300 #5 minutes

website_status = True
internet_status = True
last_update_timestamp = 0
@app.route("/availability", methods=["GET"])
def get_availability():
    global last_update_timestamp, website_status, internet_status, MIN_TIME_BETWEEN_UPDATES
    everything_fine = True
    message = "SERVER:ON "

    storage_connected = os.path.exists("/path/to/storage")
    if storage_connected:
        message += "SSD:ON"
    else:
        message += "SSD:OFF"
        everything_fine = False
    message += "\n"
    
    #to not raise ratelimits and stuff, check periodically
    if time.time() - last_update_timestamp > MIN_TIME_BETWEEN_UPDATES: 
        last_update_timestamp = time.time()
        with httpx.Client(verify=False, headers=httpx_headers) as client:
            try:
                response = client.get(TEST_URL, headers=httpx_headers, timeout=2)
                internet_status = True
            except httpx.RequestError as e:
                internet_status = False
                print(f"Internet access check failed: {e}")

            if internet_status:
                try:
                    response = client.get(WEBSITE_URL, headers=httpx_headers, timeout=2)
                    if response.status_code//100 < 4: #2XX or 3XX
                        website_status = True
                    else:
                        website_status = False
                        everything_fine = False
                        print(f"Website access check failed: Status code {response.status_code}")
                except httpx.RequestError as e:
                    website_status = False
                    everything_fine = False
                    print(f"Website access check failed: {e}")
            else:
                website_status = False
                everything_fine = False

    if internet_status:
        message += "INET:ON"
    else:
        message += "INET:OFF"

    if internet_status:
        if website_status:
            message += " WEB:ON"
        else:
            message += " WEB:OFF"

    status_code = 200 if everything_fine else 503
    return message, status_code



SPECIAL_MAP = {
    'Ø': 'O',
    'ø': 'o',
    'Æ': 'AE',
    'æ': 'ae',
    'Þ': 'Th',
    'þ': 'th',
    'ß': 'ss',
}
def normalize_text(text):
    normalized = ""
    for char in text:
        if char in SPECIAL_MAP:
            normalized += SPECIAL_MAP[char]
        else:
            normalized += char
    return "".join(c for c in unicodedata.normalize('NFD', normalized) if not unicodedata.combining(c))

POST_SECRET = int(os.getenv("SECRET_KEY", 0))
artist = None
title = None
last_media_timestamp = 0

@app.route("/post/media", methods=["POST"])
def receive_media_info():
    global artist, title, last_media_timestamp

    data = flask.request.get_json()
    secret = data.get("secret", None)
    if secret != POST_SECRET:
        return "Not found", 404 #to not reveal that the endpoint exists
    
    artist = data.get("artist", None)
    title = data.get("title", None)
    last_media_timestamp = time.time()
    print(f"Received media info: {artist} - {title}")
    return "OK", 200

@app.route("/post/media", methods=["GET"])
def fake_receive_media_info():
    return "Not found", 404 #to not reveal that the endpoint exists

@app.route("/media", methods=["GET"])
def get_media_info():
    global artist, title, last_media_timestamp

    if time.time() - last_media_timestamp > 600: #if it's been more than 10 minutes since we got media info, consider it expired
        artist = None
        title = None

    if not artist and not title:
        return "No media info received yet", 404
    elif not artist:
        artist = "Unknown Artist"
    elif not title:
        title = "Unknown Title"
    
    message = ""
    if title:
        message += normalize_text(title)
    message += "\n"
    if artist:
        message += normalize_text(artist)


    return message, 200

#if this test is set to something, the device will show it and will check in a loop if it got updated
TEST_FILE = "/path/to/test.txt"
@app.route("/test", methods=["GET"])
def get_test_text():
    try:
        with open(TEST_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return content, 200
            else:
                return "Test file is empty", 404
    except FileNotFoundError:
        return "Test file not found", 404
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
