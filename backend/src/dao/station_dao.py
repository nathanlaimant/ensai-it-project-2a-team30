from business_object.station_information import StationInformation
from utils.db_connection import DbConnection


class StationDAO:
    """Gère l'accès aux données des informations de stations en base de données."""

    def __init__(self, db_connection: DbConnection):
        self._db_connection = db_connection

    def upsert_station_info(self, station: StationInformation) -> bool:
        """
        Crée ou met à jour les informations d'une station.
 
        Parameters
        ----------
        station : StationInformation
            Informations de la station à créer ou mettre à jour.
 
        Returns
        -------
        bool
            True si l'opération a réussi.
        """
        raise NotImplementedError

    def get_by_id(self, station_id: str) -> StationInformation:
        """
        Récupère une station à partir de son identifiant.
 
        Parameters
        ----------
        station_id : str
            Identifiant de la station recherchée.
 
        Returns
        -------
        StationInformation
            Informations de la station correspondante, ou None si introuvable.
        """
        raise NotImplementedError

    def get_nearby(
        self, lat: float, lon: float, radius_meters: float
    ) -> list[StationInformation]:
        """
        Récupère les stations situées à proximité d'une position donnée.
 
        Parameters
        ----------
        lat : float
            Latitude du point de référence.
        lon : float
            Longitude du point de référence.
        radius_meters : float
            Rayon de recherche en mètres.
 
        Returns
        -------
        list of StationInformation
            Liste des stations situées dans le rayon demandé.
        """
        raise NotImplementedError

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
