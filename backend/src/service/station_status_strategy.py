from ..business_object import StationStatus
from ..dao import StationStatusDAO
from .feed_ingestion_strategy import FeedIngestionStrategy


class StationStatusStrategy(FeedIngestionStrategy[StationStatus]):
    """
    Ingère et persiste les flux de statut en temps réel des stations.
 
    Parameters
    ----------
    dao : StationStatusDAO
        DAO permettant la persistance des statuts de stations.
    feed_name : str
        Nom du flux de données ingéré (ex: "station_status").
    interval_seconds : int
        Intervalle, en secondes, entre deux ingestions du flux.
    url : str
        URL du flux de données à ingérer.
    """

    def __init__(
        self, dao: StationStatusDAO, feed_name: str, interval_seconds: int, url: str
    ):
        super().__init__(feed_name, interval_seconds, url)
        self.dao = dao

    def parse_payload(self, headers: dict, raw_data: dict) -> list[StationStatus]:
        """
        Transforme les données brutes d'un flux en entités StationStatus.
 
        Parameters
        ----------
        headers : dict
            En-têtes de la réponse HTTP du flux ingéré.
        raw_data : dict
            Contenu brut du flux à transformer.
 
        Returns
        -------
        list of StationStatus
            Liste des statuts de stations extraits du flux.
        """
        raise NotImplementedError

    def persist(self, entities: list[StationStatus]) -> int:
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
