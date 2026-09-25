"""Gère les recommandations de stations pour l'utilisateur."""

from service.recommendation_service import RecommendationService


def get_nearby_recommendations(payload: dict) -> list[dict]:
    """
    Recommande des stations à proximité d'une position donnée.
 
    Parameters
    ----------
    payload : dict
        Critères de la requête (ex: latitude, longitude, rayon).
 
    Returns
    -------
    list of dict
        Liste des stations recommandées, avec leurs informations
        pertinentes (distance, disponibilité, etc.).
    """
    raise NotImplementedError
