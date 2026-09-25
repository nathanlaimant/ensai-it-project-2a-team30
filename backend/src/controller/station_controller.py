"""Gère les consultations de stations."""

from ..business_object.station_information import StationInformation
from ..service.station_service import StationService


def get_station_info(station_id: str) -> StationInformation:
    """
    Récupère les informations fixes d'une station.
 
    Parameters
    ----------
    station_id : str
        Identifiant de la station demandée.
 
    Returns
    -------
    StationInformation
        Informations statiques de la station.
    """
    raise NotImplementedError


def list_stations(payload: dict) -> list[StationInformation]:
    """
    Liste les stations selon des critères de recherche.
 
    Parameters
    ----------
    payload : dict
        Critères de filtrage et/ou de pagination.
 
    Returns
    -------
    list of StationInformation
        Liste des stations correspondant aux critères.
    """
    raise NotImplementedError


def get_station_current_status(station_id: str) -> dict:
    """
    Récupère l'état en temps réel d'une station.
 
    Parameters
    ----------
    station_id : str
        Identifiant de la station demandée.
 
    Returns
    -------
    dict
        État courant de la station (vélos/docks disponibles, etc.).
    """
    raise NotImplementedError


def get_station_history(payload: dict) -> list[dict]:
    """
    Récupère l'historique de l'état d'une station sur une période donnée.
 
    Parameters
    ----------
    payload : dict
        Critères de la requête (ex: station_id, période).
 
    Returns
    -------
    list of dict
        Historique des états de la station sur la période demandée.
    """
    raise NotImplementedError
