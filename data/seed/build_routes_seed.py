"""Build data/seed/routes_seed.json from OpenFlights' raw routes.dat/airlines.dat/
airports.dat/planes.dat (data/seed/openflights_raw/, jpatokal/openflights).

OpenFlights gives real airline -> route -> aircraft-type networks but no flight
numbers or durations (it's a ~2014 snapshot with no schedule data at all).
Scope and approach - see memory/project_routes_import.md:

- Only routes matched to rows already in our airlines/airports/aircraft tables
  are kept; everything else (airlines/airports/equipment we don't have) is
  dropped rather than guessed.
- Codeshares and multi-stop entries are dropped - we only want one row per
  real operated direct service.
- Where OpenFlights lists multiple equipment types for a route, only the
  first one that matches our aircraft table is used (one row per
  (airline, origin, destination), not one per aircraft variant).
- A meaningful chunk of OpenFlights equipment codes are generic family codes
  rather than real IATA variant codes (e.g. KLM's rows mostly say "330",
  "737", "777" instead of "332", "738", "77W") or codes missing from
  planes.dat entirely (e.g. "73H", "CRJ", "DH8"). GENERIC_EQUIPMENT_FALLBACK
  below maps the common ones to a representative variant already in our
  `aircraft` table - a reasonable guess, not a claim of accuracy - so these
  routes aren't dropped outright. Routes matched this way (and only these)
  get aircraft_icao_type_synthetic=True.
- distance_nm is computed via great-circle from our own airports table
  (authoritative, already in the DB) rather than OpenFlights' coordinates.
- flight_number and duration_minutes are synthesized (real-world schedules
  aren't available in bulk from any free source): flight numbers are
  assigned sequentially per airline; durations are distance divided by a
  per-aircraft-category cruise speed plus a fixed taxi/climb/descent
  buffer, rounded to the nearest 5 minutes.
"""
import csv
import json
import math
import sqlite3
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent / "openflights_raw"
OUT_PATH = Path(__file__).resolve().parent / "routes_seed.json"
DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"

EARTH_RADIUS_NM = 3440.065

CRUISE_SPEED_KT = {
    "mainline_jet": 460,
    "regional_jet": 430,
    "turboprop": 280,
    "business": 400,
}
TAXI_CLIMB_DESCENT_BUFFER_MIN = 20

# OpenFlights equipment code -> representative icao_type in our aircraft table.
# Covers generic family codes (e.g. "737", "777") and codes missing from
# planes.dat (e.g. "73H", "CRJ") that account for meaningful route volume.
# Picks a plausible mid-range variant per family; not an attempt at precision.
GENERIC_EQUIPMENT_FALLBACK = {
    # 737 family
    "737": "B737", "73H": "B738", "73W": "B737", "73C": "B733",
    "73J": "B739", "73M": "B38M", "73Q": "B733",
    # 747 family
    "747": "B744", "74E": "B744", "74H": "B748", "74M": "B744",
    # 757 / 767
    "757": "B752", "75W": "B752", "767": "B763", "76W": "B763",
    # 777 / 787
    "777": "B772", "787": "B788",
    # Airbus widebodies
    "330": "A332", "340": "A342", "380": "A388",
    # Airbus narrowbody generic
    "32S": "A320", "32A": "A320",
    # BAe 146
    "146": "B461",
    # Regional jets
    "CRJ": "CRJ9", "ERJ": "E145", "EMJ": "E145", "E75": "E75L",
    # Dash 8
    "DH8": "DH8D",
    # MD-80 / DC-9
    "M80": "MD82", "DC9": "DC93",
    # Beechcraft 1900
    "BE1": "B190",
    # Let L-410
    "L4T": "L410",
}


def haversine_nm(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(a))


def round5(x):
    return int(round(x / 5.0) * 5)


def load_db_reference():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("select icao, iata from airlines")
    our_airline_icao = set()
    our_airline_by_iata = {}
    for icao, iata in cur.fetchall():
        our_airline_icao.add(icao)
        if iata:
            our_airline_by_iata.setdefault(iata, []).append(icao)

    cur.execute("select icao, latitude, longitude from airports")
    our_airports = {icao: (lat, lon) for icao, lat, lon in cur.fetchall()}

    cur.execute(
        "select aircraft.icao_type, aircraft_families.category "
        "from aircraft join aircraft_families on aircraft.family_id = aircraft_families.id"
    )
    our_aircraft_category = {icao_type: cat for icao_type, cat in cur.fetchall()}

    con.close()
    return our_airline_icao, our_airline_by_iata, our_airports, our_aircraft_category


