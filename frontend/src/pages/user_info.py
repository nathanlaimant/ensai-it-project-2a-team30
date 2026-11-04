from datetime import datetime

import streamlit as st
from utils.api_client import api_client
from utils.log_init import get_page_logger
from utils.security import hash_password

st.title("Paramètres d'utilisateur")

logger = get_page_logger("user_info")

query_params = st.query_params
username = st.session_state["username"]
token = st.session_state["token"]
logger.info(f"Informations sur {username}")

if not username:
    st.warning("Utilisateur introuvable")
else:
    try:
        user_res = api_client.get("user/info", headers={"Authorization": f"Bearer {token}"})

        user = user_res
        logger.info(f"Profil de l'utilisateur {user["username"]} trouvé !")

        st.write(f"Nom d'utilisateur : {user["username"]}")
        new_username = st.text_input("Nouveau nom d'utilisateur :")
        if new_username:
            new_username = api_client.post("/user/info", json={"username": new_username})
            new_upadate = api_client.post("/user/info", json={"updated_at": datetime.now})

        st.write(f"E-mail : {user["email"]}")
        new_email = st.text_input("Nouvel email :", type="email")
        if new_email:
            new_email = api_client.post("/user/info", json={"email": new_email})
            new_upadate = api_client.post("/user/info", json={"updated_at": datetime.now})
            
        new_password = st.text_input("Nouveau mot de passe :", type="password")
        if new_password:
            new_password = api_client.post("/user/info", json={"password_hashed": hash_password(new_password)})
            new_upadate = api_client.post("/user/info", json={"updated_at": datetime.now})
            
    except ValueError:
        logger.error(f"Format de nom d'utilisateur invalide {username}")
        st.error("Format de nom d'utilisateur invalide dans l'URL")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        st.error(f"An error occurred: {e}")