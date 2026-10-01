from ..dao import StationStatusDAO, StationStatusHourlyDAO


class StationAggregationService:
    """
    Agrège les statuts en temps réel des stations en statistiques horaires.

    Parameters
    ----------
    station_status_dao : StationStatusDAO
        DAO permettant l'accès aux statuts en temps réel des stations.
    station_hourly_dao : StationStatusHourlyDAO
        DAO permettant l'accès aux agrégations horaires des stations.
    """

    def __init__(
        self,
        station_status_dao: StationStatusDAO,
        station_hourly_dao: StationStatusHourlyDAO,
    ):
        self.station_status_dao = station_status_dao
        self.station_hourly_dao = station_hourly_dao

    def aggregate_hourly_stats(self) -> int:
        """
        Agrège les statuts en temps réel des stations sur l'heure écoulée
        et persiste le résultat sous forme d'agrégations horaires.

        Returns
        -------
        int
            Nombre d'agrégations horaires générées.
        """
        raise NotImplementedError
