"""Handle administration requests."""

from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from dependencies import get_current_user, get_user_service
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter(prefix="/admin", tags=["Administration"])

logger = get_logger(__name__)


class AdminController:
    """
    Gère les requêtes des administrateurs.
    
    Parameters
    ----------
    user_service : Any
        Service applicatif gérant la logique métier liée
        aux utilisateurs.
    """


    def list_users(self, payload: dict) -> list[User]:
        """
        Liste les utilisateurs selon des critères de recherche.
 
        Parameters
        ----------
        payload : dict
            Critères de filtrage et/ou de pagination.
 
        Returns
        -------
        list of User
            Liste des utilisateurs correspondant aux critères.
        """
        raise NotImplementedError

    def update_user_status(self, user_id: int, is_active: bool) -> str:
        """
        Active ou désactive le compte d'un utilisateur.
 
        Parameters
        ----------
        user_id : int
            Identifiant de l'utilisateur concerné.
        is_active : bool
            Nouveau statut d'activation du compte.
 
        Returns
        -------
        str
            Message de confirmation de la mise à jour du statut.
        """
        raise NotImplementedError
