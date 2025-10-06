import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']

class AuthService:
    def get_google_auth_flow(self):
        """
        Initializes and returns the Google OAuth 2.0 Flow object.
        """
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.google.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [os.getenv("REDIRECT_URI")],
            }
        }
        return Flow.from_client_config(
            client_config=client_config,
            scopes=SCOPES,
            redirect_uri=os.getenv("REDIRECT_URI")
        )

    def get_authorization_url(self):
        """
        Generates the URL to which the user should be redirected to authorize the application.
        """
        flow = self.get_google_auth_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return authorization_url, state

    def fetch_token(self, authorization_response: str):
        """
        Fetches the OAuth 2.0 token from Google using the authorization response.
        """
        flow = self.get_google_auth_flow()
        flow.fetch_token(authorization_response=authorization_response)
        return flow.credentials.to_json()

    def get_user_info(self, credentials_json: str):
        """
        Uses the credentials to get the user's basic profile information (email, id).
        """
        credentials = Credentials.from_authorized_user_info(
            info=json.loads(credentials_json),
            scopes=SCOPES
        )
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info

auth_service = AuthService()