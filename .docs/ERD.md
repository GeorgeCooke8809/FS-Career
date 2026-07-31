# ERD — Airlines & Routes

```mermaid
erDiagram
    AIRLINES ||--o{ ROUTES : "operates"
    AIRCRAFT ||--o{ ROUTES : "flies"
    AIRCRAFT_FAMILIES ||--o{ AIRCRAFT : "groups"
    AIRPORTS ||--o{ ROUTES : "origin of"
    AIRPORTS ||--o{ ROUTES : "destination of"

    AIRPORTS {
        string icao PK
        string iata
        string name
        string city
        string country
        float latitude
        float longitude
        string timezone
    }

    AIRLINES {
        string icao PK
        string iata
        string name
        string callsign
        string country
    }

    AIRCRAFT_FAMILIES {
        int id PK
        string name
        string manufacturer
        string category
    }

    AIRCRAFT {
        string icao_type PK
        string name
        int family_id FK
    }

    ROUTES {
        int id PK
        string airline_icao FK
        string origin_icao FK
        string destination_icao FK
        string aircraft_icao_type FK
        string flight_number
        float distance_nm
        time departure_time_utc
        int duration_minutes
    }
```

`routes` is the central fact table. Both `origin_icao` and `destination_icao` are foreign keys to `airports.icao` — the two relationship lines above represent the same table referenced twice (a route's origin and destination). See `.docs/DATA_DICTIONARY.md` for full column-level detail.
