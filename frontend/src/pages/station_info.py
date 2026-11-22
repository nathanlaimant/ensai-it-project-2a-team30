from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from utils.api_client import APIClient, api_client
from utils.log_init import get_page_logger

st.set_page_config(
    page_title="Informations Station - VeloScope",
    page_icon="🚲",
    layout="wide",
)

logger = get_page_logger("station_info")

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
# 2. Barre de navigation
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
# 3. Sélection de la station (URL en priorité, puis session_state)
# -----------------------------------------------------------------------------
station_id = st.query_params.get("station_id")

if not station_id and st.session_state.get("selected_station_id"):
    station_id = st.session_state.get("selected_station_id")
    st.query_params["station_id"] = station_id

if not station_id:
    with st.expander("Saisir l'identifiant d'une station", expanded=True):
        with st.form("select_station_form"):
            saisie_id = st.text_input(
                "Identifiant de la station (station_id) :",
                value="",
                placeholder="Ex: 1, station_rennes_01...",
            )
            btn_charger = st.form_submit_button("Afficher les informations")

        if btn_charger and saisie_id.strip():
            station_id = saisie_id.strip()
            st.session_state["selected_station_id"] = station_id
            st.query_params["station_id"] = station_id
            st.rerun()

    st.info(
        "Veuillez renseigner un identifiant de station ci-dessus ou choisir une station depuis la page de recherche."
    )
    st.stop()
else:
    with st.expander("Changer de station", expanded=False):
        with st.form("select_station_form"):
            saisie_id = st.text_input(
                label="Identifiant de la station (station_id) :",
                placeholder="Ex: 1, 1234...",
            )
            saisie_nom = st.text_input(
                label="Nom de la station",
                type="search",
                autocomplete="search",
                placeholder="Ex: Gare, Mairie...",
            )
            btn_charger = st.form_submit_button("Afficher les informations")

        if btn_charger and (saisie_id.strip() or saisie_nom.strip()):
            if saisie_id.strip():
                station_id = saisie_id.strip()
                st.session_state["selected_station_id"] = station_id
                st.query_params["station_id"] = station_id
                st.info(f"Résultat unique pour la recherche : « {saisie_id} »")
                st.rerun()
            else:
                nom_recherche = saisie_nom.strip()
                try:
                    resultats = api_client.post("/station", {"name": nom_recherche})
                except requests.exceptions.RequestException as e:
                    st.error(f"Erreur lors de la recherche de la station : {e}")
                    st.stop()

                if not resultats:
                    st.error(f"Aucune station trouvée avec le nom « {nom_recherche} ».")
                elif len(resultats) > 1:
                    st.session_state["in_search"] = nom_recherche
                    st.switch_page("pages/station_search.py")
                else:
                    station_id = str(resultats[0]["station_id"])
                    st.session_state["in_search"] = nom_recherche
                    st.session_state["selected_station_id"] = station_id
                    st.query_params["station_id"] = station_id
                    st.info(f"Résultat unique pour la recherche : « {nom_recherche} »")
                    st.rerun()


if st.session_state.get("in_search"):
    st.info(f"Résultat pour la recherche : « {st.session_state['in_search']} »")

ENDPOINT_INFO = f"/station/{station_id}"
ENDPOINT_STATUS = f"/station/{station_id}/status"
ENDPOINT_HOURLY = f"/station/{station_id}/history"

station_info = None
station_status = None

try:
    station_info = api_client.get(ENDPOINT_INFO)
except requests.exceptions.RequestException as e:
    if "404" in str(e):
        st.error(f"Aucune station trouvée avec l'identifiant « {station_id} ».")
    else:
        st.error(f"Erreur lors de la récupération des informations de la station : {e}")
    st.stop()

try:
    station_status = api_client.get(ENDPOINT_STATUS)
except requests.exceptions.RequestException:
    station_status = None

nom_station = station_info.get("name", f"Station {station_id}")
short_name = station_info.get("short_name")

col_titre, col_fav = st.columns([3, 1])

with col_titre:
    st.header(f"🚲 {nom_station}")
    if short_name:
        st.caption(f"Nom court : **{short_name}** | ID : `{station_id}`")
    else:
        st.caption(f"ID : `{station_id}`")

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
                    api_client.get(f"/favorites/{station_id}", headers=headers)
                    st.success("Station ajoutée aux favoris !")
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Impossible d'ajouter la station : {e}")
    else:
        st.caption("🔒 *Connectez-vous pour ajouter cette station à vos favoris.*")

