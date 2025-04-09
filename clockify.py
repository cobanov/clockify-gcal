import requests
from datetime import datetime, timedelta
from config import Config, logger


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
