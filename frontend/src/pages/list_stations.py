import pandas as pd
import streamlit as st

from utils.api_client import APIClient

st.set_page_config(page_title="Stations - VeloScope", page_icon="🚲", layout="wide")

st.title("🚲 Liste des stations VeloScope")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()

client: APIClient = st.session_state["api_client"]

st.sidebar.header("Filtres")
terme_recherche = st.sidebar.text_input(
    "Recherche par nom", placeholder="Ex : République..."
)

size_wanted = st.number_input(label="Nombre de stations à afficher", min_value=1, max_value=100)
page_wanted = st.number_input(label="Afficher la page :", min_value=1, max_value=100)

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

df = pd.DataFrame(stations)

st.metric("Total des stations affichées", len(df))

# 6. Affichage sous forme de tableau interactif
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)
