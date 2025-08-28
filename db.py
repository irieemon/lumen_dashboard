import sqlite3
import pandas as pd
import os

DB_PATH = os.getenv("LUMEN_DB", "lumen_dashboard.db")


def init_db():
    """Initialize database tables and seed data from CSV if empty."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS initiatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            details TEXT,
            color TEXT,
            category TEXT,
            x REAL,
            y REAL,
            value TEXT,
            effort TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            is_deleted BOOLEAN DEFAULT 0
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            initiative_id INTEGER,
            initiative_title TEXT,
            user TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()

    c.execute("SELECT COUNT(*) FROM initiatives")
    if c.fetchone()[0] == 0:
        csv_path = os.path.join(os.path.dirname(__file__), "lumen_initiatives.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df["is_deleted"] = 0
            df.to_sql("initiatives", conn, if_exists="append", index=False)
            conn.commit()
    conn.close()


def get_initiatives():
    conn = sqlite3.connect(DB_PATH)
    query = (
        "SELECT id, title, details, color, category, x, y, value, effort, created_at, updated_at, created_by, updated_by "
        "FROM initiatives WHERE is_deleted = 0 ORDER BY id"
    )
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def update_position(initiative_id: int, x: float, y: float, user: str = "user") -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    value = "High" if y > 66 else "Medium" if y > 33 else "Low"
    effort = "High" if x > 66 else "Medium" if x > 33 else "Low"
    c.execute(
        """
        UPDATE initiatives SET x=?, y=?, value=?, effort=?,
               updated_at=CURRENT_TIMESTAMP, updated_by=? WHERE id=?
        """,
        (x, y, value, effort, user, initiative_id),
    )
    conn.commit()
    conn.close()


def add_initiative(title: str, details: str, color: str, category: str, x: float, y: float, user: str = "user") -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    value = "High" if y > 66 else "Medium" if y > 33 else "Low"
    effort = "High" if x > 66 else "Medium" if x > 33 else "Low"
    c.execute(
        """
        INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, details, color, category, x, y, value, effort, user, user),
    )
    conn.commit()
    conn.close()


def upsert_initiative(
    initiative_id: int | None,
    title: str,
    details: str,
    color: str,
    category: str,
    x: float,
    y: float,
    user: str = "user",
) -> int:
    """Add a new initiative or update an existing one and return its id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    value = "High" if y > 66 else "Medium" if y > 33 else "Low"
    effort = "High" if x > 66 else "Medium" if x > 33 else "Low"
    if initiative_id:
        c.execute(
            """
            UPDATE initiatives
            SET title=?, details=?, color=?, category=?, x=?, y=?,
                value=?, effort=?, updated_at=CURRENT_TIMESTAMP, updated_by=?
            WHERE id=?
            """,
            (title, details, color, category, x, y, value, effort, user, initiative_id),
        )
        new_id = initiative_id
    else:
        c.execute(
            """
            INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, details, color, category, x, y, value, effort, user, user),
        )
        new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def delete_initiative(initiative_id: int, user: str = "user") -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE initiatives SET is_deleted=1, updated_at=CURRENT_TIMESTAMP, updated_by=? WHERE id=?",
        (user, initiative_id),
    )
    conn.commit()
    conn.close()


def get_last_updated() -> str | None:
    """Return the most recent updated_at timestamp from initiatives."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(updated_at) FROM initiatives")
    result = c.fetchone()[0]
    conn.close()
    return result
