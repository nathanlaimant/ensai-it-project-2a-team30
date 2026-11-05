import pandas as pd
import requests
import streamlit as st
from utils.api_client import APIClient, api_client

st.set_page_config(
    page_title="Stations Favorites - VeloScope", page_icon="⭐", layout="wide"
)

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

st.title("⭐ Mes Stations Favorites")

if st.session_state["token"] is None:
    st.warning("Vous devez être connecté pour consulter vos stations favorites.")
    if st.button("Aller à la page de connexion"):
        st.switch_page("pages/connexion.py")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

try:
    favorites = api_client.get(
        "/favorites/",
        params={"page": 1, "size": 100},
        headers=headers,
    )
except requests.exceptions.RequestException as e:
    if "401" in str(e):
        st.error("Votre session a expiré. Veuillez vous reconnecter.")
        st.session_state["token"] = None
    else:
        st.error(f"Impossible de récupérer vos favoris : {e}")
    st.stop()

if not favorites:
    st.info("Vous n'avez aucune station en favori pour le moment.")
else:
    df_favorites = pd.DataFrame(favorites)
    st.metric("Nombre de stations favorites", len(df_favorites))
    st.dataframe(df_favorites, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Retirer une station des favoris")

    options_stations = {
        f"{station.get('name', 'Station')} (ID : {station['station_id']})": station[
            "station_id"
        ]
        for station in favorites
    }

    col1, col2 = st.columns([3, 1])
    with col1:
        choix_label = st.selectbox(
            "Sélectionnez la station à retirer :",
            options=list(options_stations.keys()),
        )
    with col2:
        st.write("")
        btn_supprimer = st.button("🗑️ Retirer des favoris", type="primary")

    if btn_supprimer:
        station_id_to_remove = options_stations[choix_label]
        try:
            api_client.delete(
                f"/favorites/{station_id_to_remove}",
                headers=headers,
            )
            st.success("Station retirée des favoris !")
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la suppression : {e}")
