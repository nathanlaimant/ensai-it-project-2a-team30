import pandas as pd
import streamlit as st
from utils.api_client import APIClient

st.set_page_config(page_title="Stations - VeloScope", page_icon="🚲", layout="wide")

st.title("🚲 Liste des stations VeloScope")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()

client: APIClient = st.session_state["api_client"]


@st.cache_data(ttl=60)
def charger_stations() -> list[dict]:
    reponse = client.get_stations()
    if reponse.status_code == 200:
        return reponse.json()
    return []


stations = charger_stations()

if not stations:
    st.warning(
        "Aucune station trouvée. Assurez-vous que le serveur FastAPI est bien démarré."
    )
    st.stop()

# 3. Conversion des données brutes en DataFrame Pandas
df = pd.DataFrame(stations)

# 4. Barre latérale : Recherche textuelle rapide
st.sidebar.header("Filtres")
terme_recherche = st.sidebar.text_input(
    "Recherche par nom", placeholder="Ex : République..."
)

df_filtre = df.copy()

if terme_recherche.strip() and "name" in df_filtre.columns:
    df_filtre = df_filtre[
        df_filtre["name"].str.contains(terme_recherche, case=False, na=False)
    ]

# 5. Métrique récapitulative
st.metric("Total des stations affichées", len(df_filtre))

# 6. Affichage sous forme de tableau interactif
st.dataframe(
    df_filtre,
    use_container_width=True,
    hide_index=True,
)
