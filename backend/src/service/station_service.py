from datetime import UTC, date, datetime, timedelta

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
        return {
            "num_bikes_available": statut.num_bikes_available,
            "num_docks_available": statut.num_docks_available,
            "last_reported": statut.last_reported,
            "vehicle_types_available": statut.vehicle_types_available,
            "vehicle_docks_available": statut.vehicle_docks_available,
            "station_state": statut.station_state,
            "operational_capacity": statut.operational_capacity,
            "full_ratio": min(
                statut.num_bikes_available / statut.operational_capacity, 1.0
            ),
            "reliability_score": s_horaire.reliability_score if s_horaire else None,
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
        stations = self.station_dao.get_nearby(
            criteria.lat, criteria.lon, criteria.radius_meters
        )

        res = []
        if stations:
            for i in range(len(stations)):
                station_id = stations[i].station_id
                if station_id is not None:
                    latest_status = self.status_dao.get_latest_status(station_id)
                    hourly_status = self.hourly_dao.get_latest_hourly_status(station_id)
                    daily_status = self.hourly_dao.aggregate_daily_stats(
                        station_id,
                        datetime.now(UTC).date() - timedelta(days=1),
                        datetime.now(UTC).date(),
                    )

                    if criteria.op_cap is not None and (
                        not latest_status
                        or latest_status.operational_capacity < criteria.op_cap
                    ):
                        continue

                    if criteria.station_state and (
                        not latest_status
                        or latest_status.station_state != criteria.station_state
                    ):
                        continue

                    if criteria.score_min is not None and (
                        not hourly_status
                        or hourly_status.reliability_score < criteria.score_min
                    ):
                        continue

                    if criteria.vehicle_type == VehicleTypeFilter.MECHANICAL:
                        vtypes = (
                            latest_status.vehicle_types_available
                            if latest_status
                            else None
                        )
                        if (
                            not isinstance(vtypes, dict)
                            or (vtypes.get("mechanical") or 0) <= 0
                        ):
                            continue
                    elif criteria.vehicle_type == VehicleTypeFilter.ELECTRIC:
                        vtypes = (
                            latest_status.vehicle_types_available
                            if latest_status
                            else None
                        )
                        if (
                            not isinstance(vtypes, dict)
                            or (vtypes.get("electric") or 0) <= 0
                        ):
                            continue

                    la, lo = stations[i].lat, stations[i].lon
                    res.append(
                        {
                            "station_id": stations[i].station_id,
                            "name": stations[i].name,
                            "lat": la,
                            "lon": lo,
                            "distance_meters": haversine(
                                (la, lo), (criteria.lat, criteria.lon), unit="m"
                            ),
                            "operational_capacity": (
                                latest_status.operational_capacity
                                if latest_status
                                else None
                            ),
                            "station_state": (
                                latest_status.station_state if latest_status else None
                            ),
                            "vehicle_types_available": (
                                latest_status.vehicle_types_available
                                if latest_status
                                else None
                            ),
                            "last_hour_reliability": (
                                hourly_status.reliability_score
                                if hourly_status
                                else None
                            ),
                            "last_day_reliability": (
                                daily_status[-1]["avg_reliability_score"]
                                if daily_status
                                else None
                            ),
                        }
                    )
            return sorted(res, key=lambda r: r["distance_meters"])
        return res
