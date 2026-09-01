import requests
import random
import time
from datetime import datetime

# =========================================================
# BACKEND
# =========================================================
BACKEND_URL = "https://resqnet1-backend.vercel.app/api/sensor-data"


# =========================================================
# INITIAL NODE DATA
# =========================================================

nodes = {

    "N1": {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "battery": 92,
        "water_level": 65,
        "temperature": 31.0,
        "rssi": -70
    },

    "N2": {
        "latitude": 13.0848,
        "longitude": 80.2735,
        "battery": 70,
        "water_level": 45,
        "temperature": 30.5,
        "rssi": -82
    },

    "N3": {
        "latitude": 13.0795,
        "longitude": 80.2675,
        "battery": 98,
        "water_level": 25,
        "temperature": 29.8,
        "rssi": -65
    }
}


# =========================================================
# GENERATE DATA
# =========================================================

def generate_node_data(node_id, node):

    # -----------------------------------------
    # BATTERY
    # -----------------------------------------

    node["battery"] -= random.uniform(0.0, 0.3)

    if node["battery"] < 0:
        node["battery"] = 100

    # -----------------------------------------
    # WATER LEVEL
    # -----------------------------------------

    change = random.uniform(-3, 5)

    node["water_level"] += change

    # Keep realistic range
    node["water_level"] = max(
        0,
        min(100, node["water_level"])
    )

    # -----------------------------------------
    # TEMPERATURE
    # -----------------------------------------

    node["temperature"] += random.uniform(
        -0.4,
        0.4
    )

    node["temperature"] = max(
        20,
        min(45, node["temperature"])
    )

    # -----------------------------------------
    # RSSI
    # -----------------------------------------

    node["rssi"] += random.randint(-2, 2)

    node["rssi"] = max(
        -120,
        min(-40, node["rssi"])
    )

    # -----------------------------------------
    # SOS
    # -----------------------------------------

    # Small probability
    sos = random.random() < 0.01

    # -----------------------------------------
    # DISASTER STATUS
    # -----------------------------------------

    water = node["water_level"]

    if water >= 80:
        disaster = "Flood"
        severity = "CRITICAL"

    elif water >= 50:
        disaster = "Flood"
        severity = "WARNING"

    else:
        disaster = "Safe"
        severity = "SAFE"

    # -----------------------------------------
    # PACKET
    # -----------------------------------------

    packet = {

        "node_id": node_id,

        "latitude": round(
            node["latitude"],
            6
        ),

        "longitude": round(
            node["longitude"],
            6
        ),

        "battery": round(
            node["battery"],
            1
        ),

        "rssi": node["rssi"],

        "water_level": round(
            node["water_level"],
            1
        ),

        "temperature": round(
            node["temperature"],
            1
        ),

        "disaster": disaster,

        "severity": severity,

        "sos": sos,

        "timestamp": datetime.now().isoformat()
    }

    return packet


# =========================================================
# SEND DATA
# =========================================================

def send_data(packet):

    try:

        response = requests.post(
            BACKEND_URL,
            json=packet,
            timeout=5
        )

        print(
            packet["node_id"],
            "→ Backend",
            response.status_code
        )

        print(packet)

    except Exception as e:

        print(
            "ERROR sending data:",
            e
        )


# =========================================================
# MAIN LOOP
# =========================================================

print()
print("==============================")
print("RESQNET SENSOR SIMULATOR")
print("==============================")

# ---------------------------------------------------------
# DEVELOPMENT MODE
# ---------------------------------------------------------

# Use 10 seconds for testing.
# Change to 600 for 10 minutes.

INTERVAL = 10

print()
print("Simulation interval:", INTERVAL, "seconds")
print()

while True:

    print("------------------------------")
    print(
        "Generating sensor data:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    for node_id, node in nodes.items():

        packet = generate_node_data(
            node_id,
            node
        )

        send_data(packet)

    print()
    print(
        "Waiting",
        INTERVAL,
        "seconds..."
    )

    time.sleep(INTERVAL)
