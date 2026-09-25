from pydantic import BaseModel


class StationPhysicalCapacity(BaseModel):
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
    
    Returns
    -------
    StationPhysicalCapacity
        Instance représentant la capacité physique.
    """

    station_id: str
    vehicle_type_id: str
    dock_count: int
