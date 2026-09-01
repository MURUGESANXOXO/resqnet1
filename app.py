import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ResQNet Disaster Monitoring",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 ResQNet Disaster Monitoring Dashboard")
st.caption("📡 Real-time disaster monitoring using simulated LoRa telemetry")


# =========================================================
# AUTO REFRESH
# =========================================================

# Refresh dashboard every 10 seconds
st_autorefresh(
    interval=10000,
    key="resqnet_refresh"
)


# =========================================================
# BACKEND
# =========================================================

BACKEND_URL = "https://resqnet1-backend.vercel.app"


# =========================================================
# GET DATA FROM BACKEND
# =========================================================

try:

    response = requests.get(
        f"{BACKEND_URL}/api/latest",
        timeout=5
    )

    if response.status_code == 200:

        nodes = response.json()
        backend_online = True

    else:

        nodes = []
        backend_online = False

except Exception:

    nodes = []
    backend_online = False


# =========================================================
# BACKEND STATUS
# =========================================================

if backend_online:

    st.success("🟢 Backend ONLINE")

else:

    st.error("🔴 Backend OFFLINE")


# =========================================================
# NODE STATISTICS
# =========================================================

total_nodes = len(nodes)

critical_nodes = 0
warning_nodes = 0
safe_nodes = 0
sos_nodes = 0

for node in nodes:

    severity = node.get("severity", "SAFE")

    if severity == "CRITICAL":

        critical_nodes += 1

    elif severity == "WARNING":

        warning_nodes += 1

    else:

        safe_nodes += 1

    if node.get("sos") is True:

        sos_nodes += 1


# =========================================================
# DASHBOARD CARDS
# =========================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "📡 Total Nodes",
        total_nodes
    )

with col2:

    st.metric(
        "🔴 Critical",
        critical_nodes
    )

with col3:

    st.metric(
        "🟠 Warning",
        warning_nodes
    )

with col4:

    st.metric(
        "🟢 Safe",
        safe_nodes
    )

with col5:

    st.metric(
        "🚨 SOS",
        sos_nodes
    )


st.divider()


# =========================================================
# NODE STATUS
# =========================================================

st.subheader("📡 LoRa Node Status")


if len(nodes) == 0:

    st.warning(
        "No node data received from backend."
    )

else:

    columns = st.columns(len(nodes))

    for index, node in enumerate(nodes):

        with columns[index]:

            node_id = node.get("node_id", "Unknown")

            battery = node.get("battery", 0)

            rssi = node.get("rssi", 0)

            water = node.get("water_level", 0)

            temperature = node.get("temperature", 0)

            severity = node.get(
                "severity",
                "SAFE"
            )

            if severity == "CRITICAL":

                status_icon = "🔴"

            elif severity == "WARNING":

                status_icon = "🟠"

            else:

                status_icon = "🟢"

            st.markdown(
                f"### {status_icon} {node_id}"
            )

            st.write(
                f"🔋 Battery: **{battery}%**"
            )

            st.write(
                f"📶 RSSI: **{rssi} dBm**"
            )

            st.write(
                f"🌊 Water: **{water} cm**"
            )

            st.write(
                f"🌡️ Temperature: **{temperature} °C**"
            )

            st.write(
                f"Status: **{severity}**"
            )

            if node.get("sos") is True:

                st.error(
                    "🚨 SOS ACTIVE"
                )


st.divider()


# =========================================================
# MAP
# =========================================================

st.subheader("🗺️ Live Disaster Monitoring Map")


m = folium.Map(
    location=[
        13.0827,
        80.2707
    ],
    zoom_start=13
)


# =========================================================
# GATEWAY LOCATION
# =========================================================

gateway_lat = 13.0885
gateway_lon = 80.2795


# =========================================================
# DYNAMIC NODE ZONES
# =========================================================

for node in nodes:

    latitude = node["latitude"]

    longitude = node["longitude"]

    node_id = node["node_id"]

    severity = node.get(
        "severity",
        "SAFE"
    )

    water = node.get(
        "water_level",
        0
    )


    # -----------------------------------------------------
    # SELECT COLOR AND RADIUS
    # -----------------------------------------------------

    if severity == "CRITICAL":

        zone_color = "red"

        radius = 450

        status_text = "🔴 CRITICAL"

    elif severity == "WARNING":

        zone_color = "orange"

        radius = 350

        status_text = "🟠 WARNING"

    else:

        zone_color = "green"

        radius = 250

        status_text = "🟢 SAFE"


    # -----------------------------------------------------
    # NODE DISASTER CIRCLE
    # -----------------------------------------------------

    folium.Circle(

        location=[
            latitude,
            longitude
        ],

        radius=radius,

        color=zone_color,

        fill=True,

        fill_color=zone_color,

        fill_opacity=0.25,

        popup=f"""
        <b>📡 Node:</b> {node_id}<br>
        <b>Status:</b> {status_text}<br>
        <b>Water Level:</b> {water} cm<br>
        <b>Radius:</b> {radius} m
        """

    ).add_to(m)


