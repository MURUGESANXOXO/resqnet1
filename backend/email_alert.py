import os
import requests


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
ALERT_TO = os.getenv("RESQNET_ALERT_TO")


def send_critical_alert(data):

    if not RESEND_API_KEY:
        raise Exception("RESEND_API_KEY is not configured")

    if not ALERT_TO:
        raise Exception("RESQNET_ALERT_TO is not configured")


    node_id = data.get("node_id", "Unknown")

    latitude = data.get("latitude", "Unknown")
    longitude = data.get("longitude", "Unknown")

    water = data.get("water_level", "Unknown")
    temperature = data.get("temperature", "Unknown")
    battery = data.get("battery", "Unknown")
    rssi = data.get("rssi", "Unknown")

    disaster = data.get("disaster", "Unknown")
    sos = data.get("sos", False)

    timestamp = data.get(
        "timestamp",
        data.get("server_timestamp", "Unknown")
    )


    subject = f"🚨 ResQNet CRITICAL ALERT - {node_id}"


    message = f"""
RESQNET CRITICAL DISASTER ALERT
================================

🚨 CRITICAL EVENT DETECTED

Node ID:
{node_id}

LOCATION
--------
Latitude: {latitude}
Longitude: {longitude}

DISASTER INFORMATION
--------------------
Disaster: {disaster}
Severity: CRITICAL
SOS: {sos}

SENSOR DATA
-----------
Water Level: {water} cm
Temperature: {temperature} °C
Battery: {battery} %
RSSI: {rssi} dBm

TIME
----
{timestamp}

================================
ResQNet Disaster Monitoring System
"""


    response = requests.post(
        "https://api.resend.com/emails",

        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },

        json={
            "from": "onboarding@resend.dev",
            "to": [ALERT_TO],
            "subject": subject,
            "text": message
        },

        timeout=15
    )


    if response.status_code not in [200, 201]:

        raise Exception(
            f"Resend API error: "
            f"{response.status_code} "
            f"{response.text}"
        )


    print("✅ CRITICAL EMAIL SENT THROUGH RESEND")