st.subheader("📊 Disponibilité en temps réel et Fiabilité")

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

    if station_status.get("full_ratio") is not None:
        taux_remplissage = float(station_status["full_ratio"])
    else:
        cap_op = station_status.get("operational_capacity") or 0
        docks_dispo = station_status.get("num_docks_available") or 0
        taux_remplissage = (100 * docks_dispo / cap_op) if cap_op > 0 else 0

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
        "Taux de remplissage :",
        f"{int(taux_remplissage)} %",
    )

    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric(
        "🎯 Score de fiabilité",
        (
            f"{int(station_status.get('reliability_score'))} %"
            if station_status.get("reliability_score") is not None
            else "Non calculé"
        ),
    )
    if station_status.get("last_reported"):
        last_rep = (
            str(station_status["last_reported"]).replace("T", " ").replace("Z", "")
        )
        try:
            dt_reported = datetime.strptime(last_rep, "%Y-%m-%d %H:%M:%S")
            periode = datetime.now() - dt_reported
            mins = "minute" if periode.seconds // 60 <= 1 else "minutes"
            col_stat2.write(
                f"**Dernier relevé :** Il y a `{periode.seconds // 60} {mins}`."
            )
        except Exception:
            col_stat2.write(f"**Dernier relevé :** `{last_rep}`")
    else:
        col_stat2.write("**Dernier relevé :** `N/A`")
else:
    st.info(
        "Les données de statut en temps réel (`StationStatus`) ne sont pas disponibles pour cette station."
    )

st.divider()

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

st.divider()
st.subheader("📈 Historique horaire et métriques de fiabilité")

periode_options = {
    "Dans les 30 derniers jours": "30j",
    "Dans les 7 derniers jours": "7j",
    "Dans les dernières 24 heures": "24h",
    "Dans la dernière heure": "1h",
}

col_sel_p, _ = st.columns([2, 2])
with col_sel_p:
    periode_voulue = st.selectbox(
        label="Période d'observation",
        options=list(periode_options.keys()),
        index=0,
        help="Choisissez la fenêtre temporelle d'observation pour analyser la disponibilité et la fiabilité.",
    )

periode_param = periode_options[periode_voulue]

try:
    hourly_stats = api_client.get(ENDPOINT_HOURLY, params={"period": periode_param})
except Exception as e:
    hourly_stats = []
    logger.error(f"Erreur lors de la récupération de l'historique : {e}")
    st.warning(f"Erreur lors de la récupération des données d'historique : {e}")

if not hourly_stats:
    st.info("Aucun historique disponible pour cette période.")
