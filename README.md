# Clockify to Google Calendar Sync

A Python application that syncs your Clockify time entries to Google Calendar.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with the following variables:
   ```
   CLOCKIFY_API_KEY=your_clockify_api_key
   WORKSPACE_ID=your_clockify_workspace_id
   USER_ID=your_clockify_user_id
   GOOGLE_CALENDAR_ID=your_google_calendar_id
   ```
4. Download `credentials.json` from the Google Cloud Console:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download as `credentials.json` and place in the project root

## Usage

Run the main script to sync Clockify entries to Google Calendar:

```
python main.py
```

On first run, a browser window will open to authenticate with Google. This will create a `token.pickle` file that stores your authentication credentials for future use.

## Modules

- `config.py`: Application configuration
- `db.py`: Database operations for tracking synced entries
- `gcal.py`: Google Calendar integration
- `clockify.py`: Clockify API integration
- `sync.py`: Synchronization logic
- `main.py`: Main application entry point
