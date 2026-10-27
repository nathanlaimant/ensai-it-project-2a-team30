"""Gère les consultations de stations."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from business_object.station_information import StationInformation
from dependencies.service import get_station_service
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


@router.get("/{station_id}", response_model=StationInformation, tags=["Stations"])
async def get_station_info(station_id: str, station_service=Depends(get_station_service)) -> Any:
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

    Raises
    ------
    HTTPException: Erreur 404 si la station n'est pas trouvée
    """
    logger.info("Recherche d'une station à partir de son identifiant")
    station = station_service.get_by_id(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station (id={station_id}) non trouvée.")
    return station


@router.get("/", response_model=list[StationInformation], tags=["Stations"])
async def list_stations(payload: dict, station_service=Depends(get_station_service)) -> Any:
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
    logger.info("Recherche d'une station à partir de paramètres donnés ou non")
    stations = station_service.list_stations(payload)
    return stations


async def get_station_current_status(station_id: str) -> dict:
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


async def get_station_history(payload: dict) -> list[dict]:
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
