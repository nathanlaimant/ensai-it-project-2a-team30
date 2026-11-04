import streamlit as st
from utils.api_client import api_client
from utils.log_init import get_page_logger

st.title("Rechercher une station")

logger = get_page_logger("station_search")

research = st.text_input("Entrer un lieu ou une adresse :", type="search")
stations_searched = api_client.get("/station/", params={"name": research})

if not stations_searched:
    st.warning("Aucun station trouvable")
else:
    st.write("Des stations ont été trouvées")