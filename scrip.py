import requests
from datetime import datetime, timedelta, UTC
import os
import sqlite3
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("clockify-gcal")

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables"""

    # Clockify API configuration
    CLOCKIFY_API_KEY = os.getenv("CLOCKIFY_API_KEY")
    WORKSPACE_ID = os.getenv("WORKSPACE_ID")
    USER_ID = os.getenv("USER_ID")
    BASE_URL = "https://api.clockify.me/api/v1"

    # Google Calendar configuration
    SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
    CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

    @classmethod
    def validate(cls):
        """Validate that all required configuration is available"""
        required = ["CLOCKIFY_API_KEY", "WORKSPACE_ID", "USER_ID", "CALENDAR_ID"]
        missing = [var for var in required if not getattr(cls, var)]

        if missing:
            logger.error(
                f"Missing required environment variables: {', '.join(missing)}"
            )
            return False
        return True


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


class GoogleCalendar:
    """Handles Google Calendar operations"""

    @staticmethod
    def get_service():
        """Get authenticated Google Calendar service"""
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", Config.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        return build("calendar", "v3", credentials=creds)

    @classmethod
    def add_event(cls, entry):
        """Add a time entry to Google Calendar"""
        try:
            service = cls.get_service()

            start_time = datetime.strptime(
                entry["timeInterval"]["start"], "%Y-%m-%dT%H:%M:%SZ"
            )
            end_time = datetime.strptime(
                entry["timeInterval"]["end"], "%Y-%m-%dT%H:%M:%SZ"
            )

            event = {
                "summary": entry.get("description", "Time Entry"),
                "description": f"Project: {entry.get('projectId', 'No project')}",
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
                "colorId": "2",  # 2 corresponds to green in Google Calendar
            }

            service.events().insert(calendarId=Config.CALENDAR_ID, body=event).execute()
            logger.info(f"Added entry {entry['id']} to Google Calendar")
            return True

        except Exception as e:
            logger.error(f"Error adding to Google Calendar: {e}")
            return False


class ClockifyAPI:
    """Handles Clockify API operations"""

    @classmethod
    def get_time_entries(cls, hours=6):
        """Get time entries from Clockify API"""
        headers = {
            "X-Api-Key": Config.CLOCKIFY_API_KEY,
            "Content-Type": "application/json",
        }

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        url = f"{Config.BASE_URL}/workspaces/{Config.WORKSPACE_ID}/user/{Config.USER_ID}/time-entries"
        params = {
            "start": start_time_str,
            "end": end_time_str,
            "page-size": 50,
            "in-progress": "false",
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Clockify events: {e}")
            return []


class Sync:
    """Synchronizes Clockify entries to Google Calendar"""

    @classmethod
    def process_entries(cls, time_entries):
        """Process time entries and add them to Google Calendar if needed"""
        if not time_entries:
            logger.info("No time entries to process")
            return

        for entry in time_entries:
            try:
                result = Database.entry_exists(entry["id"])

                if result is None:
                    # New entry
                    added_to_calendar = 0
                    if GoogleCalendar.add_event(entry):
                        added_to_calendar = 1

                    Database.add_entry(entry, added_to_calendar)
                    logger.info(f"Added new entry {entry['id']} to database")

                elif result[1] == 0:
                    # Entry exists but not added to calendar
                    if GoogleCalendar.add_event(entry):
                        Database.mark_as_added_to_calendar(entry["id"])
                        logger.info(f"Updated entry {entry['id']} in calendar")

            except Exception as e:
                logger.error(
                    f"Error processing entry {entry.get('id', 'unknown')}: {e}"
                )
                continue


def main():
    """Main function to run the sync process"""
    # Check configuration
    if not Config.validate():
        return

    # Initialize database
    Database.init()

    # Get time entries from Clockify
    time_entries = ClockifyAPI.get_time_entries()

    # Process entries
    Sync.process_entries(time_entries)

    logger.info("Sync completed successfully")


if __name__ == "__main__":
    main()
