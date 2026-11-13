import pandas as pd
import streamlit as st

from utils.api_client import APIClient

st.set_page_config(page_title="Stations - VeloScope", page_icon="🚲", layout="wide")

st.title("🚲 Liste des stations VeloScope")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "in_search" not in st.session_state:
    st.session_state["in_search"] = None

client: APIClient = st.session_state["api_client"]


@st.cache_data(ttl=60)
def get_stations_states(station_ids: tuple[str, ...]) -> dict[str, str | None]:
    """
    Retourne l'état de chaque station trouvée via un appel batch.
    """
    if not station_ids:
        return {}
    statuses = APIClient().get_stations_statuses(list(station_ids))
    return {
        sid: (status.get("station_state") if status else None)
        for sid, status in statuses.items()
    }


st.sidebar.header("Filtres")
terme_recherche = st.sidebar.text_input(
    "Recherche par nom",
    placeholder="Ex : République...",
    value=st.session_state["in_search"],
)

size_wanted = st.number_input(
    label="Nombre de stations à afficher", min_value=5, max_value=50, value=10
)
page_wanted = st.number_input(label="Afficher la page :", min_value=1, max_value=20, value=1)

stations = client.post(
    "/station",
    data={
        "name": terme_recherche,
        "page": page_wanted,
        "size": size_wanted,
    },
)

if not stations:
    st.warning(
        "Aucune station trouvée. Assurez-vous que le serveur FastAPI est bien démarré "
        "ou changez le numéro de page à afficher."
    )
    st.stop()

station_ids = tuple(station["station_id"] for station in stations)
states_by_id = get_stations_states(station_ids)

nb_sans_statut = 0
for station in stations:
    state = states_by_id.get(station["station_id"])
    if state is None:
        nb_sans_statut += 1
    station["state"] = state or "Indisponible"

if nb_sans_statut:
    st.caption(f"Statut indisponible pour {nb_sans_statut} station(s) de cette page.")

st.metric("Total des stations affichées", len(stations))

st.divider()

# Affichage sous forme de lignes interactives propres pour conserver la session
for station in stations:
    s_id = str(station["station_id"])
    s_name = station["name"]
    s_address = station.get("address") or "Adresse inconnue"
    s_capacity = station.get("capacity", "N/A")
    s_state = station["state"]

    cols = st.columns([1.5, 3, 2, 1, 1, 1])
    cols[0].write(f"`{s_id}`")
    cols[1].write(f"**{s_name}**")
    cols[2].write(s_address)
    cols[3].write(f"Capacité : {s_capacity}")
    cols[4].write(s_state)

    with cols[5]:
        if st.button("ℹ️ Infos", key=f"btn_station_{s_id}", use_container_width=True):
            # On met à jour à la fois le state et les query_params pour la page info
            st.session_state["selected_station_id"] = s_id
            st.query_params["station_id"] = s_id
            st.switch_page("pages/station_info.py")

    st.divider()
