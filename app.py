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

# Load nursery data
df = pd.read_excel("NURSARY.xlsx")
required_cols = ['Name', 'Latitude', 'Longitude', 'Capacity', 'PlantsAvailable', 'Contact']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Excel must include: " + ", ".join(required_cols))
    st.stop()

# Load Khariar division boundary (optional)
try:
    with open("khariar_boundary.geojson", "r") as f:
        khariar_boundary = json.load(f)
except:
    khariar_boundary = None

# Get user's live location from browser
st.subheader("📍 Detecting your current location...")
loc = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((pos) => pos.coords)",
    key="get_user_location"
)

if loc and "latitude" in loc and "longitude" in loc:
    user_location = (loc["latitude"], loc["longitude"])
    st.success(f"✅ Location found.")
else:
    user_location = (_
