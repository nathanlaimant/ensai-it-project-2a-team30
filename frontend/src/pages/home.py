import streamlit as st
from src.utils.api_client import APIClient

st.set_page_config(page_title="Compte - VeloScope", page_icon="🚲")
st.title("Espace Utilisateur")

# 1. Initialisation des états de session
if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()

if "token" not in st.session_state:
    st.session_state["token"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

client: APIClient = st.session_state["api_client"]

# 2. Cas où l'utilisateur est connecté
if st.session_state["token"] is not None:
    st.success(f"Bienvenue, **{st.session_state['username']}** !")

    # Optionnel : bouton pour voir les infos complètes de l'utilisateur
    if st.button("Afficher mon profil"):
        res = client.get_user_info()
        if res.status_code == 200:
            st.json(res.json())
        else:
            st.error("Impossible de récupérer les détails du profil.")

    # Bouton de déconnexion
    if st.button("Se déconnecter", type="primary"):
        client.logout()
        client.clear_token()
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.rerun()

# 3. Cas où l'utilisateur est déconnecté : formulaires
else:
    tab_login, tab_signup = st.tabs(["Connexion", "Inscription"])

    # --- Onglet Connexion ---
    with tab_login:
        with st.form("login_form"):
            login_user = st.text_input("Nom d'utilisateur")
            login_pwd = st.text_input("Mot de passe", type="password")
            btn_login = st.form_submit_button("Se connecter")

        if btn_login:
            if not login_user.strip() or not login_pwd:
                st.warning(
                    "Veuillez renseigner votre identifiant et votre mot de passe."
                )
            else:
                res = client.login(login_user.strip(), login_pwd)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["username"] = data["username"]
                    client.set_token(data["access_token"])
                    st.success("Connexion réussie !")
                    st.rerun()
                elif res.status_code == 401:
                    st.error("Identifiants incorrects.")
                else:
                    detail = res.json().get("detail", "Erreur lors de la connexion.")
                    st.error(f"Échec ({res.status_code}) : {detail}")

    # --- Onglet Inscription ---
    with tab_signup:
        with st.form("signup_form"):
            new_user = st.text_input("Nom d'utilisateur")
            new_email = st.text_input("Adresse e-mail")
            new_pwd = st.text_input("Mot de passe", type="password")
            btn_signup = st.form_submit_button("Créer mon compte")

        if btn_signup:
            if not new_user.strip() or not new_email.strip() or not new_pwd:
                st.warning("Tous les champs sont requis pour l'inscription.")
            else:
                res = client.signup(new_user.strip(), new_email.strip(), new_pwd)
                if res.status_code == 200:
                    st.success(
                        "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
                    )
                elif res.status_code == 409:
                    st.error(
                        "Ce nom d'utilisateur ou cette adresse e-mail existe déjà."
                    )
                elif res.status_code == 422:
                    st.error("Données d'inscription invalides.")
                else:
                    detail = res.json().get("detail", "Erreur serveur.")
                    st.error(f"Échec ({res.status_code}) : {detail}")
