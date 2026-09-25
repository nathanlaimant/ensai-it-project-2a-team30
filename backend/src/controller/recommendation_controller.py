from ..service import RecommendationService


class RecommendationController:
    """
    Gère les recommandations de stations pour l'utilisateur.
    
    Parameters
    ----------
    recommendation_service : Any
        Service applicatif gérant la logique
        métier de recommandation de stations.
    """

    def __init__(self, recommendation_service: RecommendationService):
        self.recommendation_service = recommendation_service

    def get_nearby_recommendations(self, payload: dict) -> list[dict]:
        """Get nearby recommendations."""
        raise NotImplementedError
