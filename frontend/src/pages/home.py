
import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="VeloScope",
    page_icon="🚲",
    layout="wide"
)

st.title("🚲 Bienvenue sur VeloScope")

st.write(
    "Bienvenue sur VeloScope, votre application de recherche "
    "et de consultation des stations de vélos."
)

st.info(
    "Utilisez le menu latéral pour accéder aux différentes "
    "fonctionnalités de l'application."
)

if st.session_state.get("token") is not None:

    st.success(
        f"Vous êtes connecté en tant que "
        f"{st.session_state.get('username', 'utilisateur')}."
    )

    if st.button("🚪 Se déconnecter", use_container_width=True):

        try:
            client = st.session_state.get("api_client")

            if client is None:
                client = APIClient()

            client.logout(st.session_state["token"])

            st.session_state["token"] = None
            st.session_state["username"] = None

            st.success("Vous avez été déconnecté avec succès.")

            st.switch_page("app.py")

        except Exception as e:
            st.error(f"Erreur lors de la déconnexion : {e}")

else:
    st.info("Vous n'êtes pas connecté.")
    if st.button("Se connecter"):
        st.switch_page("pages/connexion.py")