else:
    df_raw = pd.DataFrame(hourly_stats)

    # 1. Normalisation de la colonne temporelle
    time_col = None
    for c in ["last_reported", "bucket_hour", "stat_date"]:
        if c in df_raw.columns:
            time_col = c
            break

    if time_col:
        df_raw["datetime"] = pd.to_datetime(df_raw[time_col], errors="coerce")
        df_raw = (
            df_raw.dropna(subset=["datetime"])
            .sort_values("datetime")
            .reset_index(drop=True)
        )
        if periode_param in ["7j", "30j"]:
            df_raw["Période"] = df_raw["datetime"].dt.strftime("%d/%m/%Y")
        else:
            df_raw["Période"] = df_raw["datetime"].dt.strftime("%d/%m/%Y %H:%M")
    else:
        df_raw["Période"] = [f"Relevé {i + 1}" for i in range(len(df_raw))]

    # 2. Normalisation des noms de colonnes et types
    if (
        "num_bikes_available" not in df_raw.columns
        and "avg_num_bikes_available" in df_raw.columns
    ):
        df_raw["num_bikes_available"] = df_raw["avg_num_bikes_available"]
    if (
        "num_docks_available" not in df_raw.columns
        and "avg_num_docks_available" in df_raw.columns
    ):
        df_raw["num_docks_available"] = df_raw["avg_num_docks_available"]
    if (
        "operational_capacity" not in df_raw.columns
        and "avg_operational_capacity" in df_raw.columns
    ):
        df_raw["operational_capacity"] = df_raw["avg_operational_capacity"]
    if (
        "reliability_score" not in df_raw.columns
        and "avg_reliability_score" in df_raw.columns
    ):
        df_raw["reliability_score"] = df_raw["avg_reliability_score"]

    num_cols = [
        "num_bikes_available",
        "num_docks_available",
        "operational_capacity",
        "reliability_score",
        "full_ratio",
        "full_duration_ratio",
        "avg_full_duration",
        "empty_duration_ratio",
        "avg_empty_duration",
    ]
    for col in num_cols:
        if col in df_raw.columns:
            df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    if (
        "full_ratio" not in df_raw.columns
        and "num_bikes_available" in df_raw.columns
        and "operational_capacity" in df_raw.columns
    ):
        df_raw["full_ratio"] = df_raw.apply(
            lambda r: (
                min(r["num_bikes_available"] / r["operational_capacity"], 1.0)
                if r["operational_capacity"] and r["operational_capacity"] > 0
                else 0.0
            ),
            axis=1,
        )

    # 3. Synthèse sous forme de KPIs (Métriques globales sur la période)
    st.markdown("##### 📌 Synthèse sur la période sélectionnée")
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    has_rel = (
        "reliability_score" in df_raw.columns
        and df_raw["reliability_score"].notna().any()
    )
    if has_rel:
        mean_score = float(df_raw["reliability_score"].dropna().mean())
        label_score = (
            "Score de fiabilité"
            if periode_param == "1h"
            else "Score de fiabilité moyen"
        )
        col_kpi1.metric(
            label_score,
            f"{mean_score:.1f} %",
        )
    else:
        col_kpi1.metric(
            (
                "Score de fiabilité"
                if periode_param == "1h"
                else "Score de fiabilité moyen"
            ),
            "N/A",
        )

    if (
        "num_bikes_available" in df_raw.columns
        and df_raw["num_bikes_available"].notna().any()
    ):
        mean_bikes = float(df_raw["num_bikes_available"].dropna().mean())
        col_kpi2.metric("Moy. vélos disponibles", f"{mean_bikes:.1f}")
    else:
        col_kpi2.metric("Moy. vélos disponibles", "N/A")

    if (
        "num_docks_available" in df_raw.columns
        and df_raw["num_docks_available"].notna().any()
    ):
        mean_docks = float(df_raw["num_docks_available"].dropna().mean())
        col_kpi3.metric("Moy. places libres", f"{mean_docks:.1f}")
    else:
        col_kpi3.metric("Moy. places libres", "N/A")

    if "full_ratio" in df_raw.columns and df_raw["full_ratio"].notna().any():
        mean_fill = float(df_raw["full_ratio"].dropna().mean()) * 100
        col_kpi4.metric("Taux de remplissage moyen", f"{mean_fill:.1f} %")
    else:
        col_kpi4.metric("Taux de remplissage moyen", "N/A")

    has_durations = (
        "empty_duration_ratio" in df_raw.columns
        and df_raw["empty_duration_ratio"].notna().any()
    ) or (
        "full_duration_ratio" in df_raw.columns
        and df_raw["full_duration_ratio"].notna().any()
    )

    if has_durations:
        col_ten1, col_ten2, col_ten3, col_ten4 = st.columns(4)
        if (
            "empty_duration_ratio" in df_raw.columns
            and df_raw["empty_duration_ratio"].notna().any()
        ):
            empty_pct = float(df_raw["empty_duration_ratio"].dropna().mean()) * 100
            col_ten1.metric("Temps vide (pénurie)", f"{empty_pct:.1f} %")
        if (
            "avg_empty_duration" in df_raw.columns
            and df_raw["avg_empty_duration"].notna().any()
        ):
            avg_empty_s = float(df_raw["avg_empty_duration"].dropna().mean())
            dur_text = (
                f"{avg_empty_s / 60:.1f} min"
                if avg_empty_s >= 60
                else f"{int(avg_empty_s)} s"
            )
            col_ten2.metric("Durée moy. pénurie", dur_text)
        if (
            "full_duration_ratio" in df_raw.columns
            and df_raw["full_duration_ratio"].notna().any()
        ):
            full_pct = float(df_raw["full_duration_ratio"].dropna().mean()) * 100
            col_ten3.metric("Temps saturé (plein)", f"{full_pct:.1f} %")
        if (
            "avg_full_duration" in df_raw.columns
            and df_raw["avg_full_duration"].notna().any()
        ):
            avg_full_s = float(df_raw["avg_full_duration"].dropna().mean())
            dur_full_text = (
                f"{avg_full_s / 60:.1f} min"
                if avg_full_s >= 60
                else f"{int(avg_full_s)} s"
            )
            col_ten4.metric("Durée moy. saturation", dur_full_text)

    st.write("")

    # 4. Organisation en onglets : Graphiques, Tableau complet
    tab_graphs, tab_table = st.tabs(
        [
            "📊 Graphiques temporels",
            "📋 Tableau complet des relevés",
        ]
    )

    with tab_graphs:
        st.markdown("###### 🚲 Disponibilité des vélos et places libres")
        cols_disp = []
        if "num_bikes_available" in df_raw.columns:
            df_raw["Vélos disponibles"] = df_raw["num_bikes_available"]
            cols_disp.append("Vélos disponibles")
        if "num_docks_available" in df_raw.columns:
            df_raw["Places libres"] = df_raw["num_docks_available"]
            cols_disp.append("Places libres")

        if cols_disp:
            st.line_chart(
                df_raw,
                x="Période",
                y=cols_disp,
                color=["#2E7D32", "#1976D2"][: len(cols_disp)],
            )

        cols_score = []
        if (
            periode_param != "1h"
            and "reliability_score" in df_raw.columns
            and df_raw["reliability_score"].notna().any()
        ):
            df_raw["Score de fiabilité (%)"] = df_raw["reliability_score"]
            cols_score.append("Score de fiabilité (%)")
        if "full_ratio" in df_raw.columns and df_raw["full_ratio"].notna().any():
            df_raw["Taux de remplissage (%)"] = (df_raw["full_ratio"] * 100).round(1)
            cols_score.append("Taux de remplissage (%)")

        if cols_score:
            titre_score = (
                "###### 🎯 Score de fiabilité et Taux de remplissage"
                if "Score de fiabilité (%)" in cols_score
                else "###### 🎯 Taux de remplissage"
            )
            st.markdown(titre_score)
            st.line_chart(
                df_raw,
                x="Période",
                y=cols_score,
                color=["#FF9800", "#9C27B0"][: len(cols_score)],
            )

        if has_durations:
            st.markdown("###### ⚠️ Proportion du temps en pénurie ou saturation")
            tension_cols = []
            if (
                "empty_duration_ratio" in df_raw.columns
                and df_raw["empty_duration_ratio"].notna().any()
            ):
                df_raw["Temps vide (%)"] = (df_raw["empty_duration_ratio"] * 100).round(
                    1
                )
                tension_cols.append("Temps vide (%)")
            if (
                "full_duration_ratio" in df_raw.columns
                and df_raw["full_duration_ratio"].notna().any()
            ):
                df_raw["Temps saturé (%)"] = (
                    df_raw["full_duration_ratio"] * 100
                ).round(1)
                tension_cols.append("Temps saturé (%)")

            if tension_cols:
                st.area_chart(
                    df_raw,
                    x="Période",
                    y=tension_cols,
                    color=["#D32F2F", "#F57C00"][: len(tension_cols)],
                )

    with tab_table:
        df_table = pd.DataFrame()
        df_table["Période"] = df_raw["Période"]

        if "station_state" in df_raw.columns and df_raw["station_state"].notna().any():
            state_map = {
                "FUNCTIONAL": "🟢 Fonctionnelle",
                "EMPTY": "🔴 Vide",
                "FULL": "🟠 Saturée",
            }
            df_table["État"] = df_raw["station_state"].map(
                lambda s: state_map.get(s, s)
            )

        if (
            "reliability_score" in df_raw.columns
            and df_raw["reliability_score"].notna().any()
        ):
            df_table["Fiabilité (%)"] = df_raw["reliability_score"].round(1)

        if "num_bikes_available" in df_raw.columns:
            df_table["Vélos dispo"] = df_raw["num_bikes_available"].round(1)

        if "num_docks_available" in df_raw.columns:
            df_table["Places libres"] = df_raw["num_docks_available"].round(1)

        if (
            "operational_capacity" in df_raw.columns
            and df_raw["operational_capacity"].notna().any()
        ):
            df_table["Capacité"] = (
                df_raw["operational_capacity"].round(0).astype("Int64")
            )

        if "full_ratio" in df_raw.columns and df_raw["full_ratio"].notna().any():
            df_table["Remplissage (%)"] = (df_raw["full_ratio"] * 100).round(1)

        if (
            "empty_duration_ratio" in df_raw.columns
            and df_raw["empty_duration_ratio"].notna().any()
        ):
            df_table["Temps vide (%)"] = (df_raw["empty_duration_ratio"] * 100).round(1)

        if (
            "avg_empty_duration" in df_raw.columns
            and df_raw["avg_empty_duration"].notna().any()
        ):
            df_table["Durée moy. vide (s)"] = df_raw["avg_empty_duration"].round(0)

        if (
            "full_duration_ratio" in df_raw.columns
            and df_raw["full_duration_ratio"].notna().any()
        ):
            df_table["Temps saturé (%)"] = (df_raw["full_duration_ratio"] * 100).round(
                1
            )

        if (
            "avg_full_duration" in df_raw.columns
            and df_raw["avg_full_duration"].notna().any()
        ):
            df_table["Durée moy. saturé (s)"] = df_raw["avg_full_duration"].round(0)

        if "vehicle_types_available" in df_raw.columns and any(
            isinstance(x, dict) and x for x in df_raw["vehicle_types_available"]
        ):
            df_table["Vélos mécaniques"] = df_raw["vehicle_types_available"].apply(
                lambda x: x.get("mechanical") if isinstance(x, dict) else None
            )
            df_table["Vélos électriques"] = df_raw["vehicle_types_available"].apply(
                lambda x: x.get("electric") if isinstance(x, dict) else None
            )

        st.dataframe(df_table, use_container_width=True, hide_index=True)
