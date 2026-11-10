import geocoder
import requests
import streamlit as st
from utils.api_client import APIClient

st.title("Je veux trouver un vélo à proximité")

RADIUS_METERS = 1000


def get_current_gps_coordinates():
    """Retourne (latitude, longitude) d'après l'adresse IP, ou None."""
    g = geocoder.ip("me")
    if g.latlng is not None:
        return g.latlng
    return None


coordinates = get_current_gps_coordinates()

if coordinates is None:
    st.error("Impossible de récupérer vos coordonnées GPS.")
else:
    latitude, longitude = coordinates
    st.write("On a vos coordonnées GPS maintenant")

    # ATTENTION : les clés du payload doivent correspondre aux champs de
    # StationRecommendationRequest (backend/src/schema/station_model.py).
    payload = {
        "lat": latitude,
        "lon": longitude,
        "radius_meters": RADIUS_METERS,
    }

    try:
        stations_nearby = APIClient().get_nearby_recommendations(payload)
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur de l'API : {e}")
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre le backend.")
    else:
        if not stations_nearby:
            st.info(f"Aucune station trouvée dans un rayon de {RADIUS_METERS} m.")
        else:
            st.dataframe(stations_nearby)
