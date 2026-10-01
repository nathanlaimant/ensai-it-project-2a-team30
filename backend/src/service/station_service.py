from business_object.station_information import StationInformation
from dao.station_dao import StationDAO
from dao.station_status_dao import StationStatusDAO
from dao.station_status_hourly_dao import StationStatusHourlyDAO


class StationService:
    """
    Gère la logique métier liée à la consultation des stations.

    Parameters
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

    def list_stations(self, query_params: dict) -> list[StationInformation]:
        """
        Liste les stations selon des critères de recherche.

        Parameters
        ----------
        query_params : dict
            Critères de filtrage et/ou de pagination.

        Returns
        -------
        list of StationInformation
            Liste des stations correspondant aux critères.
        """
        raise NotImplementedError

    def get_station_current_status(self, station_id: str) -> dict:
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
        """
        raise NotImplementedError

    def get_station_history(self, query_params: dict) -> list[dict]:
        """
        Récupère l'historique d'état d'une station sur une période donnée.

        Parameters
        ----------
        query_params : dict
            Critères de la requête (ex: station_id, période).

        Returns
        -------
        list of dict
            Historique des états de la station sur la période demandée.
        """
        raise NotImplementedError
