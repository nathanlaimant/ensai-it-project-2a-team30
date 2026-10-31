"""Gère les requètes sur les stations favorites."""

from fastapi import APIRouter, Depends, HTTPException, status

from business_object.station_information import StationInformation
from dependencies.authentication import get_current_user
from dependencies.service import get_favorite_station_service
from schema.station_model import StationInfoResponse
from service.favorite_station_service import FavoriteStationService
from utils.log_utils import get_logger

router = APIRouter(prefix="/favorites", tags=["Favoris"])
logger = get_logger(__name__)


@router.post("/{station_id}")
async def add_favorite(
    station_id: str,
    user_id: int = Depends(get_current_user),
    favorite_service: FavoriteStationService = Depends(get_favorite_station_service),
) -> str:
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
    logger.info("Ajout de la station %s aux favoris de l'utilisateur %s", station_id, user_id)
    if not favorite_service.add_favorite_station(user_id, station_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible d'ajouter cette station aux favoris.",
        )
    return "Station ajoutée aux favoris."


@router.post("/", response_model=list[StationInfoResponse])
async def list_favorites(
    payload: dict,
    user_id: int = Depends(get_current_user),
    favorite_service: FavoriteStationService = Depends(get_favorite_station_service),
) -> list[StationInformation]:
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
    logger.info("Liste des stations favorites de l'utilisateur %s", user_id)
    query_params = {**payload, "user_id": user_id}
    favorites = favorite_service.list_favorites(query_params)
    if favorites is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )
    return favorites


@router.delete("/{station_id}")
async def remove_favorite(
    station_id: str,
    user_id: int = Depends(get_current_user),
    favorite_service: FavoriteStationService = Depends(get_favorite_station_service),
) -> str:
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
    logger.info("Retrait de la station %s des favoris de l'utilisateur %s", station_id, user_id)
    if not favorite_service.remove_favorite_station(user_id, station_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cette station n'est pas présente dans les favoris.",
        )
    return "Station retirée des favoris."
