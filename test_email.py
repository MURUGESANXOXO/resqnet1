from backend.email_alert import send_critical_alert


test_node = {
    "node_id": "TEST-N1",

    "latitude": 13.0827,
    "longitude": 80.2707,

    "water_level": 92.5,

    "temperature": 32.4,

    "battery": 86.7,

    "rssi": -71,

    "disaster": "Flood",

    "severity": "CRITICAL",

    "sos": False,

    "server_timestamp": "2026-09-01 22:45:00"
}


print("Sending test critical email...")

send_critical_alert(test_node)

print("Test completed.")