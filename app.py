import streamlit as st
import pandas as pd
import folium
import json
from geopy.distance import geodesic
from folium.plugins import LocateControl
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Nursery Locator", layout="wide")
st.title("🌱 Public Nursery Locator")

# 🔹 Load Excel file (already uploaded in app)
df = pd.read_excel("NURSARY.xlsx")
required_cols = ['Name', 'Latitude', 'Longitude', 'Capacity', 'PlantsAvailable', 'Contact']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Excel must include: " + ", ".join(required_cols))
    st.stop()

# 🔹 Optional: Load Khariar boundary
try:
    with open("khariar_boundary.geojson", "r") as f:
        khariar_boundary = json.load(f)
except:
    khariar_boundary = None

# 🌍 Get user location
st.subheader("📍 Detecting your current location...")
loc = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((pos) => pos.coords)",
    key="get_user_location"
)

# ✅ Use real or fallback location
if loc and "latitude" in loc and "longitude" in loc:
    user_location = (loc["latitude"], loc["longitude"])
    st.success(f"✅ Location found: {user_location}")
else:
    user_location = (20.5600, 84.1400)
    st.warning("⚠️ Location not allowed. Using default (Khariar).")

# 🗺️ Map setup
m = folium.Map(location=user_location, zoom_start=12)
LocateControl(auto_start=True).add_to(m)

# 🔲 Optional: Add division boundary
if khariar_boundary:
    folium.GeoJson(
        khariar_boundary,
        name="Khariar Division",
        style_function=lambda x: {
            "fillColor": "orange",
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.1,
        },
    ).add_to(m)

# 🔁 Add nurseries to map
df['Distance_km'] = df.apply(
    lambda row: geodesic(user_location, (row['Latitude'], row['Longitude'])).km,
    axis=1
)

for _, row in df.iterrows():
    popup = f"""
    <b>{row['Name']}</b><br>
    Distance: {row['Distance_km']:.2f} km<br>
    Capacity: {row['Capacity']}<br>
    Plants Available: {row['PlantsAvailable']}<br>
    Contact: {row['Contact']}
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        tooltip=row['Name'],
        popup=popup,
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(m)

# 🔎 Click to view nursery info
st.subheader("🖱️ Click a nursery on the map to view info")
map_data = st_folium(m, width=1000, height=600)

if map_data and map_data.get("last_object_clicked_tooltip"):
    name = map_data["last_object_clicked_tooltip"]
    row = df[df["Name"] == name].iloc[0]
    distance_km = row["Distance_km"]
    st.success(f"📍 {name} – {distance_km:.2f} km away")
    st.markdown(f"""
    **Capacity:** {row['Capacity']}  
    **Plants Available:** {row['PlantsAvailable']}  
    **Contact:** {row['Contact']}
    """)
else:
    st.info("Click on a marker to view nursery details and your distance.")
