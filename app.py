import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
from collections import deque
import folium
from streamlit_folium import st_folium
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Water Monitoring", layout="wide")
st.title("🚰 AI-Powered Smart Water Pipeline Monitoring System")

# ---------------- LOAD MODEL ----------------
model = joblib.load("anomaly_model.pkl")
scaler = joblib.load("scaler.pkl")

# ---------------- SESSION STATE ----------------
if "run" not in st.session_state:
    st.session_state.run = False

if "flow" not in st.session_state:
    st.session_state.flow = deque(maxlen=50)
    st.session_state.pressure = deque(maxlen=50)
    st.session_state.acoustic = deque(maxlen=50)

if "map_key" not in st.session_state:
    st.session_state.map_key = 0

# ---------------- START / STOP ----------------
c1, c2 = st.columns(2)

if c1.button("▶️ Start Monitoring"):
    st.session_state.run = True

if c2.button("⏹ Stop Monitoring"):
    st.session_state.run = False

# ---------------- ZONES ----------------
zones = ["Zone_A", "Zone_B", "Zone_C", "Zone_D"]

zone_map_model = {
    "Zone_A": "zone_Zone_1",
    "Zone_B": "zone_Zone_2",
    "Zone_C": "zone_Zone_3",
    "Zone_D": "zone_Zone_4"
}

zone_coordinates = {
    "Zone_A": [18.5204, 73.8567],
    "Zone_B": [18.5314, 73.8446],
    "Zone_C": [18.5420, 73.8650],
    "Zone_D": [18.5100, 73.8700]
}

# ---------------- CONSTANTS ----------------
NORMAL_FLOW = 100
NORMAL_PRESSURE = 55

model_features = [
    'flow', 'pressure', 'acoustic',
    'zone_Zone_1', 'zone_Zone_2', 'zone_Zone_3', 'zone_Zone_4',
    'flow_ma', 'pressure_drop_rate', 'acoustic_change', 'flow_pressure_ratio'
]

# ---------------- FUNCTIONS ----------------
def get_severity(flow, pressure):
    score = (NORMAL_FLOW - flow) + (NORMAL_PRESSURE - pressure)

    if score < 5:
        return "🟢 LOW", "green"
    elif score < 15:
        return "🟡 MEDIUM", "orange"
    else:
        return "🔴 HIGH", "red"

def estimate_water_loss(flow):
    return round(abs(NORMAL_FLOW - flow), 2)

# def generate_live_data():
#     zone = np.random.choice(zones)

#     flow = np.random.normal(100, 5)
#     pressure = np.random.normal(55, 3)
#     acoustic = np.random.normal(25, 2)

#     df = pd.DataFrame([[flow, pressure, acoustic]],
#                       columns=["flow", "pressure", "acoustic"])

#     return df, zone, flow, pressure, acoustic
def generate_live_data():

    zone = np.random.choice(zones)

    flow = np.random.normal(100, 5)
    pressure = np.random.normal(55, 3)
    acoustic = np.random.normal(25, 2)

    # 💥 20% chance to simulate leak
    if np.random.rand() < 0.2:
        pressure *= np.random.uniform(0.4, 0.6)
        flow *= np.random.uniform(1.3, 1.6)
        acoustic *= np.random.uniform(1.5, 2.0)

    df = pd.DataFrame([[flow, pressure, acoustic]],
                      columns=["flow", "pressure", "acoustic"])

    return df, zone, flow, pressure, acoustic

# ---------------- MAIN ----------------
if st.session_state.run:

    data, zone, flow, pressure, acoustic = generate_live_data()

    # FEATURE ENGINEERING
    data["flow_ma"] = data["flow"]
    data["pressure_drop_rate"] = 0
    data["acoustic_change"] = 0
    data["flow_pressure_ratio"] = data["flow"] / data["pressure"]

    data[zone_map_model[zone]] = 1

    for col in model_features:
        if col not in data:
            data[col] = 0

    data = data[model_features]

    scaled = scaler.transform(data)
    prediction = model.predict(scaled)

    # STORE DATA
    st.session_state.flow.append(flow)
    st.session_state.pressure.append(pressure)
    st.session_state.acoustic.append(acoustic)

    # ---------------- LAYOUT ----------------
    left, right = st.columns([2, 1])

    # ================= ANALYTICS =================
    with left:

        st.info(f"📍 Monitoring Zone: {zone}")

        chart_data = pd.DataFrame({
            "Flow": st.session_state.flow,
            "Pressure": st.session_state.pressure,
            "Acoustic": st.session_state.acoustic
        })

        c1, c2, c3 = st.columns(3)

        c1.subheader("Flow Rate")
        c1.plotly_chart(px.line(chart_data, y="Flow"), use_container_width=True)

        c2.subheader("Pressure")
        c2.plotly_chart(px.line(chart_data, y="Pressure"), use_container_width=True)

        c3.subheader("Acoustic")
        c3.plotly_chart(px.line(chart_data, y="Acoustic"), use_container_width=True)

    # ================= LEAK LOGIC =================
    leak_detected = prediction[0] == -1

    if leak_detected:

        severity, color = get_severity(flow, pressure)
        water_loss = estimate_water_loss(flow)

        with left:
            st.error(f"🚨 Leak detected in {zone}")
            st.markdown(f"### Severity Level: {severity}")
            st.markdown(f"### 💧 Estimated Water Loss: {water_loss} L/min")

        # ================= MAP =================
        with right:

            st.subheader("🗺 Leak Location")

            m = folium.Map(location=zone_coordinates[zone], zoom_start=14)

            folium.Marker(
                location=zone_coordinates[zone],
                popup=f"Leak in {zone} ({severity})",
                icon=folium.Icon(color=color),
            ).add_to(m)

            st.session_state.map_key += 1

            st_folium(
                m,
                width=450,
                height=450,
                key=f"map_{st.session_state.map_key}"
            )

    else:
        with left:
            st.success("✅ System Normal — No Leak Detected")

        with right:
            st.info("🗺 Map will appear when a leak is detected")

    time.sleep(3)
    st.rerun()

else:
    st.warning("⏹ Monitoring stopped. Click 'Start Monitoring' to begin.")
