import pandas as pd
import requests
from geopy.geocoders import Nominatim
import os

EBIRD_API_KEY = os.getenv("EBIRD_API_KEY", "your-ebird-api-key")

def geocode_location(location_text):
    geolocator = Nominatim(user_agent="birding-app")
    location = geolocator.geocode(location_text)
    if location:
        return location.latitude, location.longitude
    return None, None

def get_hotspots_by_location(location_text, species=None):
    lat, lng = geocode_location(location_text)
    if lat is None or lng is None:
        return None

    url = f"https://api.ebird.org/v2/ref/hotspot/geo?lat={lat}&lng={lng}&fmt=json&dist=50&back=30&maxResults=10"
    headers = {"X-eBirdApiToken": EBIRD_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    return pd.DataFrame(data)
