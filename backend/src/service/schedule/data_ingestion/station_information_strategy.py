from typing import Any

import httpx

from business_object.station_information import StationInformation
from dao.station_dao import StationDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class StationInformationStrategy(BaseIngestionStrategy[StationInformation]):
    """
    Ingère le flux d'informations fixes des stations.

    Parameters
    ----------
    dao : StationDAO
        DAO permettant la persistance des informations de stations.
    feed_name : str
        Nom du flux de données ingéré.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        dao: StationDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    def from_json_dict(self, json_dict: dict) -> StationInformation:
        """
        Crée une instance de StationInformation à partir d'un dictionnaire JSON.

        Parameters
        ----------
        json_dict : dict
            Données d'une station extraites du JSON.

        Returns
        -------
        StationInformation
            Instance représentant la station.
        """
        return StationInformation(
            name=json_dict["name"],
            short_name=json_dict.get("short_name"),
            lat=float(json_dict["lat"]),
            lon=float(json_dict["lon"]),
            address=json_dict.get("address"),
            is_virtual_station=(
                bool(json_dict["is_virtual_station"])
                if json_dict.get("is_virtual_station")
                else None
            ),
            station_area=json_dict.get("station_area"),
            contact_phone=json_dict.get("contact_phone"),
            capacity=(
                int(json_dict["capacity"]) if json_dict.get("capacity") else None
            ),
            is_charging_station=(
                bool(json_dict["is_charging_station"])
                if json_dict.get("is_charging_station")
                else None
            ),
            station_id=json_dict["station_id"],
        )

    def parse_payload(self, raw_data: Any) -> list[StationInformation]:
        """
        Transforme les données brutes du flux en entités StationInformation.

        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux (format GBFS `station_information`).

        Returns
        -------
        list of StationInformation
            Liste des stations extraites du flux, ou une liste vide si
            le flux est vide ou mal formé.
        """
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                stations = data.get("stations", [])
                return [self.from_json_dict(station) for station in stations]
        return []

    async def persist(self, entities: list[StationInformation]) -> int:
        """
        Persiste une liste d'informations de stations en base de données.

        Parameters
        ----------
        entities : list of StationInformation
            Informations de stations à persister.

        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        raise NotImplementedError
