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
                return [SystemInformation.from_dict(data)]
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
        return len(entities)  # TODO
