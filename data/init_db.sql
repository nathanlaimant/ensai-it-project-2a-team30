

DROP TABLE IF EXISTS vehicle_type CASCADE;
CREATE TABLE vehicle_type(
    vehicle_type_id TEXT PRIMARY KEY,
    form_factor TEXT NOT NULL CHECK (form_factor IN (
        'bicycle', 'cargo_bicycle', 'car', 'moped', 
        'scooter', 'scooter_standing', 'scooter_seated', 'other'
    )),
    rider_capacity INT,
    cargo_volume_capacity INT,
    cargo_load_capacity INT,
    propulsion_type TEXT NOT NULL CHECK (propulsion_type IN (
        'human', 'electric_assist', 'electric', 'combustion', 
        'combustion_diesel', 'hybrid', 'plug_in_hybrid', 'hydrogen_fuel_cell'
    )),
    max_range_meters REAL,
    name TEXT,
    return_constraint TEXT CHECK (return_constraint IN (
        'free_floating', 'roundtrip_station', 'any_station', 'hybrid'
    ))
);

DROP TABLE IF EXISTS system_information CASCADE;
CREATE TABLE system_information(
    system_id TEXT PRIMARY KEY,
    language TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT,
    start_date DATE,
    phone_number TEXT,
    email TEXT,
    timezone TEXT NOT NULL
);

DROP TABLE IF EXISTS station_information CASCADE;
CREATE TABLE station_information(
    station_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    adress TEXT,
    is_virtual_station BOOLEAN,
    station_area JSONB,
    contact_phone TEXT,
    capacity INT,
    is_charging_station BOOLEAN
);

DROP TABLE IF EXISTS station_virtual_capacity CASCADE;
CREATE TABLE station_virtual_capacity (
    station_id TEXT NOT NULL REFERENCES station_information(station_id) ON DELETE CASCADE,
    vehicle_type_id TEXT NOT NULL REFERENCES vehicle_type(vehicle_type_id) ON DELETE CASCADE,
    capacity INTEGER NOT NULL,
    PRIMARY KEY (station_id, vehicle_type_id)
);

DROP TABLE IF EXISTS station_status CASCADE;
CREATE TABLE station_status (
    station_status_id BIGSERIAL PRIMARY KEY,
    station_id TEXT NOT NULL REFERENCES station_information(station_id) ON DELETE CASCADE,
    num_bikes_available INTEGER NOT NULL,
    num_bikes_disabled INTEGER,
    num_docks_available INTEGER,
    num_docks_disabled INTEGER,
    operational_capacity INTEGER NOT NULL,
    is_installed BOOLEAN NOT NULL,
    is_renting BOOLEAN NOT NULL,
    is_returning BOOLEAN NOT NULL,
    last_reported TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vehicle_types_available JSONB,
    vehicle_docks_available JSONB,
    station_state TEXT NOT NULL CHECK (station_state IN ('FULL', 'EMPTY', 'FUNCTIONAL'))
);

