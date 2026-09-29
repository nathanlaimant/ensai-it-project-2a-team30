class StationVirtualCapacity:
    """
    Décrit la capacité virtuelle d'une station pour un type de véhicule donné.

    Parameters
    ----------
    station_id : str
        Identifiant de la station concernée.
    vehicle_type_id : str
        Identifiant du type de véhicule concerné.
    capacity : int
        Capacité virtuelle allouée à ce type de véhicule dans la station.
    """

    def __init__(self, station_id: str, vehicle_type_id: str, capacity: int):
        self.station_id = station_id
        self.vehicle_type_id = vehicle_type_id
        self.capacity = capacity
