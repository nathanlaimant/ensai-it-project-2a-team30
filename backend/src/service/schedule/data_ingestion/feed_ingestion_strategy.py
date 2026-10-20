from abc import ABC, abstractmethod
from typing import Any

import httpx

from utils.log_utils import get_logger

logger = get_logger(__name__)


class BaseIngestionStrategy[T](ABC):
    """
    Définit le contrat commun à toute stratégie d'ingestion de flux.

    Classe abstraite générique : `T` représente le type d'entité métier
    produite par la stratégie (ex: `StationStatus`, `SystemInformation`).

    Parameters
    ----------
    feed_name : str
        Nom du flux ingéré, utilisé notamment pour la journalisation.
    url : str
        URL du flux de données à ingérer.
    http_client : httpx.AsyncClient
        Client HTTP asynchrone utilisé pour récupérer le flux.
    """

    def __init__(
        self,
        feed_name: str,
        url: str,
        http_client: httpx.AsyncClient,
    ):
        self.feed_name = feed_name
        self.url = url
        self.http_client = http_client

    async def fetch_feed(self) -> Any:
        """
        Récupère le contenu JSON brut du flux à l'URL configurée.

        Returns
        -------
        Any
            Contenu JSON brut de la réponse du flux.
        """
        response = await self.http_client.get(self.url)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    def parse_payload(self, raw_data: Any) -> list[T]:
        """
        Transforme les données brutes d'un flux en entités métier.

        Parameters
        ----------
        raw_data : Any
            Contenu brut du flux à transformer.

        Returns
        -------
        list of T
            Liste des entités métier extraites du flux.
        """
        raise NotImplementedError

    @abstractmethod
    async def persist(self, records: list[T]) -> int:
        """
        Persiste une liste d'entités métier extraites d'un flux.

        Parameters
        ----------
        records : list of T
            Entités métier à persister.

        Returns
        -------
        int
            Nombre d'entités effectivement persistées.
        """
        raise NotImplementedError

    async def execute(self) -> None:
        """
        Exécute la stratégie d'ingestion de bout en bout.

        Enchaîne la récupération du flux (`fetch_feed`), son analyse
        (`parse_payload`) puis sa persistance (`persist`), en
        journalisant le résultat ou toute erreur survenue.

        Returns
        -------
        None
        """
        try:
            raw_data = await self.fetch_feed()
            records = self.parse_payload(raw_data)
            count = await self.persist(records)
            logger.info(f"{self.feed_name}: {count} records ingested.")
        except Exception as e:
            logger.error(f"Error during {self.feed_name} ingestion: {e}")
