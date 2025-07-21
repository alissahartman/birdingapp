import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="Birding Hotspots", layout="wide")
st.title("Where should I go birding?")
st.write("Enter a location and find nearby birding hotspots using eBird data.")

# Location text box and button
location = st.text_input("City, State OR Zip Code:", value="San Francisco, CA", key="location")
distance_km = st.slider("Search radius (km):", min_value=1, max_value=50, value=15)

if st.button("Enter"):
    with st.spinner("Finding hotspots..."):
        st.write("You entered:", location)

geolocator = Nominatim(user_agent="birding_app")

location_obj = geolocator.geocode(location)

api_key = "dj75ond675p1"

if location_obj:
    lat = location_obj.latitude
    lon = location_obj.longitude
    st.success(f"Coordinates: {lat:.4f}, {lon:.4f}")
else:
    st.error("Location not found. Please try a different city or ZIP code.")

# Construct the eBird API URL
url = "https://api.ebird.org/v2/ref/hotspot/geo"
params = {
    "lat": lat,
    "lng": lon,
    "fmt": "json",
    "dist": distance_km,        # radius in kilometers
    "back": 30,        # how many days back to look for activity
    "maxResults": 10   # max number of hotspots to return
}

# Add the API key to headers
headers = {
    "X-eBirdApiToken": api_key
}

# Make the request
response = requests.get(url, params=params, headers=headers)

# Check response
if response.status_code == 200:
    hotspots = response.json()

    if hotspots:
        st.subheader("Nearby Birding Hotspots")

        # Create a DataFrame
        df = pd.DataFrame(hotspots)
        df["lat"] = df["lat"].astype(float)
        df["lng"] = df["lng"].astype(float)
        df["ebird_url"] = "https://ebird.org/hotspot/" + df["locId"]

        # Show map with Pydeck
        import pydeck as pdk

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lng, lat]',
            get_radius=500,
            get_color=[0, 150, 0],
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=10,
            pitch=0
        )

        st.pydeck_chart(pdk.Deck(
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{locName}"}
        ))

    else:
        st.warning("No hotspots found in this area.")
else:
    st.error("Failed to fetch data from eBird API.")

# Hotspot container with scrolling
st.subheader("Nearby Birding Hotspots")

st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)

for hotspot in hotspots:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"📍 **{hotspot['locName']}**")
        st.caption(f"{hotspot['lat']:.4f}, {hotspot['lng']:.4f}")
        loc_id = hotspot["locId"]
        ebird_url = f"https://ebird.org/hotspot/{loc_id}"
        st.markdown(f"[View on eBird]({ebird_url})")

    with col2:
        sightings_url = f"https://api.ebird.org/v2/data/obs/{loc_id}/recent"
        sightings_response = requests.get(sightings_url, headers=headers)

        if sightings_response.status_code == 200:
            observations = sightings_response.json()
            if observations:
                species_seen = {obs["comName"] for obs in observations}
                st.write(f"🦉 {len(species_seen)} species seen recently")
                for name in list(sorted(species_seen))[:5]:
                    st.caption(f"• {name}")
            else:
                st.write("🦉 No recent sightings")
        else:
            st.write("⚠️ Could not retrieve recent sightings")

    st.markdown("---")

## in cmd terminal
# 1. activate venv: .venv\Scripts\activate.bat
# 2. run app: streamlit run app.py