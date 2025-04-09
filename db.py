import sqlite3
from config import logger


class Database:
    """Handles database operations"""

    DB_FILE = "time_entries.db"

    @classmethod
    def init(cls):
        """Initialize the database"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration TEXT,
            description TEXT,
            project_id TEXT,
            added_to_calendar INTEGER DEFAULT 0
        )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    @classmethod
    def entry_exists(cls, entry_id):
        """Check if an entry exists in the database"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, added_to_calendar FROM time_entries WHERE id = ?", (entry_id,)
        )
        result = cursor.fetchone()

        conn.close()
        return result

    @classmethod
    def add_entry(cls, entry, added_to_calendar=0):
        """Add a new time entry to the database"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO time_entries 
        (id, start_time, end_time, duration, description, project_id, added_to_calendar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                entry["id"],
                entry["timeInterval"]["start"],
                entry["timeInterval"].get("end"),
                entry["timeInterval"].get("duration"),
                entry.get("description"),
                entry.get("projectId"),
                added_to_calendar,
            ),
        )

        conn.commit()
        conn.close()

    @classmethod
    def mark_as_added_to_calendar(cls, entry_id):
        """Mark an entry as added to Google Calendar"""
        conn = sqlite3.connect(cls.DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
        UPDATE time_entries 
        SET added_to_calendar = 1 
        WHERE id = ?
        """,
            (entry_id,),
        )

        conn.commit()
        conn.close()
