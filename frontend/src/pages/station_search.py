import streamlit as st
from utils.api_client import api_client
from utils.log_init import get_page_logger

st.title("Rechercher une station")

logger = get_page_logger("station_search")

research = st.text_input("Entrer un lieu ou une adresse :", type="search")

if research:
    try:
        stations_searched = api_client.post(
            "/station/",
            data={"name": research},
        )

        if not stations_searched:
            st.warning("Aucune station trouvée")
        else:
            st.write(f"{len(stations_searched)} station(s) trouvée(s)")
            for station in stations_searched:
                st.write(f"- {station['name']} ({station['address']})")

    except Exception as e:
        logger.exception(f"Erreur lors de la recherche de stations : {e}")
        st.error(f"Une erreur est survenue : {e}")
