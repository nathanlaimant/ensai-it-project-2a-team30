from typing import Any

import httpx

from business_object.station_status import StationStatus
from dao.station_status_dao import StationStatusDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class StationStatusStrategy(BaseIngestionStrategy[StationStatus]):
    """
    Ingère le flux de statuts en temps réel des stations.
 
    Parameters
    ----------
    dao : StationStatusDAO
        DAO permettant la persistance des statuts de stations.
    feed_name : str
        Nom du flux de données ingéré.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        dao: StationStatusDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[StationStatus]:
        """
        Transforme les données brutes du flux en entités StationStatus.
 
        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux (format GBFS `station_status`).
 
        Returns
        -------
        list of StationStatus
            Liste des statuts de stations extraits du flux, ou une liste
            vide si le flux est vide ou mal formé.
        """
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                statuses = data.get("stations", [])
                return [
                    StationStatus.from_dict(station_status)
                    for station_status in statuses
                ]
        return []

    async def persist(self, entities: list[StationStatus]) -> int:
        """
        Persiste une liste de statuts de stations en base de données.
 
        Parameters
        ----------
        entities : list of StationStatus
            Statuts de stations à persister.
 
        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        raise NotImplementedError
