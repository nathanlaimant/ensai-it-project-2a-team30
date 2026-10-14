from business_object.station_status_hourly import StationStatusHourly


class StationReliabilityCalculator:
    """Calcule la fiabilité d'une station à partir de ses statistiques horaires."""

    def calculate_reliability(
        self, station_status_hourly: StationStatusHourly
    ) -> float:
        """
        Calcule le score de fiabilité d'une station.
 
        Parameters
        ----------
        station_status_hourly : StationStatusHourly
            Agrégation horaire des statistiques de la station, utilisée
            pour calculer son score de fiabilité.
 
        Returns
        -------
        float
            Score de fiabilité de la station.
        """
        raise NotImplementedError
