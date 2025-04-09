from config import Config, logger
from db import Database
from clockify import ClockifyAPI
from sync import Sync


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
