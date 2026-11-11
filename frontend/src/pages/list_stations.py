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

st.sidebar.header("Filtres")
terme_recherche = st.sidebar.text_input(
    "Recherche par nom", placeholder="Ex : République...",
    value=st.session_state["in_search"] 
)

size_wanted = st.number_input(label="Nombre de stations à afficher", min_value=5, max_value=50)
page_wanted = st.number_input(label="Afficher la page :", min_value=1, max_value=20)

stations = client.post(
    "/station",
    data={
        "name": terme_recherche,
        "page": page_wanted,
        "size": size_wanted
    }
)

if not stations:
    st.warning(
        "Aucune station trouvée. Assurez-vous que le serveur FastAPI est bien démarré ou changez le numéro de page à afficher."
    )
    st.stop()

for i in range(len(stations)):
    statut = client.get(f"/station/{stations[i]["station_id"]}/status")["station_state"]
    if not statut:
        st.warning("Statut indisponible")
    stations[i]["state"] = statut

df_brut = pd.DataFrame(stations)
df = df_brut[["station_id", "name", "address", "capacity", "state"]]
df = df.rename(columns={
    "station_id": "Identifiant",
    "name": "Nom",
    "address": "Adresse",
    "capacity": "Capacité",
    "state": "État"
})
df["Infos de la station"] = df.apply(lambda row: f"/proxy/8501/station_info?station_id={row['Identifiant']}", axis=1)

st.metric("Total des stations affichées", len(df))

st.dataframe(
    df,
    column_config={
        "Infos de la station": st.column_config.LinkColumn(label="Infos", display_text="ℹ️"),
    },
    use_container_width=True,
    hide_index=True,
)
