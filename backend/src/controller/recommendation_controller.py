from ..service import RecommendationService


class RecommendationController:
    """Handle recommendation requests."""

    def __init__(self, recommendation_service: RecommendationService):
        self.recommendation_service = recommendation_service

    def get_nearby_recommendations(self, payload: dict) -> list[dict]:
        """Get nearby recommendations."""
        raise NotImplementedError
