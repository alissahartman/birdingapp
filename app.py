import streamlit as st
from utils import get_hotspots_by_location
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Where Should I Go Birding?", layout="wide")

st.title("🦜 Where Should I Go Birding?")
st.write("Enter a location and find nearby birding hotspots using eBird data.")

# Inputs
location = st.text_input("Enter a city or ZIP code:", "San Francisco, CA")
species = st.text_input("Optional: Target bird species (e.g., 'Western Tanager')", "")

if st.button("Find Hotspots"):
    with st.spinner("Searching nearby birding hotspots..."):
        hotspots_df = get_hotspots_by_location(location, species)

        if hotspots_df is not None and not hotspots_df.empty:
            st.success(f"Found {len(hotspots_df)} hotspots near {location}")

            m = folium.Map(location=[hotspots_df.lat.mean(), hotspots_df.lng.mean()], zoom_start=10)
            for _, row in hotspots_df.iterrows():
                popup = f"<b>{row['locName']}</b><br>Species count: {row['numSpeciesAllTime']}"
                folium.Marker([row['lat'], row['lng']], popup=popup).add_to(m)

            st_folium(m, width=700, height=500)
        else:
            st.warning("No hotspots found. Try another location or check your API key.")
