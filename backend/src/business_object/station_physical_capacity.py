class StationPhysicalCapacity:
    """
    Décrit la capacité physique d'une station pour un certain type de vehicule.

    Parameters
    ----------
    station_id : str
        Identifiant unique de la station.
    vehicle_type_id : str
        Identifiant unique d'un type de vehicule.
    dock_count : int
        Le nombre de bornes physiques dans une station.
    """

    def __init__(self, station_id: str, vehicle_type_id: str, dock_count: int):
        self.station_id = station_id
        self.vehicle_type_id = vehicle_type_id
        self.dock_count = dock_count
