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
    """Position approximative d'après l'adresse IP (peu fiable)."""
    g = geocoder.ip("me")
    if g.latlng is None:
        raise ValueError("Position IP introuvable")
    return g.latlng


@st.cache_data(ttl=600)
def locate_from_address(address: str):
    """Position d'une adresse ou d'une ville (Nominatim, puis Open-Meteo en secours)."""
    # 1) Nominatim (OpenStreetMap), avec un User-Agent explicite
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "jsonv2", "limit": 1},
            headers={
                "User-Agent": "veloscope-ensai-team30/1.0 (projet etudiant ENSAI)"
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except requests.RequestException:
        pass  # on tente le service de secours

    # 2) Open-Meteo (recherche par nom de lieu, sans clé)
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": address.split(",")[0].strip(),
                "count": 1,
                "language": "fr",
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results")
        if results:
            return float(results[0]["latitude"]), float(results[0]["longitude"])
    except requests.RequestException as e:
        raise ValueError(f"service de géocodage injoignable : {e}")

    raise ValueError("aucun résultat pour cette adresse")


mode = st.radio(
    "Ma position",
    ["Saisir une adresse ou une ville", "Position approximative (IP)"],
)

coordinates = None
if mode == "Saisir une adresse ou une ville":
    address = st.text_input("Adresse ou ville", placeholder="Ex : Rennes, France")
    if address:
        try:
            coordinates = locate_from_address(address)
        except ValueError as e:
            st.error(f"Adresse introuvable ({e}).")
else:
    try:
        coordinates = locate_from_ip()
    except ValueError:
        st.error("Impossible de récupérer votre position.")

if coordinates is None:
    st.stop()

latitude, longitude = coordinates
st.caption(f"Position utilisée : {latitude:.4f}, {longitude:.4f}")

radius = st.slider("Rayon de recherche (mètres)", 100, 5000, 1000, step=100)

with st.expander("Filtres facultatifs"):
    op_cap = st.number_input("Capacité opérationnelle minimale", min_value=0, value=0)
    score_min = st.slider("Score de fiabilité minimal", 0, 100, 0)
    vehicle_type = st.selectbox(
        "Type de vélo disponible",
        options=["all", "mechanical", "electric"],
        format_func=lambda x: {
            "all": "Tous les vélos",
            "mechanical": "Mécanique",
            "electric": "Électrique",
        }.get(x, x),
    )

payload = {
    "lat": latitude,
    "lon": longitude,
    "radius_meters": radius,
    "op_cap": op_cap or None,
    "score_min": float(score_min) if score_min else None,
    "vehicle_type": vehicle_type,
}

try:
    stations_nearby = APIClient().get_nearby_recommendations(payload)
except requests.exceptions.HTTPError as e:
    st.error(f"Erreur de l'API : {e}")
except requests.exceptions.ConnectionError:
    st.error("Impossible de joindre le backend.")
else:
    if not stations_nearby:
        st.info(
            f"Aucune station trouvée dans un rayon de {radius} m. "
            "Essayez d'agrandir le rayon."
        )
    else:
        df = pd.DataFrame(stations_nearby)
        st.success(
            f"{len(df)} station(s) trouvée(s), de la plus proche à la plus éloignée."
        )
        if {"lat", "lon"}.issubset(df.columns):
            st.map(df[["lat", "lon"]])
            df = df.drop(columns=["lat", "lon"])
        st.dataframe(df, hide_index=True)
