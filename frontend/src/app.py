import streamlit as st
from utils.env_variables import display_values, load_environment_variables
from utils.log_init import initialize_logs

st.set_page_config(
    page_title="VeloScope",
    page_icon="🚲",
    layout="wide"
)

if "logs_initialized" not in st.session_state:
    initialize_logs("Streamlit App")
    load_environment_variables()
    display_values(include_prefix="BACKEND")
    st.session_state["logs_initialized"] = True

pages = [
    st.Page("pages/home.py", title="Accueil", icon="🏠", default=True),
    st.Page("pages/connexion.py", title="Connexion", icon="🔑"),
    st.Page("pages/inscription.py", title="Inscription", icon="📝"),
    st.Page("pages/admin.py", title="Administrateurs", icon="🛡️"),
    st.Page("pages/station_search.py", title="Rechercher une station", icon="🔍"),
    st.Page("pages/list_stations.py", title="Liste des stations", icon="🚲"),
    st.Page("pages/station_info.py", title="Informations station", icon="📍"),
    st.Page("pages/velo_a_proximite.py", title="Trouver un vélo à proximité", icon="🎯"),
    st.Page("pages/favorite_stations.py", title="Mes favoris", icon="⭐"),
    st.Page("pages/user_info.py", title="Mon profil", icon="👤"),
]

pg = st.navigation(pages)
pg.run()
