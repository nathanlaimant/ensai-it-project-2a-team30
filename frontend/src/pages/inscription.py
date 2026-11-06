import requests
import streamlit as st
from utils.api_client import APIClient

PAGE_PRINCIPALE = "app.py"

st.set_page_config(page_title="Inscription - VeloScope", page_icon="🚲")

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

client: APIClient = st.session_state["api_client"]

if st.session_state["token"] is not None:
    st.switch_page(PAGE_PRINCIPALE)

st.title("Inscription")

with st.form("signup_form"):
    new_user = st.text_input("Nom d'utilisateur")
    new_email = st.text_input("Adresse e-mail")
    new_pwd = st.text_input("Mot de passe", type="password")
    btn_signup = st.form_submit_button("Créer mon compte")

if btn_signup:
    if not new_user.strip() or not new_email.strip() or not new_pwd:
        st.warning("Tous les champs sont requis pour l'inscription.")
    else:
        try:
            client.signup(new_user.strip(), new_email.strip(), new_pwd)
            st.success(
                "Compte créé avec succès ! Rendez-vous sur la page "
                "**Connexion** pour vous connecter."
            )
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 409:
                st.error("Ce nom d'utilisateur ou cette adresse e-mail existe déjà.")
            elif status_code == 422:
                st.error("Données d'inscription invalides.")
            else:
                try:
                    detail = str(e.response.json().get("detail", "Erreur serveur."))
                except ValueError:
                    detail = "Erreur serveur."
                st.error(f"Échec ({status_code}) : {detail}")
        except requests.exceptions.RequestException:
            st.error("Le serveur est injoignable. Réessayez plus tard.")
