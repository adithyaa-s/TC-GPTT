import os
import requests
from library.common_utils import DateConverter


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
        self.DOMAIN = os.getenv("DOMAIN")
        self.base_url = f"{self.DOMAIN}/api/v4"
        self.date_converter = DateConverter()


    def create_course_live_workshop(
        self,
        orgId: str,
        access_token: str,
        courseId: str,
        name: str,
        description_html: str,
        start_time_str: str,
        end_time_str: str,
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
            orgId (str): Organization ID
            access_token (str): OAuth access token
            courseId (str): Parent course ID
            name (str): Workshop title
            description_html (str): Workshop description
            start_time_str (str): "DD-MM-YYYY HH:MMAM/PM"
            end_time_str (str): "DD-MM-YYYY HH:MMAM/PM"

        Returns:
            dict: API response containing the newly created workshop.
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
                "courseId": courseId,
                "deliveryMode": 3,                
                "scheduledTime": start_ms,
                "scheduledEndTime": end_ms,
                "durationTime": end_ms - start_ms,
            }
        }

        return requests.post(url, json=body, headers=headers).json()


    def list_upcoming_live_sessions(self, orgId: str, access_token: str, filter_type=5, limit=50, si=0):
        """List upcoming live sessions"""
        url = f"{self.base_url}/{orgId}/upcomingSessions.json"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"filterType": filter_type, "limit": limit, "si": si}

        return requests.get(url, params=params, headers=headers).json()


    def delete_live_session(self, session_id: str, orgId: str, access_token: str):
        """Delete a live session"""
        url = f"{self.base_url}/{orgId}/sessions/{session_id}.json"
        headers = {"Authorization": f"Bearer {access_token}"}

        return requests.delete(url, headers=headers).json()


    def invite_learner_to_course_or_course_live_session(
        self,
        email: str,
        orgId: str,
        access_token: str,
        first_name: str,
        last_name: str,
        courseId: str = None,
        session_id: str = None,
        is_access_granted: bool = True,
        expiry_time: int = None,
        expiry_duration: str = None
    ) -> dict:
        """
        Invite a learner to a COURSE or COURSE LIVE WORKSHOP.

        REQUIRED FORMAT:
        {
            "courseAttendee": {
                "email": "...",
                "courseId" OR "sessionId": "...",
                "firstName": "...",
                "lastName": "...",
                "isAccessGranted": true
            }
        }
        """

        if not courseId and not session_id:
            raise ValueError("You must provide either courseId or session_id.")

        url = f"{self.base_url}/{orgId}/addCourseAttendee.json"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        attendee = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "isAccessGranted": is_access_granted
        }

        if courseId:
            attendee["courseId"] = courseId
        if session_id:
            attendee["sessionId"] = session_id
        if expiry_time:
            attendee["expiryTime"] = expiry_time
        if expiry_duration:
            attendee["expiryDuration"] = expiry_duration

        body = {"courseAttendee": attendee}

        return requests.post(url, json=body, headers=headers).json()