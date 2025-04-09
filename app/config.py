import os
import logging
from dotenv import load_dotenv

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
