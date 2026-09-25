from pydantic import BaseModel


class StationVirtualCapacity(BaseModel):
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
 
    Returns
    -------
    StationVirtualCapacity
        Instance représentant la capacité virtuelle.
    """
    
    station_id: str
    vehicle_type_id: str
    capacity: int
