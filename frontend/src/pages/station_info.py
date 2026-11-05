import pandas as pd
import requests
import streamlit as st
from utils.api_client import APIClient, api_client

st.set_page_config(
    page_title="Informations Station - VeloScope",
    page_icon="🚲",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 1. Initialisation des variables de session
# -----------------------------------------------------------------------------
if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient()
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "selected_station_id" not in st.session_state:
    st.session_state["selected_station_id"] = None

st.title("📍 Informations détaillées de la station")

# -----------------------------------------------------------------------------
# 2. Barre de navigation (Retour en arrière selon les diagrammes d'activité)
# -----------------------------------------------------------------------------
col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])
with col_nav1:
    if st.button("⬅️ Liste des stations"):
        st.switch_page("pages/list_stations.py")
with col_nav2:
    if st.button("🔍 Rechercher"):
        st.switch_page("pages/station_search.py")

st.divider()

# -----------------------------------------------------------------------------
# 3. Sélection de la station (pré-sélectionnée en session ou saisie manuelle)
# -----------------------------------------------------------------------------
station_id = st.session_state.get("selected_station_id")

with st.expander(
    "Changer ou saisir l'identifiant d'une station", expanded=(station_id is None)
):
    with st.form("select_station_form"):
        saisie_id = st.text_input(
            "Identifiant de la station (station_id) :",
            value=station_id if station_id else "",
            placeholder="Ex: 1, station_rennes_01...",
        )
        btn_charger = st.form_submit_button("Afficher les informations")

    if btn_charger and saisie_id.strip():
        st.session_state["selected_station_id"] = saisie_id.strip()
        station_id = saisie_id.strip()
        st.rerun()

if not station_id:
    st.info(
        "Veuillez renseigner un identifiant de station ci-dessus ou choisir une station depuis la page de recherche."
    )
    st.stop()

# -----------------------------------------------------------------------------
# 4. Appels au Backend (StationController)
# -----------------------------------------------------------------------------
# Adapter les chemins ci-dessous si les routes de votre StationController diffèrent
ENDPOINT_INFO = f"/stations/{station_id}"
ENDPOINT_STATUS = f"/stations/{station_id}/status"
ENDPOINT_HOURLY = f"/stations/{station_id}/hourly"

station_info = None
station_status = None
hourly_stats = []

try:
    station_info = api_client.get(ENDPOINT_INFO)
except requests.exceptions.RequestException as e:
    if "404" in str(e):
        st.error(f"Aucune station trouvée avec l'identifiant « {station_id} ».")
    else:
        st.error(f"Erreur lors de la récupération des informations de la station : {e}")
    st.stop()

# Récupération du statut temps réel (StationStatus)
try:
    station_status = api_client.get(ENDPOINT_STATUS)
except requests.exceptions.RequestException:
    station_status = None

# Récupération des statistiques horaires et du score de fiabilité (StationStatusHourly)
try:
    hourly_stats = api_client.get(ENDPOINT_HOURLY, params={"hours": 24})
except requests.exceptions.RequestException:
    hourly_stats = []

# -----------------------------------------------------------------------------
# 5. En-tête de la station & Gestion des Favoris (si utilisateur connecté)
# -----------------------------------------------------------------------------
nom_station = station_info.get("name", f"Station {station_id}")
short_name = station_info.get("short_name")

col_titre, col_fav = st.columns([3, 1])

with col_titre:
    st.header(f"🚲 {nom_station}")
    if short_name:
        st.caption(f"Nom court : **{short_name}** | ID : `{station_id}`")
    else:
        st.caption(f"ID : `{station_id}`")

# Logique du diagramme d'activité 2.3.1 : Ajouter / Retirer des favoris
with col_fav:
    if st.session_state["token"] is not None:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        est_favori = False
        try:
            mes_favoris = api_client.get(
                "/favorites/",
                params={"page": 1, "size": 100},
                headers=headers,
            )
            ids_favoris = [str(f.get("station_id")) for f in mes_favoris]
            est_favori = str(station_id) in ids_favoris
        except requests.exceptions.RequestException:
            pass

        if est_favori:
            if st.button("🗑️ Retirer des favoris", use_container_width=True):
                try:
                    api_client.delete(f"/favorites/{station_id}", headers=headers)
                    st.success("Station retirée des favoris.")
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Impossible de retirer la station : {e}")
        else:
            if st.button(
                "⭐ Ajouter aux favoris", type="primary", use_container_width=True
            ):
                try:
                    # Votre contrôleur favorites utilise @router.get("/{station_id}") pour l'ajout
                    api_client.get(f"/favorites/{station_id}", headers=headers)
                    st.success("Station ajoutée aux favoris !")
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Impossible d'ajouter la station : {e}")
    else:
        st.caption("🔒 *Connectez-vous pour ajouter cette station à vos favoris.*")

# -----------------------------------------------------------------------------
# 6. État en temps réel et Score de fiabilité (KPIs principaux)
# -----------------------------------------------------------------------------
st.subheader("📊 Disponibilité en temps réel et Fiabilité")

