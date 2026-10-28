"""Gère les consultations de stations."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from dependencies.service import get_station_service
from schema.common_model import TimePeriod
from schema.station_model import (
    StationInfoResponse,
    StationSearchRequest,
    StationStatusResponse,
)
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


@router.get("/{station_id}", response_model=StationInfoResponse, tags=["Stations"])
async def get_station_info(
    station_id: str, station_service=Depends(get_station_service)
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
            status_code=404, detail="Station (id={station_id}) non trouvée."
        )
    # On returne l'objet StationInformation, qui sera automatiquement converti
    # en StationInfoResponse par la configuration from_attributes=True du modèle Pydantic.
    return station


@router.post("/", response_model=list[StationInfoResponse], tags=["Stations"])
async def list_stations(
    payload: StationSearchRequest, station_service=Depends(get_station_service)
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
    stations = station_service.list_stations(payload)
    # On returne la liste des StationInformation, qui sera automatiquement converti
    # en liste de StationInfoResponse.
    return stations


@router.get(
    "/{station_id}/status", response_model=StationStatusResponse, tags=["Stations"]
)
async def get_station_current_status(
    station_id: str, station_service=Depends(get_station_service)
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
    # Puis, les convertit en StationStatusResponse. Ce classe peut être modifiée si nécessaire !
    statut = station_service.get_station_current_status(station_id)
    if not statut:
        raise HTTPException(
            status_code=404, detail="Station (id={station_id}) non trouvée."
        )
    return statut


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
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    station_service=Depends(get_station_service),
) -> Any:
    """
    Récupère l'historique de l'état d'une station sur une période donnée.

    Parameters
    ----------
    station_id: str
        Identifiant de la station
    period: TimePeriod
        Période de temps pour l'historique (1h, 24h, 7j, 30j)
    page: int
        Numéro de page pour la pagination (1 par défaut)
    size: int
        Nombre d'éléments par page (10 par défaut, maximum 100)

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
    # L'idée est qu'on limite les choix de periode à : 1h, 24h, 7 jours et 30 jours.
    # Si 1h : on recupère seulement les StationStatus, sans score de fiabilité.
    # Sinon : on recupère seulement les StationStatusHourly.
    # Puis, les convertit en une liste de StationStatusResponse.
    # Tu peux revenir à la methode précédente (avec start_time et end_time) si tu veux !
    history = station_service.get_station_history(station_id, start_time, end_time)
    if not history:
        raise HTTPException(
            status_code=404, detail="Station (id={station_id}) non trouvée."
        )
    return history
