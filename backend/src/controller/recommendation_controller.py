"""Gère les recommandations de stations pour l'utilisateur."""

from service.recommendation_service import RecommendationService


def get_nearby_recommendations(payload: dict) -> list[dict]:
    """Get nearby recommendations."""
    raise NotImplementedError
