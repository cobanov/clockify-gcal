from db import Database
from gcal import GoogleCalendar
from config import logger


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
