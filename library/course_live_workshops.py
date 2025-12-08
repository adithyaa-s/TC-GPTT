import os
import requests
from .oauth import ZohoOAuth
from .common_utils import DateConverter


class TrainerCentralLiveWorkshops:
    """
    TrainerCentral LIVE WORKSHOPS inside a course.

    IMPORTANT FOR MCP / AI MODELS:
    ----------------------------------------------------------
    ALL date and time inputs MUST be given in this format:

        "DD-MM-YYYY HH:MMAM/PM"
        Examples:
            "05-12-2025 3:00PM"
            "01-01-2026 9:15AM"

    The MCP MUST NOT compute Unix timestamps.
    The library automatically converts this string format into
    milliseconds using DateConverter.convert_date_to_time().
    ----------------------------------------------------------
    """

    def __init__(self):
        self.ORG_ID = os.getenv("ORG_ID")
        self.DOMAIN = os.getenv("DOMAIN")
        self.base_url = f"{self.DOMAIN}/api/v4/{self.ORG_ID}"
        self.oauth = ZohoOAuth()
        self.date_converter = DateConverter()



    def create_course_live_workshop(
        self,
        course_id: str,
        name: str,
        description_html: str,
        start_time_str: str,
        end_time_str: str,
        timezone: str,
        max_attendees: int = 0
    ):
        """
        Create a LIVE WORKSHOP inside a course.

        API:
            POST /api/v4/<orgId>/sessions.json

        REQUIRED DATE FORMAT FOR MCP/LLM:
            start_time_str and end_time_str MUST be:
                "DD-MM-YYYY HH:MMAM/PM"

        This function converts them into milliseconds automatically.

        Args:
            course_id (str)
            name (str)
            description_html (str)
            start_time_str (str): "DD-MM-YYYY HH:MMAM/PM"
            end_time_str   (str): "DD-MM-YYYY HH:MMAM/PM"
            timezone (str): Example: "Asia/Kolkata"
            max_attendees (int)

        Returns:
            dict: API response containing the newly created workshop.
        """


        start_ms = int(self.date_converter.convert_date_to_time(start_time_str))
        end_ms = int(self.date_converter.convert_date_to_time(end_time_str))

        url = f"{self.base_url}/sessions.json"
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
            "Content-Type": "application/json",
        }

        body = {
            "session": {
                "name": name,
                "description": description_html,
                "courseId": course_id,
                "deliveryMode": 3,                
                "maxParticipants": max_attendees,
                "schedule": {
                    "startTime": start_ms,
                    "endTime": end_ms,
                    "timeZone": timezone
                }
            }
        }

        return requests.post(url, json=body, headers=headers).json()


    def list_upcoming_live_sessions(self, filter_type=5, limit=50, si=0):
        url = f"{self.base_url}/upcomingSessions.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}
        params = {"filterType": filter_type, "limit": limit, "si": si}

        return requests.get(url, params=params, headers=headers).json()


    def delete_live_session(self, session_id: str):
        url = f"{self.base_url}/sessions/{session_id}.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.delete(url, headers=headers).json()


    def invite_learner_to_course_or_course_live_session(
    self,
    email: str,
    first_name: str,
    last_name: str,
    course_id: str = None,
    session_id: str = None,
    is_access_granted: bool = True,
    expiry_time: int = None,
    expiry_duration: str = None
) -> dict:
        """
        Invite a learner to a COURSE or COURSE LIVE WORKSHOP.

        REQUIRED FORMAT (Actual Working Format):
        {
            "courseAttendee": {
                "email": "...",
                "courseId": "...", OR "sessionId": "...",
                "firstName": "...",
                "lastName": "...",
                "isAccessGranted": true
            }
        }
        """

        if not course_id and not session_id:
            raise ValueError("You must provide either course_id or session_id.")

        url = f"{self.base_url}/addCourseAttendee.json"

        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
            "Content-Type": "application/json"
        }

        attendee = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "isAccessGranted": is_access_granted
        }

        if course_id:
            attendee["courseId"] = course_id
        if session_id:
            attendee["sessionId"] = session_id
        if expiry_time:
            attendee["expiryTime"] = expiry_time
        if expiry_duration:
            attendee["expiryDuration"] = expiry_duration

        body = { "courseAttendee": attendee }

        return requests.post(url, json=body, headers=headers).json()
