from datetime import datetime

import pandas as pd
import streamlit as st
from utils.api_client import APIClient
from utils.log_init import get_page_logger
from utils.security import hash_password

st.title("Paramètres d'utilisateur")

logger = get_page_logger("player_stats")

query_params = st.query_params
user_id = query_params.get("user_id")
logger.info(f"Informations sur l'utilisateur {user_id}")

if not user_id:
    st.warning("Utilisateur introuvable")
else:
    try:
        user_id = int(user_id)
        user_res = APIClient().get_user_info()

        if user_res["status_code"] == 200:
            user = user_res["data"]
            logger.info(f"Profil de l'utilisateur {user["username"]} trouvé !")

            st.write(f"Nom d'utilisateur : {user["username"]}")
            new_username = st.text_input("Nouveau nom d'utilisateur :")
            if new_username:
                user["username"] = new_username # Update dans la DAO
                user["updated_at"] = datetime.now

            st.write(f"E-mail : {user["email"]}")
            new_email = st.text_input("Nouvel email :", type="email")
            if new_email:
                user["email"] = new_email
                user["updated_at"] = datetime.now
            
            st.write(f"Mot de passe : {user["password_hashed"]}")
            new_password = st.text_input("Nouveau mot de passe :", type="password")
            if new_password:
                user["password_hashed"] = hash_password(new_password)
                user["updated_at"] = datetime.now
            
    except ValueError:
        logger.error(f"Format d'identifiant invalide {user_id}")
        st.error("Format d'identifiant invalide dans l'URL")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        st.error(f"An error occurred: {e}")