import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# This is the scope we requested during the OAuth flow.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def get_calendar_service(self, credentials_json: str):
        """
        Creates and returns a Google Calendar API service client.

        Args:
            credentials_json: The user's stored OAuth 2.0 credentials as a JSON string.

        Returns:
            A Google API client service object, ready to make requests.
        """
        try:
            # Load the credentials from the JSON string.
            credentials = Credentials.from_authorized_user_info(
                info=json.loads(credentials_json),
                scopes=SCOPES
            )

            # Build the service object.
            # The version 'v3' is the current stable version of the Calendar API.
            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            print(f"Error building calendar service: {e}")
            return None

# Create a singleton instance to be used by the application
calendar_service = CalendarService()