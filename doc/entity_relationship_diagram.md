# ERD

```mermaid
erDiagram
 direction LR
    %% ═══════════════════════════════════════════════
    %% SYSTEM INFORMATION
    %% ═══════════════════════════════════════════════

    system_information {
        string system_id PK
        string language
        string name
        string url "Nullable"
        date start_date "Nullable"
        string phone_number "Nullable"
        string email "Nullable"
        string timezone
    }

    %% ═══════════════════════════════════════════════
    %% VEHICLE TYPES
    %% ═══════════════════════════════════════════════

    vehicle_type {
        string vehicle_type_id PK
        string form_factor
        integer rider_capacity "Nullable"
        integer cargo_volume_capacity "Nullable"
        integer cargo_load_capacity "Nullable"
        string propulsion_type
        real max_range_meters "Nullable"
        string name "Nullable"
        string return_constraint "Nullable"
    }

    %% ═══════════════════════════════════════════════
    %% STATION INFORMATION
    %% ═══════════════════════════════════════════════

    station_information {
        string station_id PK
        string name
        string short_name "Nullable"
        real lat
        real lon
        string address "Nullable"
        boolean is_virtual_station "Nullable"
        json station_area "Nullable"
        string contact_phone "Nullable"
        integer capacity "Nullable"
        boolean is_charging_station "Nullable"
    }

    station_virtual_capacity {
        string station_id PK,FK
        string vehicle_type_id PK,FK
        integer capacity
    }

    station_physical_capacity {
        string station_id PK,FK
        string vehicle_type_id PK,FK
        integer dock_count
    }

    station_information ||--o{ station_virtual_capacity : "has"
    station_information ||--o{ station_physical_capacity : "has"
    station_virtual_capacity }o--|| vehicle_type : "is available at"
    station_physical_capacity }o--|| vehicle_type : "is available at"

    %% ═══════════════════════════════════════════════
    %% STATION STATUS
    %% ═══════════════════════════════════════════════

    station_status {
        integer station_status_id PK
        string station_id FK
        integer num_bikes_available
        integer num_bikes_disabled "Nullable"
        integer num_docks_available "Nullable"
        integer num_docks_disabled "Nullable"
        integer operational_capacity
        boolean is_installed
        boolean is_renting
        boolean is_returning
        timestampt last_reported
        json vehicle_types_available "Nullable"
        json vehicle_docks_available "Nullable"
        string station_state
    }

    station_information ||--o{ station_status : "has"

    %% ═══════════════════════════════════════════════
    %% STATION_STATUS_HOURLY
    %% ═══════════════════════════════════════════════

    station_status_hourly {
        string station_id PK,FK
        timestampt bucket_hour PK
        integer sample_count
        real avg_operational_capacity
        real avg_num_bikes_available
        real avg_num_docks_available
        integer empty_duration_sec
        integer full_duration_sec
        integer empty_events_cnt
        integer full_events_cnt
        real reliability_score
    }

    station_status_hourly }o--|| station_information : "has"

    %% ═══════════════════════════════════════════════
    %% USER
    %% ═══════════════════════════════════════════════

    user {
        integer user_id PK
        string username 
        string password_hashed
        string email
        string role
        boolean is_active
        timestampt created_at
        timestampt updated_at
        string access_token
    }

    user_favorite_station {
        integer user_id PK,FK
        string station_id PK,FK
        timestampt created_at
    }

    user ||--o{ user_favorite_station : "favorites"
    user_favorite_station }o--|| station_information : "is favorited by"
```
