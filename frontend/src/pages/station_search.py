import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger

st.set_page_config(
    page_title="Rechercher une station",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Rechercher une station")

logger = get_page_logger("station_search")

research = st.text_input("Entrer un lieu ou une adresse :", type="search")

if research:
    try:
        # Recherche des stations auprès du backend
        stations_searched = api_client.post(
            "/station",
            data={"name": research},
        )

        if not stations_searched:
            st.warning("Aucune station trouvée")

        else:
            st.write(f"{len(stations_searched)} station(s) trouvée(s)")

            # Affichage des résultats sous forme de boutons
            for station in stations_searched:

                station_id = str(station["station_id"])
                name = station["name"]
                address = station.get("address") or "Adresse inconnue"

                if st.button(
                    f"🚲 {name} ({address})",
                    key=f"station_{station_id}",
                    use_container_width=True,
                ):
                    # Enregistrement de la station sélectionnée dans le state et dans l'URL
                    st.session_state["selected_station_id"] = station_id
                    st.query_params["station_id"] = station_id

                    # Redirection vers station_info
                    st.switch_page("pages/station_info.py")

    except Exception as e:
        logger.exception(f"Erreur lors de la recherche de stations : {e}")
        st.error(f"Une erreur est survenue : {e}")
