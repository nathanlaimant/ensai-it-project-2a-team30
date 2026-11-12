from datetime import UTC, datetime, timedelta

from haversine import haversine  # type: ignore[import-not-found]

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO
from schema.common_model import TimePeriod
from schema.station_model import (
    StationRecommendationRequest,
    StationSearchRequest,
    VehicleTypeFilter,
)


class StationService:
    """
    Gère la logique métier liée à la consultation des stations.

    Attributes
    ----------
    station_dao : StationDAO
        DAO permettant l'accès aux informations fixes des stations.
    status_dao : StationStatusDAO
        DAO permettant l'accès aux statuts en temps réel des stations.
    hourly_dao : StationStatusHourlyDAO
        DAO permettant l'accès aux agrégations horaires des stations.
    """

    def __init__(
        self,
        station_dao: StationDAO,
        status_dao: StationStatusDAO,
        hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_dao = station_dao
        self.status_dao = status_dao
        self.hourly_dao = hourly_dao

    def get_by_id(self, station_id: str) -> StationInformation | None:
        """
        Donne une station à partir de son identifiant.

        Arguments
        ---------
        station_id: int
            Identifiant de la station à trouver

        Returns
        -------
        StationInformation
            Station avec l'identifiant correspondant.
            None si la station n'est pas trouvée.
        """
        if not station_id:
            return None
        return self.station_dao.get_by_id(station_id)

    def list_stations(self, payload: StationSearchRequest) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.

        Parameters
        ----------
        payload: StationSearchRequest
            Requête de recherche contenant les critères de filtrage.

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        if not payload:
            return []
        return self.station_dao.list_stations(
            name=payload.name,
            short_name=payload.short_name,
            address=payload.address,
            min_capacity=payload.min_capacity,
            max_capacity=payload.max_capacity,
            page=payload.page,
            size=payload.size,
        )

    @staticmethod
    def _build_current_status_dict(statut, s_horaire) -> dict:
        """Construit le dictionnaire de statut courant d'une station."""
        full_ratio = (
            min(statut.num_bikes_available / statut.operational_capacity, 1.0)
            if statut.operational_capacity > 0
            else 0.0
        )
        return {
            "num_bikes_available": statut.num_bikes_available,
            "num_docks_available": statut.num_docks_available,
            "last_reported": statut.last_reported,
            "vehicle_types_available": statut.vehicle_types_available,
            "vehicle_docks_available": statut.vehicle_docks_available,
            "station_state": statut.station_state,
            "operational_capacity": statut.operational_capacity,
            "full_ratio": full_ratio,
            "reliability_score": s_horaire.reliability_score if s_horaire else None,
        }

    def get_station_current_status(self, station_id: str) -> dict | None:
        """
        Récupère l'état en temps réel d'une station.

        Parameters
        ----------
        station_id : str
            Identifiant de la station demandée.

        Returns
        -------
        dict
            État courant de la station (vélos/docks disponibles, etc.).
            Ne renvoie rien si la station n'est pas identifiable.
        """
        statut = self.status_dao.get_latest_status(station_id)
        s_horaire = self.hourly_dao.get_latest_hourly_status(station_id)
        if not statut:
            return None
        return self._build_current_status_dict(statut, s_horaire)

    def get_stations_current_statuses(self, station_ids: list[str]) -> dict[str, dict]:
        """
        Récupère l'état en temps réel pour une liste de stations.

        Parameters
        ----------
        station_ids : list of str
            Identifiants des stations demandées.

        Returns
        -------
        dict[str, dict]
            Dictionnaire associant chaque identifiant de station trouvé à son état courant.
        """
        unique_ids = list({sid for sid in station_ids if sid})
        if not unique_ids:
            return {}

        statuses = self.status_dao.get_latest_statuses(unique_ids)
        if not statuses:
            return {}

        hourly_statuses = self.hourly_dao.get_latest_hourly_statuses(
            list(statuses.keys())
        )
        return {
            sid: self._build_current_status_dict(statut, hourly_statuses.get(sid))
            for sid, statut in statuses.items()
        }

    def get_station_history(
        self, station_id: str, time_period: TimePeriod
    ) -> list[dict]:
        """
        Récupère l'historique d'état d'une station sur une période donnée.

        Parameters
        ----------
        station_id: str
            Identifiant de la station
        time_period: TimePeriod
            Période de temps pour laquelle récupérer l'historique

        Returns
        -------
        list of dict
            Liste des statuts de la station sur la période demandée.
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        end_time = datetime.now(UTC)
        if time_period == TimePeriod.une_heure:
            start_time = datetime.now(UTC) - timedelta(hours=1)
            statut = self.status_dao.get_one_station_history(
                station_id, start_time, end_time
            )
            s_horaire = self.hourly_dao.get_hourly_stats(
                station_id, start_time, end_time
            )
            if not statut:
                return []
            reliability_score = s_horaire[0].reliability_score if s_horaire else None
            return [
                {
                    "station_id": s.station_id,
                    "num_bikes_available": s.num_bikes_available,
                    "num_docks_available": s.num_docks_available,
                    "last_reported": s.last_reported,
                    "station_state": s.station_state,
                    "operational_capacity": s.operational_capacity,
                    "full_ratio": min(
                        s.num_bikes_available / s.operational_capacity, 1.0
                    ),
                    "reliability_score": reliability_score,
                }
                for s in statut
            ]
        elif time_period == TimePeriod.vingt_quatre_heures:
            start_time = datetime.now(UTC) - timedelta(days=1)
            s_horaire = self.hourly_dao.get_hourly_stats(
                station_id, start_time, end_time
            )
            if not s_horaire:
                return []
            return [
                {
                    "station_id": s.station_id,
                    "num_bikes_available": s.avg_num_bikes_available,
                    "num_docks_available": s.avg_num_docks_available,
                    "last_reported": s.bucket_hour,
                    "operational_capacity": round(s.avg_operational_capacity),
                    "full_ratio": min(
                        s.avg_num_bikes_available / s.avg_operational_capacity, 1.0
                    ),
                    "full_duration_ratio": s.full_duration_sec / 3600,
                    "avg_full_duration": (
                        (s.full_duration_sec / s.full_events_cnt)
                        if s.full_events_cnt > 0
                        else 0
                    ),
                    "empty_duration_ratio": s.empty_duration_sec / 3600,
                    "avg_empty_duration": (
                        (s.empty_duration_sec / s.empty_events_cnt)
                        if s.empty_events_cnt > 0
                        else 0
                    ),
                    "reliability_score": s.reliability_score,
                }
                for s in s_horaire
            ]
        elif time_period in [TimePeriod.sept_jours, TimePeriod.trente_jours]:
            start_time = datetime.now(UTC) - (
                timedelta(days=7)
                if time_period == TimePeriod.sept_jours
                else timedelta(days=30)
            )
            s_quotidienne = self.hourly_dao.aggregate_daily_stats(
                station_id, start_time.date(), end_time.date()
            )
            if not s_quotidienne:
                return []
            return [
                {
                    "station_id": s["station_id"],
                    "num_bikes_available": s["avg_num_bikes_available"],
                    "num_docks_available": s["avg_num_docks_available"],
                    "last_reported": datetime.combine(
                        s["stat_date"], datetime.min.time(), tzinfo=UTC
                    ),
                    "operational_capacity": round(s["avg_operational_capacity"]),
                    "full_ratio": min(
                        s["avg_num_bikes_available"] / s["avg_operational_capacity"],
                        1.0,
                    ),
                    "full_duration_ratio": s["full_duration_sec"] / 3600,
                    "avg_full_duration": (
                        (s["full_duration_sec"] / s["full_events_cnt"])
                        if s["full_events_cnt"] > 0
                        else 0
                    ),
                    "empty_duration_ratio": s["empty_duration_sec"] / 3600,
                    "avg_empty_duration": (
                        (s["empty_duration_sec"] / s["empty_events_cnt"])
                        if s["empty_events_cnt"] > 0
                        else 0
                    ),
                    "reliability_score": s["avg_reliability_score"],
                }
                for s in s_quotidienne
            ]
        else:
            return []

    @staticmethod
    def _matches_status_filters(
        latest_status, criteria: StationRecommendationRequest
    ) -> bool:
        """Vérifie si le statut courant d'une station respecte les filtres demandés."""
        if criteria.op_cap is not None and (
            not latest_status or latest_status.operational_capacity < criteria.op_cap
        ):
            return False

        if criteria.station_state and (
            not latest_status or latest_status.station_state != criteria.station_state
        ):
            return False

        if criteria.vehicle_type != VehicleTypeFilter.ALL:
            vtypes = latest_status.vehicle_types_available if latest_status else None
            if (
                not isinstance(vtypes, dict)
                or (vtypes.get(criteria.vehicle_type.value) or 0) <= 0
            ):
                return False

        return True

    def get_nearby_recommendations(
        self, criteria: StationRecommendationRequest
    ) -> list[dict]:
        """
        Recommande des stations à proximité d'une position donnée.

        Arguments
        ---------
        criteria: StationRecommendationRequest
            Critères de recherche pour les stations recommandées.

        Returns
        -------
        list of dict
            Liste des stations recommandées, avec leurs informations
            pertinentes (distance, disponibilité, fiabilité, etc.).
            Ne renvoie rien si l'un des critères n'est pas dans le bon format.
        """
        # 1. Find nearby stations based on location and radius
        stations = self.station_dao.get_nearby(
            criteria.lat, criteria.lon, criteria.radius_meters
        )
        if not stations:
            return []
        nearby_stations: list[tuple[str, StationInformation]] = [
            (s.station_id, s) for s in stations if s.station_id is not None
        ]
        if not nearby_stations:
            return []
        # 2. Filter stations using op_cap, state, and vehicle type (from station_status)
        nearby_ids = [sid for sid, _ in nearby_stations]
        latest_statuses = self.status_dao.get_latest_statuses(nearby_ids)
        status_filtered = [
            (sid, s)
            for sid, s in nearby_stations
            if self._matches_status_filters(latest_statuses.get(sid), criteria)
        ]
        if not status_filtered:
            return []
        # 3. Filter stations using reliability score (from station_status_hourly)
        hourly_statuses = self.hourly_dao.get_latest_hourly_statuses(
            [sid for sid, _ in status_filtered]
        )
        final_stations = []
        for sid, s in status_filtered:
            hourly_status = hourly_statuses.get(sid)
            if criteria.score_min is not None and (
                not hourly_status
                or hourly_status.reliability_score < criteria.score_min
            ):
                continue
            final_stations.append((sid, s))
        if not final_stations:
            return []
        # 4. Aggregate daily stats for the final stations
        today = datetime.now(UTC).date()
        daily_stats_map = self.hourly_dao.aggregate_daily_stats_for_stations(
            [sid for sid, _ in final_stations],
            today - timedelta(days=1),
            today,
        )
        # 5. Combine all information and return the recommended stations with relevant details
        res = []
        for sid, s in final_stations:
            latest_status = latest_statuses.get(sid)
            hourly_status = hourly_statuses.get(sid)
            daily_status = daily_stats_map.get(sid)
            la, lo = s.lat, s.lon
            res.append(
                {
                    "station_id": sid,
                    "name": s.name,
                    "lat": la,
                    "lon": lo,
                    "distance_meters": haversine(
                        (la, lo), (criteria.lat, criteria.lon), unit="m"
                    ),
                    "operational_capacity": (
                        latest_status.operational_capacity if latest_status else None
                    ),
                    "station_state": (
                        latest_status.station_state if latest_status else None
                    ),
                    "vehicle_types_available": (
                        latest_status.vehicle_types_available if latest_status else None
                    ),
                    "last_hour_reliability": (
                        hourly_status.reliability_score if hourly_status else None
                    ),
                    "last_day_reliability": (
                        daily_status[-1]["avg_reliability_score"]
                        if daily_status
                        else None
                    ),
                }
            )
        return sorted(res, key=lambda r: r["distance_meters"])
