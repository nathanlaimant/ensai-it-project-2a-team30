import pandas as pd
import requests
import streamlit as st

from utils.api_client import api_client

PAGE_CONNEXION = "pages/connexion.py"  # à adapter au nom exact de ton fichier

st.set_page_config(
    page_title="Administration - VeloScope", page_icon="🛡️", layout="wide"
)

for cle, defaut in {
    "token": None,
    "username": None,
    "admin_page": 1,
    "admin_filtres": {},
}.items():
    if cle not in st.session_state:
        st.session_state[cle] = defaut


def message_erreur(e: requests.exceptions.RequestException) -> str:
    """Traduit une erreur de requête en message lisible."""
    if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
        code = e.response.status_code
        try:
            corps = e.response.json()
            detail = corps.get("detail") if isinstance(corps, dict) else None
        except ValueError:
            detail = None
        if code == 401:
            return "Session expirée ou invalide. Reconnectez-vous."
        if code == 403:
            return "Accès refusé : droits administrateur requis."
        if code == 422:
            return "Critères invalides (l'e-mail doit être une adresse complète)."
        return f"Erreur {code} : {detail or 'erreur serveur'}"
    return "Le serveur est injoignable. Réessayez plus tard."


def executer(action, message_ok: str, type_ok: str = "success") -> None:
    """Exécute une action admin, puis recharge la page en affichant le résultat."""
    try:
        action()
    except requests.exceptions.RequestException as e:
        st.error(message_erreur(e))
        return
    st.session_state["admin_flash"] = (type_ok, message_ok)
    st.rerun()


# --- 1. Connecté ? ---------------------------------------------------------
if st.session_state["token"] is None:
    st.warning("Vous devez être connecté pour accéder à cette page.")
    if st.button("Aller à la page de connexion"):
        st.switch_page(PAGE_CONNEXION)
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# --- 2. Administrateur ? (contrôle d'affichage, la vraie sécurité est le backend)
try:
    profil = api_client.get("/user/info", headers=headers)
except requests.exceptions.RequestException as e:
    st.error(message_erreur(e))
    st.stop()

if profil.get("role") != "ADMIN":
    st.error("Accès refusé : cette page est réservée aux administrateurs.")
    st.stop()

mon_id = profil.get("user_id")

st.title("🛡️ Administration - Gestion des utilisateurs")

flash = st.session_state.pop("admin_flash", None)
if flash:
    getattr(st, flash[0])(flash[1])

# --- 3. Filtres ------------------------------------------------------------
with st.form("filtres_form"):
    c1, c2, c3, c4, c5 = st.columns(5)
    f_username = c1.text_input("Nom d'utilisateur")
    f_email = c2.text_input("E-mail (adresse complète)")
    f_role = c3.selectbox("Rôle", ["Tous", "ADMIN", "USER"])
    f_statut = c4.selectbox("Statut", ["Tous", "Actifs", "Inactifs"])
    f_size = c5.selectbox("Par page", [10, 25, 50, 100])
    appliquer = st.form_submit_button("Filtrer")

if appliquer:
    filtres: dict = {"size": f_size}
    if f_username.strip():
        filtres["username"] = f_username.strip()
    if f_email.strip():
        filtres["email"] = f_email.strip()
    if f_role != "Tous":
        filtres["role"] = f_role
    if f_statut != "Tous":
        filtres["is_active"] = f_statut == "Actifs"
    st.session_state["admin_filtres"] = filtres
    st.session_state["admin_page"] = 1

page = st.session_state["admin_page"]
payload = {"size": 10, **st.session_state["admin_filtres"], "page": page}
taille = payload["size"]

# --- 4. Récupération de la liste ------------------------------------------
try:
    users = api_client.post("/admin/users", data=payload, headers=headers)
except requests.exceptions.RequestException as e:
    st.error(message_erreur(e))
    st.stop()

if not users:
    st.info("Aucun utilisateur ne correspond à ces critères.")
    if page > 1 and st.button("Revenir à la première page"):
        st.session_state["admin_page"] = 1
        st.rerun()
    st.stop()

# --- 5. Tableau et pagination ---------------------------------------------
df = pd.DataFrame(users)
colonnes = [
    c
    for c in ["user_id", "username", "email", "role", "is_active", "created_at"]
    if c in df.columns
]
df = df[colonnes]
if "created_at" in df.columns:
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce").dt.strftime(
        "%d/%m/%Y %H:%M"
    )

st.metric("Utilisateurs affichés sur cette page", len(df))
st.dataframe(
    df.rename(
        columns={
            "user_id": "ID",
            "username": "Nom d'utilisateur",
            "email": "E-mail",
            "role": "Rôle",
            "is_active": "Actif",
            "created_at": "Créé le",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

nav1, nav2, nav3 = st.columns([1, 1, 6])
if nav1.button("⬅️ Précédent", disabled=page <= 1):
    st.session_state["admin_page"] = page - 1
    st.rerun()
if nav2.button("Suivant ➡️", disabled=len(users) < taille):
    st.session_state["admin_page"] = page + 1
    st.rerun()
nav3.write(f"Page {page}")

st.divider()

# --- 6. Actions sur un compte ---------------------------------------------
st.subheader("⚙️ Actions sur un compte")

options = {u["user_id"]: u for u in users}
choix = st.selectbox(
    "Sélectionner un utilisateur :",
    options=list(options.keys()),
    format_func=lambda uid: (
        f"{options[uid]['username']} (ID {uid}, "
        f"{'actif' if options[uid]['is_active'] else 'inactif'})"
    ),
)
cible = options[choix]
nom = cible["username"]
est_moi = choix == mon_id

if est_moi:
    st.info("Vous ne pouvez pas modifier votre propre compte depuis cette page.")

col_a, col_d = st.columns(2)
if col_a.button(
    "✅ Activer le compte",
    use_container_width=True,
    disabled=est_moi or cible["is_active"],
):
    executer(
        lambda: api_client.post(f"/admin/users/activate/{choix}", headers=headers),
        f"Le compte « {nom} » a été activé.",
    )

if col_d.button(
    "🚫 Désactiver le compte",
    use_container_width=True,
    disabled=est_moi or not cible["is_active"],
):
    executer(
        lambda: api_client.post(f"/admin/users/deactivate/{choix}", headers=headers),
        f"Le compte « {nom} » a été désactivé.",
        "warning",
    )

st.divider()
st.subheader("🗑️ Suppression définitive")
st.caption("Irréversible : le compte et ses stations favorites sont supprimés.")

confirme = st.checkbox(
    f"Je confirme la suppression définitive de « {nom} »", key=f"confirm_{choix}"
)
if st.button("Supprimer le compte", type="primary", disabled=est_moi or not confirme):
    executer(
        lambda: api_client.delete(f"/admin/users/{choix}", headers=headers),
        f"Le compte « {nom} » a été supprimé.",
    )
