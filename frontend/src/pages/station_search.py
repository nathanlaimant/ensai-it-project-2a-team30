import streamlit as st
from utils.api_client import APIClient
from utils.log_init import get_page_logger

st.title("Rechercher une station")

logger = get_page_logger("station_search")

st.text_input("Entrer un lieu ou une adresse :", type="search")
