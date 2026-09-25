"""Gère les requètes sur les stations favorites."""

from business_object.station_information import StationInformation
from service.favorite_station_service import FavoriteStationService


def add_favorite(station_id: str) -> str:
    """
    Ajoute une station aux favoris de l'utilisateur courant.
 
    Parameters
    ----------
    station_id : str
        Identifiant de la station à ajouter aux favoris.
        
    Returns
    -------
    str
        Message de confirmation de l'ajout.
    """
    raise NotImplementedError


def list_favorites(payload: dict) -> list[StationInformation]:
    """
    Liste les stations favorites de l'utilisateur courant.
 
    Parameters
    ----------
    payload : dict
        Critères de filtrage et/ou de pagination.
 
    Returns
    -------
    list of StationInformation
        Liste des stations favorites correspondant aux critères.
    """
    raise NotImplementedError


def remove_favorite(station_id: str):
    """
    Retire une station des favoris de l'utilisateur courant.
 
    Parameters
    ----------
    station_id : str
        Identifiant de la station à retirer des favoris.
 
    Returns
    -------
    str
        Message de confirmation du retrait.
    """
    raise NotImplementedError
