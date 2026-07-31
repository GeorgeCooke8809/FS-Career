"""Download airline logos for airlines that have at least one route.

Pulls from Kiwi.com's public airline-logo CDN (images.kiwi.com/airlines/{size}/{IATA}.png),
keyed by IATA code. Airlines with no route are skipped entirely (per project decision -
~400 route-less airlines aren't in scope). Airlines with no IATA code are reported as
unresolvable via this source and left for manual follow-up.

Saves successful downloads to data/logos/{icao}.png (ICAO used as filename since it's
the airlines table primary key and always present) and sets airlines.has_logo. Writes
a JSON report of hits/misses ordered by route count so the highest-traffic gaps can be
chased down manually.
"""
import hashlib
import json
import time
from pathlib import Path

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from models import Airline

DB_PATH = Path(__file__).resolve().parent.parent / "fs_career.db"
LOGO_DIR = Path(__file__).resolve().parent.parent / "logos"
REPORT_PATH = Path(__file__).resolve().parent / "logo_fetch_report.json"

CDN_URL = "https://images.kiwi.com/airlines/128x128/{iata}.png"
MIN_VALID_BYTES = 600  # kiwi's "no logo" error page is ~567 bytes
# md5 of kiwi's generic grey-plane "no logo available" icon - served with a 200,
# so byte-size alone doesn't catch it.
PLACEHOLDER_MD5 = "946bca53c7e1c56d66a7f13e69520aee"


def fetch_route_airlines() -> list[dict]:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT a.icao, a.iata, a.name, COUNT(r.id) as route_count
                FROM airlines a
                JOIN routes r ON r.airline_icao = a.icao
                GROUP BY a.icao
                ORDER BY route_count DESC
                """
            )
        ).all()
    return [dict(r._mapping) for r in rows]


def main() -> None:
    LOGO_DIR.mkdir(exist_ok=True)
    airlines = fetch_route_airlines()
    print(f"{len(airlines)} airlines have at least one route.")

    hits, misses, no_iata = [], [], []
    session = requests.Session()

    for a in airlines:
        icao, iata, name, count = a["icao"], a["iata"], a["name"], a["route_count"]
        dest = LOGO_DIR / f"{icao}.png"
        if dest.exists():
            hits.append(a)
            continue
        if not iata:
            no_iata.append(a)
            continue

        url = CDN_URL.format(iata=iata)
        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
        except requests.RequestException as e:
            misses.append({**a, "reason": str(e)})
            continue

        is_placeholder = hashlib.md5(resp.content).hexdigest() == PLACEHOLDER_MD5
        if resp.status_code == 200 and len(resp.content) >= MIN_VALID_BYTES and not is_placeholder:
            dest.write_bytes(resp.content)
            hits.append(a)
        elif is_placeholder:
            misses.append({**a, "reason": "placeholder image (no real logo on CDN)"})
        else:
            misses.append({**a, "reason": f"status={resp.status_code} bytes={len(resp.content)}"})

        time.sleep(0.05)

    report = {"hits": len(hits), "misses": misses, "no_iata": no_iata}
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    have = {f.stem for f in LOGO_DIR.glob("*.png")}
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as db_session:
        for a in db_session.query(Airline).all():
            a.has_logo = a.icao in have
        db_session.commit()

    print(f"Downloaded/present: {len(hits)}")
    print(f"Missing (had IATA, CDN had nothing): {len(misses)}")
    print(f"Missing (no IATA code at all): {len(no_iata)}")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
