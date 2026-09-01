from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random

from backend.email_alert import send_critical_alert


app = FastAPI(
    title="ResQNet Backend",
    description="Disaster monitoring backend API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# IN-MEMORY DATABASE
# =========================================================

sensor_data = []

alerts = []

# Stores the previous severity of each node
previous_severity = {}


# =========================================================
# SIMULATOR NODE DATA
# =========================================================

simulation_nodes = {
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
# GENERATE SIMULATION DATA
# =========================================================

def generate_simulation_data(node_id, node):

    # -----------------------------------------------------
    # BATTERY
    # -----------------------------------------------------

    node["battery"] -= random.uniform(0.0, 0.3)

    if node["battery"] < 0:
        node["battery"] = 100


    # -----------------------------------------------------
    # WATER LEVEL
    # -----------------------------------------------------

    node["water_level"] += random.uniform(-3, 5)

    node["water_level"] = max(
        0,
        min(100, node["water_level"])
    )


    # -----------------------------------------------------
    # TEMPERATURE
    # -----------------------------------------------------

    node["temperature"] += random.uniform(
        -0.4,
        0.4
    )

    node["temperature"] = max(
        20,
        min(45, node["temperature"])
    )


    # -----------------------------------------------------
    # RSSI
    # -----------------------------------------------------

    node["rssi"] += random.randint(-2, 2)

    node["rssi"] = max(
        -120,
        min(-40, node["rssi"])
    )


    # -----------------------------------------------------
    # SOS
    # -----------------------------------------------------

    sos = random.random() < 0.01


    # -----------------------------------------------------
    # DISASTER
    # -----------------------------------------------------

    water = node["water_level"]

    if water >= 80:

        disaster = "Flood"

    elif water >= 50:

        disaster = "Flood"

    else:

        disaster = "Safe"


    # -----------------------------------------------------
    # PACKET
    # -----------------------------------------------------

    return {
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

        "sos": sos,

        "timestamp": datetime.now().isoformat()
    }


# =========================================================
# RECEIVE SENSOR DATA
# =========================================================

@app.post("/api/sensor-data")
def receive_sensor_data(data: dict):

    node_id = data.get("node_id")

    water = data.get("water_level", 0)

    sos = data.get("sos", False)


    # =====================================================
    # DETERMINE SEVERITY
    # =====================================================

    if sos is True:

        severity = "CRITICAL"

    elif water >= 80:

        severity = "CRITICAL"

    elif water >= 50:

        severity = "WARNING"

    else:

        severity = "SAFE"


    # Store calculated severity
    data["severity"] = severity

    # Server timestamp
    data["server_timestamp"] = datetime.now().isoformat()


    # =====================================================
    # SAVE SENSOR DATA
    # =====================================================

    sensor_data.append(data)

    # Keep latest 500 readings
    if len(sensor_data) > 500:

        sensor_data.pop(0)


    # =====================================================
    # GET PREVIOUS SEVERITY
    # =====================================================

    old_severity = previous_severity.get(
        node_id,
        "SAFE"
    )


    # =====================================================
    # FLOOD / DISASTER ALERT
    # =====================================================

    if severity == "CRITICAL":

        alert = {

            "type": "SOS" if sos else "FLOOD",

            "severity": "CRITICAL",

            "node_id": node_id,

            "latitude": data.get("latitude"),

            "longitude": data.get("longitude"),

            "water_level": water,

            "temperature": data.get("temperature"),

            "battery": data.get("battery"),

            "rssi": data.get("rssi"),

            "disaster": data.get("disaster"),

            "sos": sos,

            "timestamp": datetime.now().isoformat()
        }

        alerts.append(alert)


    elif severity == "WARNING":

        alert = {

            "type": "FLOOD",

            "severity": "WARNING",

            "node_id": node_id,

            "latitude": data.get("latitude"),

            "longitude": data.get("longitude"),

            "water_level": water,

            "temperature": data.get("temperature"),

            "battery": data.get("battery"),

            "rssi": data.get("rssi"),

            "disaster": data.get("disaster"),

            "sos": sos,

            "timestamp": datetime.now().isoformat()
        }

        alerts.append(alert)


    # =====================================================
    # EMAIL ALERT
    # =====================================================

    # Send email ONLY when node enters CRITICAL state.

    if (
        severity == "CRITICAL"
        and old_severity != "CRITICAL"
    ):

        print()
        print("================================")
        print("🚨 CRITICAL EVENT DETECTED")
        print("================================")

        print("Node:", node_id)

        print(
            "Location:",
            data.get("latitude"),
            data.get("longitude")
        )

        print(
            "Water:",
            water,
            "cm"
        )

        print(
            "Temperature:",
            data.get("temperature"),
            "°C"
        )

        print(
            "Battery:",
            data.get("battery"),
            "%"
        )

        print(
            "RSSI:",
            data.get("rssi"),
            "dBm"
        )

        print(
            "Disaster:",
            data.get("disaster")
        )

        print(
            "SOS:",
            sos
        )

        print("Sending email...")

        try:

            send_critical_alert(data)

            print("✅ CRITICAL EMAIL SENT")

        except Exception as e:

            print("❌ EMAIL FAILED:", e)

        print("================================")
        print()


    # =====================================================
    # UPDATE PREVIOUS SEVERITY
    # =====================================================

    previous_severity[node_id] = severity


    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "status": "received",

        "node_id": node_id,

        "severity": severity
    }


# =========================================================
# VERCEL SIMULATOR ENDPOINT
# =========================================================

@app.get("/api/simulate")
def run_simulation():

    generated = []

    for node_id, node in simulation_nodes.items():

        packet = generate_simulation_data(
            node_id,
            node
        )

        result = receive_sensor_data(packet)

        generated.append({
            "node_id": node_id,
            "water_level": packet["water_level"],
            "temperature": packet["temperature"],
            "battery": packet["battery"],
            "rssi": packet["rssi"],
            "severity": result["severity"],
            "sos": packet["sos"]
        })

    return {

        "status": "SIMULATION_OK",

        "timestamp": datetime.now().isoformat(),

        "nodes": generated
    }


# =========================================================
# GET LATEST DATA
# =========================================================

@app.get("/api/latest")
def get_latest():

    latest = {}

    for item in sensor_data:

        node_id = item.get("node_id")

        latest[node_id] = item

    return list(latest.values())


# =========================================================
# GET ALL SENSOR DATA
# =========================================================

@app.get("/api/history")
def get_history():

    return sensor_data


# =========================================================
# GET ALERTS
# =========================================================

@app.get("/api/alerts")
def get_alerts():

    return alerts[-50:]


# =========================================================
# SYSTEM STATUS
# =========================================================

@app.get("/api/status")
def system_status():

    return {

        "system": "ResQNet",

        "status": "ONLINE",

        "gateway": "ONLINE",

        "lora": "CONNECTED",

        "nodes": len(
            set(
                x.get("node_id")
                for x in sensor_data
            )
        ),

        "total_packets": len(sensor_data),

        "timestamp": datetime.now().isoformat()
    }


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "message": "ResQNet Backend is running",

        "status": "ONLINE"
    }