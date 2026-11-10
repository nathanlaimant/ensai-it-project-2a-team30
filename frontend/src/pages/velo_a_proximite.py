import geocoder
import pandas as pd
import requests
import streamlit as st
from utils.api_client import APIClient

st.title("Je veux trouver un vélo à proximité")

# Adapter cette clé à celle utilisée dans connexion.py
SESSION_TOKEN_KEY = "token"

if not st.session_state.get(SESSION_TOKEN_KEY):
    st.warning("Vous devez être connecté pour trouver un vélo à proximité.")
    st.stop()


@st.cache_data(ttl=600)
def locate_from_ip():
    """Position approximative d'après l'adresse IP (peu fiable), ou None."""
    g = geocoder.ip("me")
    return g.latlng if g.latlng is not None else None


@st.cache_data(ttl=600)
def locate_from_address(address: str):
    """Position d'une adresse ou d'une ville via OpenStreetMap, ou None."""
    g = geocoder.osm(address)
    return g.latlng if g.ok and g.latlng is not None else None


mode = st.radio(
    "Ma position",
    ["Saisir une adresse ou une ville", "Position approximative (IP)"],
)

coordinates = None
if mode == "Saisir une adresse ou une ville":
    address = st.text_input("Adresse ou ville", placeholder="Ex : Rennes")
    if address:
        coordinates = locate_from_address(address)
        if coordinates is None:
            st.error("Adresse introuvable.")
else:
    coordinates = locate_from_ip()
    if coordinates is None:
        st.error("Impossible de récupérer votre position.")

if coordinates is None:
    st.stop()

latitude, longitude = coordinates
st.caption(f"Position utilisée : {latitude:.4f}, {longitude:.4f}")

radius = st.slider("Rayon de recherche (mètres)", 100, 5000, 1000, step=100)

with st.expander("Filtres facultatifs"):
    op_cap = st.number_input("Capacité opérationnelle minimale", min_value=0, value=0)
    score_min = st.slider("Score de fiabilité minimal", 0, 100, 0)

payload = {
    "lat": latitude,
    "lon": longitude,
    "radius_meters": radius,
    "op_cap": op_cap or None,
    "score_min": float(score_min) if score_min else None,
}

try:
    stations_nearby = APIClient().get_nearby_recommendations(payload)
except requests.exceptions.HTTPError as e:
    st.error(f"Erreur de l'API : {e}")
except requests.exceptions.ConnectionError:
    st.error("Impossible de joindre le backend.")
else:
    if not stations_nearby:
        st.info(f"Aucune station trouvée dans un rayon de {radius} m. Essayez d'agrandir le rayon.")
    else:
        df = pd.DataFrame(stations_nearby)
        st.success(f"{len(df)} station(s) trouvée(s), de la plus proche à la plus éloignée.")
        st.map(df[["lat", "lon"]])
        st.dataframe(df.drop(columns=["lat", "lon"]), hide_index=True)
