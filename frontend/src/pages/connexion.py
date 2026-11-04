import requests
import streamlit as st
from utils.api_client import APIClient

PAGE_PRINCIPALE = "app.py"  # fichier lancé avec "streamlit run"

st.set_page_config(page_title="Connexion - VeloScope", page_icon="🚲")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

client: APIClient = st.session_state["api_client"]

# Déjà connecté : retour à la page principale
if st.session_state["token"] is not None:
    st.switch_page(PAGE_PRINCIPALE)

st.title("Connexion")

with st.form("login_form"):
    login_user = st.text_input("Nom d'utilisateur")
    login_pwd = st.text_input("Mot de passe", type="password")
    btn_login = st.form_submit_button("Se connecter")

st.caption("Pas encore de compte ? Rendez-vous sur la page **Inscription** du menu.")

if btn_login:
    if not login_user.strip() or not login_pwd:
        st.warning("Veuillez renseigner votre identifiant et votre mot de passe.")
    else:
        try:
            res = client.login(login_user.strip(), login_pwd)
        except requests.exceptions.RequestException:
            st.error("Le serveur est injoignable. Réessayez plus tard.")
            st.stop()

        if res.status_code == 200:
            data = res.json()
            st.session_state["token"] = data["access_token"]
            st.session_state["username"] = data["username"]
            client.set_token(data["access_token"])
            st.switch_page(PAGE_PRINCIPALE)
        elif res.status_code == 401:
            st.error("Identifiants incorrects.")
        else:
            try:
                detail = str(res.json().get("detail", "Erreur lors de la connexion."))
            except ValueError:
                detail = "Erreur lors de la connexion."
            st.error(f"Échec ({res.status_code}) : {detail}")
