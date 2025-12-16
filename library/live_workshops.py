import os
import requests
from library.common_utils import DateConverter


class TrainerCentralLiveWorkshops:
    """
    Handles GLOBAL Live Workshops (deliveryMode = 3).
    These are NOT associated with any course.

    API References:
      Create Workshop:
        POST /api/v4/<orgId>/sessions.json

      Edit Workshop:
        PUT /api/v4/<orgId>/sessions/<sessionId>.json

      Create Occurrence (Talk):
        POST /api/v4/<orgId>/talks.json

      Edit Occurrence:
        PUT /api/v4/<orgId>/talks/<talkId>.json

      Cancel Workshop or Occurrence:
        PUT with { "isCancelled": true }
    """

    def __init__(self):
        tc_api = os.getenv("TC_API_BASE_URL")
        self.base_url = f"{tc_api}/api/v4"
        self.date_converter = DateConverter()  


    def create_global_workshop(
        self,
        name: str,
        description_html: str,
        start_time_str: str,
        end_time_str: str,
        orgId: str,
        access_token: str
    ) -> dict:
        """
        Create a GLOBAL live workshop.

        API:
            POST /api/v4/<orgId>/sessions.json

        deliveryMode = 3 → live workshop (global)

        Args (LLM REQUIRED FORMAT):
            start_time_str: "DD-MM-YYYY HH:MMAM/PM"
            end_time_str:   "DD-MM-YYYY HH:MMAM/PM"

        Returns:
            dict: API response
        """

        start_ms = int(self.date_converter.convert_date_to_time(start_time_str))
        end_ms = int(self.date_converter.convert_date_to_time(end_time_str))

        url = f"{self.base_url}/{orgId}/sessions.json"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        body = {
            "session": {
                "name": name,
                "description": description_html,
                "deliveryMode": 3,
                "scheduledTime": start_ms,
                "scheduledEndTime": end_ms,
                "durationTime": end_ms - start_ms
            }
        }

        return requests.post(url, json=body, headers=headers).json()


    def update_workshop(self, session_id: str, updates: dict, orgId: str, access_token: str) -> dict:
        """
        Update an existing global live workshop.

        Args:
            session_id (str): workshop sessionId
            updates (dict): fields to update
                {
                   "name": "...",
                   "scheduledTime": <ms>,
                   "scheduledEndTime": <ms>,
                   "description": "<html>",
                   "isCancelled": true     # for cancellation
                }

        Returns:
            dict: API response
        """

        url = f"{self.base_url}/{orgId}/sessions/{session_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        payload = {"session": updates}
        return requests.put(url, json=payload, headers=headers).json()


    def create_occurrence(self, talk_data: dict, orgId: str, access_token: str) -> dict:
        """
        Create an occurrence (talk) for a workshop.

        Args:
            talk_data (dict):
                {
                    "scheduledTime": <ms>,
                    "scheduledEndTime": <ms>,
                    "sessionId": "<parentSessionId>",
                    "durationTime": <ms>,
                    "recurrence": { ... } # optional
                }

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/{orgId}/talks.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        payload = {"talk": talk_data}
        return requests.post(url, json=payload, headers=headers).json()


    def update_occurrence(self, talk_id: str, updates: dict, orgId: str, access_token: str) -> dict:
        """
        Update or cancel a workshop occurrence.

        Args:
            talk_id (str): talkId
            updates (dict):
                {
                    "scheduledTime": <ms>,
                    "scheduledEndTime": <ms>,
                    "informRegistrants": true/false,
                    "isCancelled": true         # for cancellation
                }

        Returns:
            dict
        """

        url = f"{self.base_url}/{orgId}/talks/{talk_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        payload = {"talk": updates}
        return requests.put(url, json=payload, headers=headers).json()

    def list_all_upcoming_workshops(self, orgId: str, access_token: str, filter_type: int = 5, limit: int = 50, si: int = 0) -> dict:
        """
        Fetch all upcoming global live workshops.
        Uses: GET /talks.json?filter=&limit=&si=

        Args:
            filter_type (int): 1 = your upcoming; 5 = all upcoming (admin).
            limit (int): number of items.
            si (int): start index.

        Returns:
            dict: API response with sessions list.
        """
        url = f"{self.base_url}/{orgId}/talks.json?filter={filter_type}&limit={limit}&si={si}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return requests.get(url, headers=headers).json()

    def invite_user_to_workshop(self, session_id: str, email: str, orgId: str, access_token: str, role: int = 3, source: int = 1) -> dict:
        """
        Invite / add a member (by email) to a course-linked live workshop / session.

        Args:
            session_id (str): ID of the existing session / live workshop.
            email (str): Email address of the user to invite.
            role (int): Role code in session (e.g. 3 = attendee – adjust as per your setup).
            source (int): Source indicator (per TrainerCentral API).

        Returns:
            dict: API response JSON.
        """
        url = f"{self.base_url}/{orgId}/sessionMembers.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "sessionMembers": [
                {
                    "emailId": email,
                    "sessionId": session_id,
                    "role": role,
                    "source": source
                }
            ]
        }
        resp = requests.post(url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()