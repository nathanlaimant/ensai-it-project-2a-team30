from business_object.station_status import StationStatus


class StationCapacityCalculator:
    """Calcule la capacité opérationnelle d'une station."""

    def calculate_capacity(self, station_status: StationStatus) -> int:
        """
        Calcule la capacité opérationnelle d'une station à partir de son statut.

        Parameters
        ----------
        station_status : StationStatus
            Statut courant de la station, à partir duquel est déduite
            la capacité opérationnelle.

        Returns
        -------
        int
            Capacité opérationnelle de la station.
        """
        raise NotImplementedError
