from fastapi import FastAPI
from datetime import datetime

from backend.email_alert import send_critical_alert


app = FastAPI(
    title="ResQNet Backend",
    description="Disaster monitoring backend API",
    version="1.0"
)


# =========================================================
# IN-MEMORY DATABASE
# =========================================================

sensor_data = []

alerts = []

# Stores the previous severity of each node
previous_severity = {}


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
    #
    # This prevents sending an email every 10 seconds
    # while the node remains critical.

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