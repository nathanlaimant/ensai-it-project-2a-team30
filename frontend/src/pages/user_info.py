import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger

st.title("Paramètres d'utilisateur")

logger = get_page_logger("user_info")

username = st.session_state["username"]
token = st.session_state["token"]
auth_headers = {"Authorization": f"Bearer {token}"}
logger.info(f"Informations sur {username}")

if not username:
    st.warning("Vous devez être connecté pour accéder à cette fonctionnalité.")
else:
    try:
        user = api_client.get("user/info", headers=auth_headers)
        logger.info(f"Profil de l'utilisateur {user['username']} trouvé !")

        st.write(f"Nom d'utilisateur : {user['username']}")
        new_username = st.text_input("Nouveau nom d'utilisateur :")
        if new_username:
            api_client.put(
                "/user/info",
                data={"username": new_username},
                headers=auth_headers,
            )
            st.session_state["username"] = new_username
            st.success("Nom d'utilisateur mis à jour.")

        st.write(f"E-mail : {user['email']}")
        new_email = st.text_input("Nouvel email :", type="email")
        if new_email:
            api_client.put(
                "/user/info",
                data={"email": new_email},
                headers=auth_headers,
            )
            st.success("Email mis à jour.")

        new_password = st.text_input("Nouveau mot de passe :", type="password")
        if new_password:
            api_client.put(
                "/user/info",
                data={"password": new_password},
                headers=auth_headers,
            )
            st.success("Mot de passe mis à jour.")

    except ValueError:
        logger.error(f"Format de nom d'utilisateur invalide {username}")
        st.error("Format de nom d'utilisateur invalide dans l'URL")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        st.error(f"An error occurred: {e}")
