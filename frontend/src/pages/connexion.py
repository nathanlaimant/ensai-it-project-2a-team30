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
            res = client.post(
                "/login",
                data={"username": login_user.strip(), "password": login_pwd},
            )
            st.session_state["token"] = res["access_token"]
            st.session_state["username"] = res["username"]
            st.switch_page(PAGE_PRINCIPALE)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                st.error("L'identifiant ou le mot de passe est incorrect.")
            else:
                try:
                    detail = str(
                        e.response.json().get("detail", "Erreur lors de la connexion.")
                    )
                except ValueError:
                    detail = "Erreur lors de la connexion."
                st.error(f"Échec ({e.response.status_code}) : {detail}")
        except requests.exceptions.RequestException:
            st.error("Le serveur est injoignable. Réessayez plus tard.")
