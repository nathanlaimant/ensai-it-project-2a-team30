from business_object.station_status import StationStatus


class StationStateDurationCalculator:
    """Calcule la durée passée par une station dans chacun de ses états."""

    def calculate_durations(self, station_status: list[StationStatus]) -> list[dict]:
        """
        Calcule les durées passées dans chaque état à partir d'un historique de statuts.

        Parameters
        ----------
        station_status : list of StationStatus
            Historique chronologique des statuts d'une station, à partir
            duquel sont déduites les durées passées dans chaque état
            (ex: "FULL", "EMPTY", "FUNCTIONAL").

        Returns
        -------
        list of dict
            Liste des durées calculées par état.
        """
        raise NotImplementedError
