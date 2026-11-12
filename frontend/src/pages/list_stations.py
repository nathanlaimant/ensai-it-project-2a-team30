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

    Les erreurs HTTP éventuelles sont relancées (et donc jamais mises en cache).
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
    label="Nombre de stations à afficher", min_value=5, max_value=50
)
page_wanted = st.number_input(label="Afficher la page :", min_value=1, max_value=20)

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

df_brut = pd.DataFrame(stations)
df = df_brut[["station_id", "name", "address", "capacity", "state"]]
df = df.rename(
    columns={
        "station_id": "Identifiant",
        "name": "Nom",
        "address": "Adresse",
        "capacity": "Capacité",
        "state": "État",
    }
)
df["Infos de la station"] = df.apply(
    lambda row: f"/proxy/8501/station_info?station_id={row['Identifiant']}", axis=1
)

st.metric("Total des stations affichées", len(df))

st.dataframe(
    df,
    column_config={
        "Infos de la station": st.column_config.LinkColumn(
            label="Infos", display_text="ℹ️"
        ),
    },
    use_container_width=True,
    hide_index=True,
)
