"""Gère les consultations de stations."""

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status  # type: ignore[import-not-found]

from dependencies.service import get_station_service
from schema.common_model import TimePeriod
from schema.station_model import (
    StationInfoResponse,
    StationRecommendationRequest,
    StationRecommendationResponse,
    StationSearchRequest,
    StationStatusResponse,
)
from service.station_service import StationService
from utils.log_utils import get_logger

router = APIRouter(prefix="/station", tags=["Stations"])

logger = get_logger(__name__)


@router.get("/{station_id}", response_model=StationInfoResponse)
async def get_station_info(
    station_id: str, station_service: StationService = Depends(get_station_service)
) -> Any:
    """
    Récupère les informations fixes d'une station.

    Parameters
    ----------
    station_id : str
        Identifiant de la station demandée.

    Returns
    -------
    StationInfoResponse
        Informations statiques de la station.

    Raises
    ------
    HTTPException:
        Erreur 404 si la station n'est pas trouvée.
    """
    logger.info("Recherche d'une station à partir de son identifiant")
    station = station_service.get_by_id(station_id)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station (id={station_id}) non trouvée.",
        )
    return station


@router.post("", response_model=list[StationInfoResponse])
async def list_stations(
    payload: StationSearchRequest,
    station_service: StationService = Depends(get_station_service),
) -> Any:
    """
    Liste les stations selon des critères de recherche.

    Parameters
    ----------
    payload : StationSearchRequest
        Critères de filtrage et/ou de pagination.

    Returns
    -------
    list of StationInfoResponse
        Liste des stations correspondant aux critères.
    """
    logger.info("Recherche d'une station à partir de paramètres donnés ou non")
    return station_service.list_stations(payload)


@router.get("/{station_id}/status", response_model=StationStatusResponse)
async def get_station_current_status(
    station_id: str, station_service: StationService = Depends(get_station_service)
) -> Any:
    """
    Récupère l'état en temps réel d'une station.

    Parameters
    ----------
    station_id : str
        Identifiant de la station demandée.

    Returns
    -------
    StationStatusResponse
        État courant de la station.

    Raises
    ------
    HTTPException:
        Erreur 404 si la station n'est pas trouvée.
    """
    logger.info("Statut le plus récent de la station")
    # Recupère StationStatus le plus récent par le StationStatusDAO.get_latest_status
    # et StationStatusHourly le plus récent par le StationStatusHourlyDAO.get_latest_hourly_status.
    # Puis, les convertit en StationStatusResponse.
    statut = station_service.get_station_current_status(station_id)
    if statut is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station (id={station_id}) non trouvée.",
        )
    return statut


@router.post("/statuses", response_model=dict[str, StationStatusResponse])
def get_stations_current_statuses(
    station_ids: list[str] = Body(..., max_length=500),
    station_service: StationService = Depends(get_station_service),
) -> Any:
    """
    Récupère l'état en temps réel de plusieurs stations.

    Parameters
    ----------
    station_ids : list[str]
        Liste des identifiants des stations demandées.

    Returns
    -------
    dict[str, StationStatusResponse]
        Dictionnaire associant chaque identifiant de station trouvé à son état courant.
    """
    logger.info("Statuts les plus récents de plusieurs stations")
    return station_service.get_stations_current_statuses(station_ids)


@router.get(
    "/{station_id}/history",
    response_model=list[StationStatusResponse],
    tags=["Stations"],
)
async def get_station_history(
    station_id: str,
    period: TimePeriod = Query(
        default=TimePeriod.une_heure,
    ),
    station_service: StationService = Depends(get_station_service),
) -> Any:
    """
    Récupère l'historique de l'état d'une station sur une période donnée.

    Parameters
    ----------
    station_id: str
        Identifiant de la station
    period: TimePeriod
        Période de temps pour l'historique (1h, 24h, 7j, 30j)

    Returns
    -------
    list of StationStatusResponse
        Historique des états de la station sur la période demandée.

    Raises
    ------
    HTTPException:
        Erreur 404 si la station n'est pas trouvée.
    """
    logger.info("Historique de la station")
    return station_service.get_station_history(station_id, period)


@router.post("/recommendations", response_model=list[StationRecommendationResponse])
def get_nearby_recommendations(
    payload: StationRecommendationRequest,
    station_service: StationService = Depends(get_station_service),
) -> Any:
    """
    Recommande des stations à proximité d'une position donnée.

    Parameters
    ----------
    payload: StationRecommendationRequest
        Critères de recherche pour les stations recommandées (position,
        rayon, capacité opérationnelle, état, score min, type de vélo: all, mechanical, electric).

    Returns
    -------
    list of StationRecommendationResponse
        Liste des stations recommandées, avec leurs informations
        pertinentes (distance, disponibilité, type de vélo, etc.).
    """
    logger.info("Proposition de stations à proximité")
    return station_service.get_nearby_recommendations(payload)
