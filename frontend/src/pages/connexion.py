import requests
import streamlit as st
from utils.api_client import APIClient, api_client
from utils.security import hash_password

PAGE_PRINCIPALE = "app.py"  # fichier lancé avec "streamlit run"

st.set_page_config(page_title="Connexion - VeloScope", page_icon="🚲")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

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
            res = api_client.post("/login", data={"username": login_user, "password": login_pwd})
        except requests.exceptions.RequestException as e:
            if "401" in str(e):
                st.error("Identifiants incorrects.")
            else:
                st.error("Le serveur est injoignable. Réessayez plus tard.")
            st.stop()

        st.write(str(res))
        st.session_state["token"] = res["access_token"]
        st.session_state["username"] = res["username"]
        # api_client.set_token(res["access_token"])
        st.switch_page(PAGE_PRINCIPALE)
            
        try:
            detail = str(res.json().get("detail", "Erreur lors de la connexion."))
        except ValueError:
            detail = "Erreur lors de la connexion."
        st.error(f"Échec ({res.status_code}) : {detail}")
