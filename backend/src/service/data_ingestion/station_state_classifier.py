from ..business_object import StationStatus


class StationStateClassifier:
    """Classify a station state."""

    def classify_state(self, status: StationStatus) -> str:
        """Return the state for a station status."""
        raise NotImplementedError