def load_openflights_airlines(our_airline_icao, our_airline_by_iata):
    mapping = {}
    with (RAW_DIR / "airlines.dat").open(encoding="utf-8") as f:
        for row in csv.reader(f):
            of_id, name, alias, iata, icao, callsign, country, active = row
            if icao and icao != "\\N" and icao in our_airline_icao:
                mapping[of_id] = icao
            elif iata and iata != "\\N" and len(our_airline_by_iata.get(iata, [])) == 1:
                mapping[of_id] = our_airline_by_iata[iata][0]
    return mapping


def load_openflights_airports(our_airports):
    mapping = {}
    with (RAW_DIR / "airports.dat").open(encoding="utf-8") as f:
        for row in csv.reader(f):
            of_id, name, city, country, iata, icao = row[0], row[1], row[2], row[3], row[4], row[5]
            if icao and icao != "\\N" and icao in our_airports:
                mapping[of_id] = icao
    return mapping


def load_openflights_planes(our_aircraft_category):
    mapping = {}
    with (RAW_DIR / "planes.dat").open(encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            name, iata, icao = row[0], row[1], row[2]
            if icao and icao in our_aircraft_category:
                mapping[iata] = icao
    return mapping


def main():
    our_airline_icao, our_airline_by_iata, our_airports, our_aircraft_category = load_db_reference()
    airline_map = load_openflights_airlines(our_airline_icao, our_airline_by_iata)
    airport_map = load_openflights_airports(our_airports)
    plane_map = load_openflights_planes(our_aircraft_category)

    for code, icao_type in GENERIC_EQUIPMENT_FALLBACK.items():
        assert icao_type in our_aircraft_category, f"fallback target {icao_type!r} for {code!r} not in aircraft table"

    seen = set()
    routes = []
    flight_number_counters = {}
    skipped = {"codeshare": 0, "stops": 0, "airline": 0, "airport": 0, "equipment": 0, "duplicate": 0}
    fallback_used = 0

    with (RAW_DIR / "routes.dat").open(encoding="utf-8") as f:
        for row in csv.reader(f):
            (airline, airline_id, src, src_id, dst, dst_id, codeshare, stops, equipment) = row

            if codeshare == "Y":
                skipped["codeshare"] += 1
                continue
            if stops != "0":
                skipped["stops"] += 1
                continue

            airline_icao = airline_map.get(airline_id)
            if not airline_icao:
                skipped["airline"] += 1
                continue

            origin_icao = airport_map.get(src_id)
            dest_icao = airport_map.get(dst_id)
            if not origin_icao or not dest_icao or origin_icao == dest_icao:
                skipped["airport"] += 1
                continue

            aircraft_icao_type = None
            aircraft_icao_type_synthetic = False
            codes = equipment.split()
            for code in codes:
                if code in plane_map:
                    aircraft_icao_type = plane_map[code]
                    break
            if not aircraft_icao_type:
                for code in codes:
                    if code in GENERIC_EQUIPMENT_FALLBACK:
                        aircraft_icao_type = GENERIC_EQUIPMENT_FALLBACK[code]
                        aircraft_icao_type_synthetic = True
                        fallback_used += 1
                        break
            if not aircraft_icao_type:
                skipped["equipment"] += 1
                continue

            key = (airline_icao, origin_icao, dest_icao)
            if key in seen:
                skipped["duplicate"] += 1
                continue
            seen.add(key)

            lat1, lon1 = our_airports[origin_icao]
            lat2, lon2 = our_airports[dest_icao]
            distance_nm = haversine_nm(lat1, lon1, lat2, lon2)

            category = our_aircraft_category[aircraft_icao_type]
            speed = CRUISE_SPEED_KT[category]
            duration_minutes = round5(
                distance_nm / speed * 60 + TAXI_CLIMB_DESCENT_BUFFER_MIN
            )
            duration_minutes = max(duration_minutes, 25)

            n = flight_number_counters.get(airline_icao, 0) + 1
            flight_number_counters[airline_icao] = n
            flight_number = str(100 + n)

            routes.append(
                {
                    "airline_icao": airline_icao,
                    "origin_icao": origin_icao,
                    "destination_icao": dest_icao,
                    "aircraft_icao_type": aircraft_icao_type,
                    "flight_number": flight_number,
                    "distance_nm": round(distance_nm, 1),
                    "duration_minutes": duration_minutes,
                    "flight_number_synthetic": True,
                    "schedule_synthetic": True,
                    "aircraft_icao_type_synthetic": aircraft_icao_type_synthetic,
                }
            )

    OUT_PATH.write_text(json.dumps(routes, indent=2), encoding="utf-8")
    print(f"Wrote {len(routes)} routes to {OUT_PATH}")
    print(f"Airlines matched: {len(set(airline_map.values()))} / {len(our_airline_icao)}")
    print(f"Routes using fallback (synthesized) equipment guess: {fallback_used}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
