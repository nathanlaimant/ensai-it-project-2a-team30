from datetime import date
from typing import Any

import httpx

from business_object.system_information import SystemInformation
from dao.system_information_dao import SystemInformationDAO
from utils.log_utils import get_logger

from .feed_ingestion_strategy import BaseIngestionStrategy

logger = get_logger(__name__)


class SystemInformationStrategy(BaseIngestionStrategy[SystemInformation]):
    """
    Ingère le flux d'informations générales du système.

    Parameters
    ----------
    dao : SystemInformationDAO
        DAO permettant la persistance des informations système.
    feed_name : str
        Nom du flux de données ingéré.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        dao: SystemInformationDAO,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        super().__init__(feed_name, url, http_client)
        self.dao = dao

    def from_json_dict(self, json_dict: dict) -> SystemInformation:
        """
        Crée une instance de SystemInformation à partir d'un dictionnaire JSON.

        Parameters
        ----------
        json_dict : dict
            Données du système extraites du JSON.

        Returns
        -------
        SystemInformation
            Instance représentant le système.
        """
        return SystemInformation(
            language=json_dict["language"],
            name=json_dict["name"],
            url=json_dict.get("url"),
            start_date=(
                date.fromisoformat(json_dict["start_date"])
                if json_dict.get("start_date")
                else None
            ),
            phone_number=json_dict.get("phone_number"),
            email=json_dict.get("email"),
            timezone=json_dict["timezone"],
            system_id=json_dict["system_id"],
        )

    def parse_payload(self, raw_data: Any) -> list[SystemInformation]:
        """
        Transforme les données brutes du flux en entité SystemInformation.

        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux (format GBFS `system_information`).

        Returns
        -------
        list of SystemInformation
            Liste contenant l'unique entité système extraite du flux, ou
            une liste vide si le flux est vide ou mal formé.
        """
        if raw_data:
            data = raw_data.get("data", {})
            if data:
                return [self.from_json_dict(data)]
        return []

    async def persist(self, entities: list[SystemInformation]) -> int:
        """
        Persiste les informations système en base de données.

        Parameters
        ----------
        entities : list of SystemInformation
            Informations système à persister.

        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        if not entities:
            return 0

        persisted_count = 0
        for entity in entities:
            if self.dao.upsert_system_info(entity):
                persisted_count += 1
        return persisted_count
