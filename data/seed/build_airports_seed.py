"""Build data/seed/airports_seed.json from OurAirports' raw airports.csv/countries.csv.

Scope: airports with a valid 4-letter ICAO code (icao_code column, all letters)
and a type of large/medium/small_airport or seaplane_base (excludes heliport,
balloonport, closed). See memory/project_airports_import.md for the reasoning
- an airport without a real ICAO code is essentially always an unpaved/private
strip with no instrument approach, which no airline or business-aviation
aircraft in scope would plausibly serve.

Timezone isn't in OurAirports data, so it's computed from lat/lon via
timezonefinder rather than joined from a second (staler, sparser) dataset.
"""
import csv
import json
import re
from pathlib import Path

from timezonefinder import TimezoneFinder

RAW_DIR = Path(__file__).resolve().parent / "raw"
OUT_PATH = Path(__file__).resolve().parent / "airports_seed.json"

ICAO_PATTERN = re.compile(r"^[A-Z]{4}$")
EXCLUDED_TYPES = {"heliport", "balloonport", "closed"}

NAME_SUFFIXES = re.compile(
    r"\s+(Airport|Airfield|Airstrip|Aerodrome|Air ?Base|Station)s?$", re.IGNORECASE
)


def fallback_city(name: str) -> str:
    """Derive a city name from the airport name when municipality is blank."""
    stripped = NAME_SUFFIXES.sub("", name).strip()
    return stripped or name


def main() -> None:
    countries = {}
    with (RAW_DIR / "countries.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            countries[row["code"]] = row["name"]

    tf = TimezoneFinder()
    rows = []
    skipped_no_tz = 0

    with (RAW_DIR / "airports.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            icao = row["icao_code"]
            if not ICAO_PATTERN.match(icao):
                continue
            if row["type"] in EXCLUDED_TYPES:
                continue

            lat = float(row["latitude_deg"])
            lon = float(row["longitude_deg"])
            tz = tf.timezone_at(lat=lat, lng=lon)
            if tz is None:
                skipped_no_tz += 1
                continue

            rows.append(
                {
                    "icao": icao,
                    "iata": row["iata_code"] or None,
                    "name": row["name"],
                    "city": row["municipality"] or fallback_city(row["name"]),
                    "country": countries[row["iso_country"]],
                    "latitude": lat,
                    "longitude": lon,
                    "timezone": tz,
                }
            )

    OUT_PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(rows)} airports to {OUT_PATH}")
    if skipped_no_tz:
        print(f"Skipped {skipped_no_tz} airports with no timezonefinder match (likely open ocean coordinates)")


if __name__ == "__main__":
    main()
