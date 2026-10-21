from enum import StrEnum


class StationState(StrEnum):
    """
    Représente l'état global d'une station de vélos.

    Attributes
    ----------
    FULL : str
        La station est pleine (aucune borne disponible pour déposer un vélo).
    EMPTY : str
        La station est vide (aucun vélo disponible à la location).
    FUNCTIONAL : str
        La station est fonctionnelle (vélos et bornes disponibles).
    """

    FULL = "FULL"
    EMPTY = "EMPTY"
    FUNCTIONAL = "FUNCTIONAL"

