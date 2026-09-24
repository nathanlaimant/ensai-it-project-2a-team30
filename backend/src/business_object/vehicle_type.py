from pydantic import BaseModel


class VehicleType(BaseModel):
    """
    Décrit un type de véhicule disponible dans le système.
 
    Parameters
    ----------
    vehicle_type_id : str
        Identifiant unique du type de véhicule (ex: "EBIKE").
    form_factor : str
        Forme du véhicule (ex: "bicycle", "cargo_bicycle", "scooter").
    rider_capacity : int
        Nombre maximum de personnes transportables.
    cargo_volume_capacity : int
        Volume de chargement maximal (en litres) pour les véhicules cargo.
    cargo_load_capacity : int
        Poids de chargement maximal (en kg) pour les véhicules cargo.
    propulsion_type : str
        Type de propulsion (ex: "human", "electric_assist", "electric").
    max_range_meters : float
        Autonomie maximale en mètres pour les véhicules à propulsion électrique.
    name : str
        Nom lisible du type de véhicule.
    return_constraint : str
        Contrainte de retour du véhicule (ex: "any_station", "roundtrip_station").
 
    Returns
    -------
    VehicleType
        Instance représentant le type de véhicule.
    """

    vehicle_type_id: str
    form_factor: str
    rider_capacity: int
    cargo_volume_capacity: int
    cargo_load_capacity: int
    propulsion_type: str
    max_range_meters: float
    name: str
    return_constraint: str
