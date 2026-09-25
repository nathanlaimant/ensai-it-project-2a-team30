from datetime import date, datetime

from business_object.station_status_hourly import StationStatusHourly
from utils.db_connection import DbConnection


class StationStatusHourlyDAO:
    """Gère l'accès aux données de statut des stations agrégées à l'heure en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def bulk_insert_hourly_stats(self, records: list[StationStatusHourly]) -> int:
        """
        Insert en masse les données d'une station sur une heure.
        
        Parameters
        ----------
        records : list of StationStatusHourly
            Enregistrements d'agrégation horaire à insérer.
 
        Returns
        -------
        int
            Nombre d'enregistrements effectivement insérés.
        """
        raise NotImplementedError

    def get_hourly_stats(
        self, station_id: str, start_time: datetime, end_time: datetime
    ) -> list[StationStatusHourly]:
        """Récupère les agrégations horaires d'une station sur une période donnée.
 
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
        list of StationStatusHourly
            Liste des agrégations horaires de la station sur la période demandée.
        """
        raise NotImplementedError

    def aggregate_daily_stats(
        self, station_id: str, start_date: date, end_date: date
    ) -> list[dict]:
        """
        Agrège les statistiques horaires d'une station à l'échelle journalière.
 
        Parameters
        ----------
        station_id : str
            Identifiant de la station concernée.
        start_date : date
            Date de début de la période.
        end_date : date
            Date de fin de la période.
 
        Returns
        -------
        list of dict
            Liste des statistiques journalières agrégées de la station.
        """
        raise NotImplementedError
