class VehicleType:
    """
    Décrit un type de véhicule disponible dans le système.

    Parameters
    ----------
    vehicle_type_id : str | None
        Identifiant unique du type de véhicule. Non-nullable, mais peut être None si l'objet n'a pas été persistée.
    form_factor : str
        Forme du véhicule (ex: "bicycle", "cargo_bicycle", "scooter").
    rider_capacity : int | None
        Nombre maximum de personnes transportables. Nullable.
    cargo_volume_capacity : int | None
        Volume de chargement maximal (en litres) pour les véhicules cargo. Nullable.
    cargo_load_capacity : int | None
        Poids de chargement maximal (en kg) pour les véhicules cargo. Nullable.
    propulsion_type : str
        Type de propulsion (ex: "human", "electric_assist", "electric").
    max_range_meters : float | None
        Autonomie maximale en mètres pour les véhicules à propulsion électrique. Nullable.
    name : str | None
        Nom lisible du type de véhicule. Nullable.
    return_constraint : str | None
        Contrainte de retour du véhicule (ex: "any_station", "roundtrip_station"). Nullable.
    """

    def __init__(
        self,
        form_factor: str,
        rider_capacity: int | None,
        cargo_volume_capacity: int | None,
        cargo_load_capacity: int | None,
        propulsion_type: str,
        max_range_meters: float | None,
        name: str | None,
        return_constraint: str | None,
        vehicle_type_id: str | None = None,
    ):
        self.vehicle_type_id = vehicle_type_id
        self.form_factor = form_factor
        self.rider_capacity = rider_capacity
        self.cargo_volume_capacity = cargo_volume_capacity
        self.cargo_load_capacity = cargo_load_capacity
        self.propulsion_type = propulsion_type
        self.max_range_meters = max_range_meters
        self.name = name
        self.return_constraint = return_constraint
