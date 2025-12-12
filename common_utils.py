# library/common_utils.py

import os
import requests
from datetime import datetime

class TrainerCentralCommon:
    """
    Shared helper for common TrainerCentral API operations.
    Provides base URL, OAuth token, and generic delete functionality.
    """
    def __init__(self):
        self.DOMAIN = os.getenv("DOMAIN")
        self.base_url = f"{self.DOMAIN}/api/v4"

    def delete_resource(self, resource: str, resource_id: str, orgId: str, access_token: str) -> dict:
        """
        Delete a generic resource.

        Args:
            resource (str): the resource path (e.g. "sessions", "courses", "course/<courseId>/sections")
            resource_id (str): the ID of the resource to delete.

        Returns:
            dict: API response JSON.
        """
        request_url = f"{self.base_url}/{orgId}/{resource}/{resource_id}.json"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.delete(request_url, headers=headers)
        return response.json()




class DateConverter:
    def convert_date_to_time(self, givenDate: str) -> str:
        """ 
        Convert a given date-time in the format DD-MM-YYYY HH:MMAM/PM to milliseconds 
        since the Unix epoch (January 1, 1970).
        
        Args:
            givenDate (str): The date-time string in DD-MM-YYYY HH:MMAM/PM format.
        
        Returns:
            str: The equivalent time in milliseconds since Unix epoch.
        
        Example:
            convert_date_to_time("29-11-2025 4:30PM") -> "1732882800000"
        """

        date_str, time_str = givenDate.split() 
        day, month, year = map(int, date_str.split('-'))
        time_obj = datetime.strptime(time_str, "%I:%M%p")  
        target_date = datetime(year, month, day, time_obj.hour, time_obj.minute)
        milliseconds = int(target_date.timestamp() * 1000)
        return str(milliseconds)