# Extraction du dernier score de fiabilité connu (dans hourly_stats ou station_status)
score_fiabilite = None
if isinstance(hourly_stats, list) and len(hourly_stats) > 0:
    score_fiabilite = hourly_stats[-1].get("reliability_score")
elif isinstance(station_info, dict) and "reliability_score" in station_info:
    score_fiabilite = station_info.get("reliability_score")

if station_status:
    etat = station_status.get("station_state", "INCONNU")
    if etat == "FUNCTIONAL":
        st.success("✅ **État de la station : FONCTIONNELLE (FUNCTIONAL)**")
    elif etat == "EMPTY":
        st.warning("⚠️ **État de la station : VIDE (EMPTY) — Aucun vélo disponible**")
    elif etat == "FULL":
        st.warning("⚠️ **État de la station : SATURÉE (FULL) — Aucune place libre**")
    else:
        st.info(f"ℹ️ **État de la station : {etat}**")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(
        "🚲 Vélos disponibles",
        station_status.get("num_bikes_available", "N/A"),
        delta=f"{station_status.get('num_bikes_disabled', 0)} hors service",
        delta_color="off",
    )
    kpi2.metric(
        "🅿️ Places libres (Docks)",
        station_status.get("num_docks_available", "N/A"),
        delta=f"{station_status.get('num_docks_disabled', 0)} hors service",
        delta_color="off",
    )
    kpi3.metric(
        "⚙️ Capacité opérationnelle",
        station_status.get("operational_capacity", station_info.get("capacity", "N/A")),
    )
    kpi4.metric(
        "🎯 Score de fiabilité",
        f"{round(score_fiabilite * 100, 1)} %"
        if isinstance(score_fiabilite, (int, float)) and score_fiabilite <= 1
        else (
            round(score_fiabilite, 2) if score_fiabilite is not None else "Non calculé"
        ),
    )

    # Détails techniques du statut en temps réel
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    col_stat1.write(
        f"**Installée :** {'Oui ✅' if station_status.get('is_installed') else 'Non ❌'}"
    )
    col_stat2.write(
        f"**Location active :** {'Oui ✅' if station_status.get('is_renting') else 'Non ❌'}"
    )
    col_stat3.write(
        f"**Restitution active :** {'Oui ✅' if station_status.get('is_returning') else 'Non ❌'}"
    )
    col_stat4.write(
        f"**Dernier relevé :** `{station_status.get('last_reported', 'N/A')}`"
    )
else:
    st.info(
        "Les données de statut en temps réel (`StationStatus`) ne sont pas disponibles pour cette station."
    )

st.divider()

# -----------------------------------------------------------------------------
# 7. Caractéristiques statiques de la station (StationInformation)
# -----------------------------------------------------------------------------
st.subheader("🗂️ Caractéristiques de la station")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown(f"* **Adresse :** {station_info.get('address') or 'Non renseignée'}")
    st.markdown(
        f"* **Capacité théorique :** {station_info.get('capacity', 'Non renseignée')} places"
    )
    st.markdown(
        f"* **Téléphone de contact :** {station_info.get('contact_phone') or 'Non renseigné'}"
    )

with col_info2:
    est_virtuelle = "Oui" if station_info.get("is_virtual_station") else "Non"
    est_recharge = "Oui ⚡" if station_info.get("is_charging_station") else "Non"
    st.markdown(f"* **Station virtuelle :** {est_virtuelle}")
    st.markdown(f"* **Borne de recharge électrique :** {est_recharge}")
    st.markdown(
        f"* **Coordonnées GPS :** `{station_info.get('lat', 'N/A')}, {station_info.get('lon', 'N/A')}`"
    )

# -----------------------------------------------------------------------------
# 8. Historique horaire et analyse de fiabilité (StationStatusHourly)
# -----------------------------------------------------------------------------
if isinstance(hourly_stats, list) and len(hourly_stats) > 0:
    st.divider()
    st.subheader("📈 Historique horaire et métriques de fiabilité")

    df_hourly = pd.DataFrame(hourly_stats)

    # Renommage lisible des colonnes issues de la table station_status_hourly
    colonnes_traduction = {
        "bucket_hour": "Tranche horaire",
        "reliability_score": "Score de fiabilité",
        "avg_num_bikes_available": "Moy. vélos dispo",
        "avg_num_docks_available": "Moy. places libres",
        "avg_operational_capacity": "Capacité op. moyenne",
        "empty_events_cnt": "Pénuries (0 vélo)",
        "full_events_cnt": "Saturations (0 place)",
        "empty_duration_sec": "Durée vide (s)",
        "full_duration_sec": "Durée saturée (s)",
    }

    colonnes_presentes = [c for c in colonnes_traduction if c in df_hourly.columns]
    df_affichage = df_hourly[colonnes_presentes].rename(columns=colonnes_traduction)

    st.dataframe(df_affichage, use_container_width=True, hide_index=True)
