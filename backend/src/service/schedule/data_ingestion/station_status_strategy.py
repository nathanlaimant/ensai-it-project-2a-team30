from datetime import UTC, datetime
from typing import Any

import httpx

from business_object.station_state import StationState
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

    def from_json_dict(self, json_dict: dict) -> StationStatus:
        """
        Crée une instance de StationStatus à partir d'un dictionnaire JSON.

        Parameters
        ----------
        json_dict : dict
            Données de statut d'une station extraites du JSON.

        Returns
        -------
        StationStatus
            Instance représentant le statut de la station.
        """
        # Number of bikes available (supports standard and camelCase)
        num_bikes_available = json_dict.get("num_bikes_available")
        if num_bikes_available is None:
            num_bikes_available = json_dict.get("numBikesAvailable", 0)

        if num_bikes_available == 0:
            # Vehicle types breakdown (handles GBFS vehicle_types_available)
            # "vehicle_types_available": [
            # 	{
            # 		"count": 10,
            # 		"vehicle_type_id": "type_1"
            # 	},
            # 	{
            # 		"count": 10,
            # 		"vehicle_type_id": "type_2"
            # 	}
            # ]
            vehicle_types_available = json_dict.get("vehicle_types_available")
            if vehicle_types_available:
                if isinstance(vehicle_types_available, list):
                    calculated_count = sum(
                        item.get("count", 0)
                        for item in vehicle_types_available
                        if isinstance(item, dict)
                    )
                    if calculated_count > 0:
                        num_bikes_available = calculated_count
            else:
                # Handle Vélib's num_bikes_available_types format
                # "num_bikes_available_types": [
                # 	{
                # 		"type_1": 10
                # 	},
                # 	{
                # 		"type_2": 10
                # 	}
                # ]
                vehicle_types_available = json_dict.get("num_bikes_available_types")
                if isinstance(vehicle_types_available, list):
                    calculated_count = sum(
                        sum(type.values()) for type in vehicle_types_available
                    )
                    if calculated_count > 0:
                        num_bikes_available = calculated_count

        # Number of docks available (supports standard and camelCase)
        num_docks_available = json_dict.get("num_docks_available")
        if num_docks_available is None:
            num_docks_available = json_dict.get("numDocksAvailable")

        num_bikes_disabled = json_dict.get("num_bikes_disabled")
        num_docks_disabled = json_dict.get("num_docks_disabled")

        # Operational capacity: computed TODO
        operational_capacity = json_dict.get("operational_capacity")
        if operational_capacity is None:
            operational_capacity = (num_bikes_available or 0) + (
                num_docks_available or 0
            )

        # Station state: derived TODO
        if num_docks_available is not None and num_docks_available == 0:
            station_state = StationState.FULL
        elif (num_bikes_available or 0) == 0:
            station_state = StationState.EMPTY
        else:
            station_state = StationState.FUNCTIONAL

        # Last reported: int timestamp
        last_reported = datetime.fromtimestamp(json_dict["last_reported"], tz=UTC)

        return StationStatus(
            station_id=json_dict["station_id"],
            num_bikes_available=num_bikes_available,
            num_bikes_disabled=num_bikes_disabled,
            num_docks_available=num_docks_available,
            num_docks_disabled=num_docks_disabled,
            operational_capacity=int(operational_capacity),
            last_reported=last_reported,
            vehicle_types_available=vehicle_types_available,
            vehicle_docks_available=json_dict.get("vehicle_docks_available"),
            station_state=station_state,
        )

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
                    self.from_json_dict(station_status) for station_status in statuses
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
