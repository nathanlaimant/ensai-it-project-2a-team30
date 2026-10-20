from business_object.station_status import StationStatus


class StationStateClassifier:
    """Classifie l'état d'une station."""

    def classify_state(self, status: StationStatus) -> str:
        """
        Détermine l'état d'une station à partir de son statut.

        Parameters
        ----------
        status : StationStatus
            Statut courant de la station à classifier.

        Returns
        -------
        str
            État de la station (ex: "FULL", "EMPTY", "FUNCTIONAL").
        """
        raise NotImplementedError
