import os
import pickle
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import Config, logger


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
