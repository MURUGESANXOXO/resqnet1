import random
from datetime import datetime
from backend.main import app


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


def generate_node_data(node_id, node):

    node["battery"] -= random.uniform(0.0, 0.3)

    if node["battery"] < 0:
        node["battery"] = 100

    node["water_level"] += random.uniform(-3, 5)
    node["water_level"] = max(
        0,
        min(100, node["water_level"])
    )

    node["temperature"] += random.uniform(-0.4, 0.4)
    node["temperature"] = max(
        20,
        min(45, node["temperature"])
    )

    node["rssi"] += random.randint(-2, 2)
    node["rssi"] = max(
        -120,
        min(-40, node["rssi"])
    )

    sos = random.random() < 0.01

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

    return {
        "node_id": node_id,
        "latitude": round(node["latitude"], 6),
        "longitude": round(node["longitude"], 6),
        "battery": round(node["battery"], 1),
        "rssi": node["rssi"],
        "water_level": round(node["water_level"], 1),
        "temperature": round(node["temperature"], 1),
        "disaster": disaster,
        "severity": severity,
        "sos": sos,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/simulate")
def simulate():

    generated = []

    for node_id, node in nodes.items():

        packet = generate_node_data(
            node_id,
            node
        )

        generated.append(packet)

        # Directly feed the packet into the existing backend
        from backend.main import sensor_data

        sensor_data.append(packet)

    return {
        "status": "SIMULATION_OK",
        "timestamp": datetime.now().isoformat(),
        "nodes": generated
    }