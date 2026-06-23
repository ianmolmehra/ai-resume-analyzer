"""Auto-initialises SQLite on first import. Import this at the top of every page."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

_initialised = False

def get_db_session():
    global _initialised
    from database import SessionLocal, init_db
    if not _initialised:
        init_db()
        _initialised = True
    return SessionLocal()
