from datetime import datetime

from business_object.station_status import StationStatus
from utils.db_connection import DbConnection


class StationStatusDAO:
    """Gère l'accès aux données de statut des stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def bulk_insert_status(self, records: list[StationStatus]) -> int:
        """
        Insère en masse une liste d'enregistrements de statut de stations.
 
        Parameters
        ----------
        records : list of StationStatus
            Enregistrements de statut à insérer.
 
        Returns
        -------
        int
            Nombre d'enregistrements effectivement insérés.
        """
        raise NotImplementedError

    def get_latest_status(self, station_id: str) -> StationStatus:
        """
        Récupère le dernier statut connu d'une station.
 
        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
 
        Returns
        -------
        StationStatus
            Dernier statut connu de la station, ou None si introuvable.
        """
        raise NotImplementedError

    def get_status_history(
        self, station_id: str, start_time: datetime, end_time: datetime
    ) -> list[StationStatus]:
        """
        Récupère l'historique des statuts d'une station sur une période donnée.
 
        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
        start_time : datetime
            Date et heure de début de la période.
        end_time : datetime
            Date et heure de fin de la période.
 
        Returns
        -------
        list of StationStatus
            Liste des statuts de la station sur la période demandée.
        """
        raise NotImplementedError
