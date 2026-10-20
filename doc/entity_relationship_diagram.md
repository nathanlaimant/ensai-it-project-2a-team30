# ERD

La table SystemInformation n'est reliée à aucune autre table car :

- Métadonnées globales (singleton) : Cette table stocke des informations générales décrivant le réseau dans son ensemble (nom du service, contacts, fuseau horaire, URL). Elle n'a vocation à contenir qu'un enregistrement unique représentant l'opérateur.
- Périmètre mono-réseau (absence de multi-tenant) : L'application étant dédiée à la gestion d'un unique réseau de vélos en libre-service, propager une clé étrangère system_id vers chaque station ou entité opérationnelle introduirait une redondance inutile dans le schéma relationnel.

```mermaid
erDiagram
 direction LR
    %% ═══════════════════════════════════════════════
    %% SYSTEM INFORMATION
    %% ═══════════════════════════════════════════════

    system_information {
        text system_id PK
        text language
        text name
        text url "Nullable"
        date start_date "Nullable"
        text phone_number "Nullable"
        text email "Nullable"
        text timezone
    }

    %% ═══════════════════════════════════════════════
    %% STATION INFORMATION
    %% ═══════════════════════════════════════════════

    station_information {
        text station_id PK
        text name
        text short_name "Nullable"
        double_precision lat
        double_precision lon
        text address "Nullable"
        boolean is_virtual_station "Nullable"
        jsonb station_area "Nullable"
        text contact_phone "Nullable"
        integer capacity "Nullable"
        boolean is_charging_station "Nullable"
    }

    %% ═══════════════════════════════════════════════
    %% STATION STATUS
    %% ═══════════════════════════════════════════════

    station_status {
        bigint station_status_id PK
        text station_id FK
        integer num_bikes_available
        integer num_bikes_disabled "Nullable"
        integer num_docks_available "Nullable"
        integer num_docks_disabled "Nullable"
        integer operational_capacity
        timestamptz last_reported
        jsonb vehicle_types_available "Nullable"
        jsonb vehicle_docks_available "Nullable"
        text station_state
    }

    station_information ||--o{ station_status : "has"

    %% ═══════════════════════════════════════════════
    %% STATION_STATUS_HOURLY
    %% ═══════════════════════════════════════════════

    station_status_hourly {
        text station_id PK,FK
        timestamptz bucket_hour PK
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
        text username 
        text password_hashed
        text email
        text role
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
        text access_token
    }

    user_favorite_station {
        integer user_id PK,FK
        text station_id PK,FK
        timestamptz created_at
    }

    user ||--o{ user_favorite_station : "favorites"
    user_favorite_station }o--|| station_information : "is favorited by"
```
