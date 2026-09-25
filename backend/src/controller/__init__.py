"""
Regroupe l'ensemble des contrôleurs exposant les endpoints de
l'application de gestion de stations de vélos : administration des
utilisateurs, authentification et profil, stations favorites,
recommandations de stations à proximité, et consultation des stations.
"""

from .admin_controller import AdminController
from .auth_and_user_controller import AuthAndUserController
from .favorite_station_controller import FavoriteStationController
from .recommendation_controller import RecommendationController
from .station_controller import StationController

__all__ = [
    "AdminController",
    "AuthAndUserController",
    "FavoriteStationController",
    "RecommendationController",
    "StationController",
]
