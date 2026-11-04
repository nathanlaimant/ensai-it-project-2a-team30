import streamlit as st
from utils.env_variables import display_values, load_environment_variables
from utils.log_init import initialize_logs

if "logs_initialized" not in st.session_state:
    initialize_logs("Streamlit App")
    load_environment_variables()
    display_values(include_prefix="BACKEND")
    st.session_state["logs_initialized"] = True

st.switch_page("pages/home.py")