# =========================================================
# NODE MARKERS
# =========================================================

for node in nodes:

    latitude = node["latitude"]

    longitude = node["longitude"]

    node_id = node["node_id"]

    severity = node.get(
        "severity",
        "SAFE"
    )

    battery = node.get(
        "battery",
        0
    )

    rssi = node.get(
        "rssi",
        0
    )

    water = node.get(
        "water_level",
        0
    )

    temperature = node.get(
        "temperature",
        0
    )

    disaster = node.get(
        "disaster",
        "Unknown"
    )

    sos = node.get(
        "sos",
        False
    )


    # -----------------------------------------------------
    # MARKER COLOR
    # -----------------------------------------------------

    if severity == "CRITICAL":

        marker_color = "red"

    elif severity == "WARNING":

        marker_color = "orange"

    else:

        marker_color = "green"


    # -----------------------------------------------------
    # POPUP
    # -----------------------------------------------------

    popup = f"""

    <h4>📡 {node_id}</h4>

    <b>Battery:</b> {battery}%<br>

    <b>RSSI:</b> {rssi} dBm<br>

    <b>Water Level:</b> {water} cm<br>

    <b>Temperature:</b> {temperature} °C<br>

    <b>Disaster:</b> {disaster}<br>

    <b>Severity:</b> {severity}<br>

    <b>SOS:</b> {sos}

    """


    # -----------------------------------------------------
    # MARKER
    # -----------------------------------------------------

    folium.Marker(

        [
            latitude,
            longitude
        ],

        popup=popup,

        tooltip=f"{node_id} | {severity}",

        icon=folium.Icon(

            color=marker_color,

            icon="signal"

        )

    ).add_to(m)


# =========================================================
# SOS MARKERS
# =========================================================

for node in nodes:

    if node.get("sos") is True:

        latitude = node["latitude"]

        longitude = node["longitude"]

        node_id = node["node_id"]


        folium.Marker(

            [
                latitude,
                longitude
            ],

            popup=f"""
            <b>🚨 SOS ALERT</b><br>

            Node: {node_id}<br>

            Priority: HIGH<br>

            Immediate assistance required.
            """,

            tooltip="🚨 SOS",

            icon=folium.Icon(

                color="darkred",

                icon="warning-sign"

            )

        ).add_to(m)


# =========================================================
# GATEWAY
# =========================================================

folium.Marker(

    [
        gateway_lat,
        gateway_lon
    ],

    popup="""

    <b>📡 Raspberry Pi Gateway</b><br>

    Internet: Available<br>

    LoRa: Connected

    """,

    tooltip="Gateway",

    icon=folium.Icon(

        color="blue",

        icon="cloud"

    )

).add_to(m)


# =========================================================
# MESH LINKS BETWEEN NODES
# =========================================================

if len(nodes) >= 2:

    for i in range(
        len(nodes) - 1
    ):

        folium.PolyLine(

            [

                [
                    nodes[i]["latitude"],
                    nodes[i]["longitude"]
                ],

                [
                    nodes[i + 1]["latitude"],
                    nodes[i + 1]["longitude"]
                ]

            ],

            color="green",

            weight=4,

            opacity=0.7

        ).add_to(m)


# =========================================================
# LAST NODE → GATEWAY
# =========================================================

if len(nodes) > 0:

    folium.PolyLine(

        [

            [
                nodes[-1]["latitude"],
                nodes[-1]["longitude"]
            ],

            [
                gateway_lat,
                gateway_lon
            ]

        ],

        color="blue",

        weight=3,

        opacity=0.7

    ).add_to(m)


# =========================================================
# DISPLAY MAP
# =========================================================

st_folium(

    m,

    width=1400,

    height=650

)


st.divider()


# =========================================================
# TELEMETRY TABLE
# =========================================================

st.subheader(
    "📊 Current Node Telemetry"
)


if nodes:

    table_data = []


    for node in nodes:

        table_data.append({

            "Node":
                node["node_id"],

            "Battery (%)":
                node["battery"],

            "RSSI (dBm)":
                node["rssi"],

            "Water (cm)":
                node["water_level"],

            "Temperature (°C)":
                node["temperature"],

            "Disaster":
                node["disaster"],

            "Severity":
                node["severity"],

            "SOS":
                node["sos"]

        })


    st.dataframe(

        table_data,

        use_container_width=True

    )


# =========================================================
# LAST UPDATE
# =========================================================

st.divider()

st.caption(
    "📡 Dashboard automatically refreshes every 10 seconds."
)

st.caption(
    "🤖 Current telemetry is simulated. "
    "Production system can replace the simulator with real LoRa data."
)