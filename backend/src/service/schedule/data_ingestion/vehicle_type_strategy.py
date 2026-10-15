from typing import Any

import httpx

from business_object.vehicle_type import VehicleType
from dao.vehicle_type_dao import VehicleTypeDAO

from .feed_ingestion_strategy import BaseIngestionStrategy


class VehicleTypeStrategy(BaseIngestionStrategy[VehicleType]):
    """
    Ingère le flux des types de véhicules.
 
    Parameters
    ----------
    dao : VehicleTypeDAO
        DAO permettant la persistance des types de véhicules.
    feed_name : str
        Nom du flux de données ingéré.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        dao: VehicleTypeDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    def parse_payload(self, raw_data: Any) -> list[VehicleType]:
        """
        Transforme les données brutes du flux en entités VehicleType.
 
        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux (format GBFS `vehicle_types`).
 
        Returns
        -------
        list of VehicleType
            Liste des types de véhicules extraits du flux, ou une liste
            vide si le flux est vide ou mal formé.
        """
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                vehicle_types = data.get("vehicle_types", [])
                return [
                    VehicleType.from_dict(vehicle_type)
                    for vehicle_type in vehicle_types
                ]
        return []

    async def persist(self, entities: list[VehicleType]) -> int:
        """
        Persiste une liste de types de véhicules en base de données.
 
        Parameters
        ----------
        entities : list of VehicleType
            Types de véhicules à persister.
 
        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        raise NotImplementedError
