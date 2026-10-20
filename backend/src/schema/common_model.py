"""Common request and response models exposed by the API."""

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
