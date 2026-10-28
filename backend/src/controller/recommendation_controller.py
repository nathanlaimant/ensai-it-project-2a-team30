"""Gère les recommandations de stations pour l'utilisateur."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from dependencies.service import get_recommendation_service
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


@router.get("/", response_model=list[dict], tags=["Recommandations"])
async def get_nearby_recommendations(
    payload: dict,
    reco_service=Depends(get_recommendation_service)
) -> Any:
    """
    Recommande des stations à proximité d'une position donnée.

    Parameters
    ----------
    lat: int
        Latitude de l'adresse données

    longitude: int
        Longitude de l'adresse données

    radius_meters: int
        Rayon envisagé pour la recherche de stations

    Returns
    -------
    list of dict
        Liste des stations recommandées, avec leurs informations
        pertinentes (distance, disponibilité, etc.).
    """
    logger.info("Proposition de stations à proximité")
    recos = reco_service.get_nearby_recommendations(payload)
    if not recos:
        raise HTTPException()
    return recos
