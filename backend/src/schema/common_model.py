"""Common request and response models exposed by the API."""

from enum import StrEnum

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Confirmation retournée après une opération modifiant l'état du système.

    Parameters
    ----------
    status : str
        Statut de l'opération effectuée. Peut être "success" ou "error".
    message : str
        Message décrivant le résultat de l'opération effectuée.

    Returns
    -------
    MessageResponse
        Instance représentant la confirmation renvoyée.
    """

    status: str = "success"
    message: str


class TimePeriod(StrEnum):
    une_heure = "1h"
    vingt_quatre_heures = "24h"
    sept_jours = "7j"
    trente_jours = "30j"
