import sqlite3
import sys
from pathlib import Path

from config import DB_PATH, DATA_DIR

if getattr(sys, "frozen", False):
    SCHEMA_PATH = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent)) / "database" / "schema.sql"
else:
    SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)
        _migrate_materi_unique_constraint(conn)
        conn.commit()


def _migrate_materi_unique_constraint(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table' AND name = 'materi'
        """
    ).fetchone()
    if row is None or "UNIQUE(semester_id, nama)" not in (row["sql"] or ""):
        return

    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("PRAGMA legacy_alter_table = ON")
    conn.execute("ALTER TABLE materi RENAME TO materi_old")
    conn.execute(
        """
        CREATE TABLE materi (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            semester_id      INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
            nama             TEXT NOT NULL,
            aspek            TEXT NOT NULL CHECK(aspek IN ('hafalan', 'praktik')),
            poin_pengurangan REAL NOT NULL CHECK(poin_pengurangan > 0),
            urutan           INTEGER NOT NULL DEFAULT 0,
            is_aktif         INTEGER NOT NULL DEFAULT 1,
            UNIQUE(semester_id, nama, aspek)
        )
        """
    )
    conn.execute(
        """
        INSERT INTO materi(id, semester_id, nama, aspek, poin_pengurangan, urutan, is_aktif)
        SELECT id, semester_id, nama, aspek, poin_pengurangan, urutan, is_aktif
        FROM materi_old
        """
    )
    conn.execute("DROP TABLE materi_old")
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_materi_semester
            ON materi(semester_id, is_aktif)
        """
    )
    conn.execute("PRAGMA legacy_alter_table = OFF")
    conn.execute("PRAGMA foreign_keys = ON")


def is_db_initialized() -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM tahun_ajaran").fetchone()
        return row["cnt"] > 0
