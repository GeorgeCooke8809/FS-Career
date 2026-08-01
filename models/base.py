from pathlib import Path

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine, event

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "fs_career.db"

engine = create_engine(f"sqlite:///{DB_PATH}")


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def with_session(func):
    def wrap(*args, **kwargs):
        session = Session()

        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except:
            session.rollback()
            raise
        finally:
            session.close()