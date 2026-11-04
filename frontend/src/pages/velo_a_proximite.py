import geocoder
import streamlit as st
from utils.api_client import APIClient

st.title("Je veux trouver un vélo à proximité")

def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None

if __name__ == "__main__":
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        st.write("On a vos coordonnées GPS maintenant")
        latitude, longitude = coordinates

stations_nearby = APIClient().get("/nearby_recos", params={"lat": latitude, "lon": longitude, "radius_meters": 20})