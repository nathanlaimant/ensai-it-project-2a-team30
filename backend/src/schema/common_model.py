"""Common request and response models exposed by the API."""

from enum import Enum

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Confirmation retournée après une opération modifiant l'état du système.

    Parameters
    ----------
    message : str
        Message décrivant le résultat de l'opération effectuée.

    Returns
    -------
    MessageResponse
        Instance représentant la confirmation renvoyée.
    """

    message: str


class TimePeriod(str, Enum):
    une_heure = "1h"
    vingt_quatre_heures = "24h"
    sept_jours = "7j"
    trente_jours = "30j"
