"""
OAuth handling for Zoho TrainerCentral API.
"""

import os
import time
import requests
import dotenv

dotenv.load_dotenv()


class ZohoOAuth:
    """
    Handles OAuth2 authentication for Zoho APIs used by TrainerCentral.

    This class manages:
    - Storing client credentials
    - Refreshing access tokens
    - Automatically reusing or refreshing tokens when required
    """

    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.access_token = None
        self.expires_at = 0

    def refresh_access_token(self):
        """
        Refresh the Zoho OAuth2 access token using the stored refresh token.

        Returns:
            str: A new access token.

        Raises:
            Exception: If the response does not contain an "access_token".
        """
        url = "https://accounts.zoho.in/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, data=data)
        result = response.json()

        if "access_token" not in result:
            raise Exception(f"Failed to refresh access token: {result}")

        self.access_token = result["access_token"]
        self.expires_at = time.time() + int(result.get("expires_in", 3600))

        return self.access_token

    def get_access_token(self):
        """
        Return a valid access token.  
        If the current token is expired or missing, it refreshes automatically.

        Returns:
            str: A valid Zoho access token.
        """
        if not self.access_token or time.time() >= self.expires_at:
            return self.refresh_access_token()
        return self.access_token
