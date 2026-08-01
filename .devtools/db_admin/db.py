from sqlalchemy.orm import Session, sessionmaker

from models.base import REPO_ROOT, engine

LOGOS_DIR = REPO_ROOT / "data" / "logos"

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Session:
    return SessionLocal()
