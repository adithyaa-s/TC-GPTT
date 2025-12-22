import os
import requests
from .common_utils import TrainerCentralCommon
import logging

logger = logging.getLogger(__name__)

class TrainerCentralLessons:
    def __init__(self):
        tc_api = os.getenv("TC_API_BASE_URL")
        self.base_url = f"{tc_api}/api/v4"
        self.common = TrainerCentralCommon()

    def create_lesson_with_content(
        self,
        lesson_data: dict,
        content_html: str,
        orgId: str, 
        access_token: str,
        content_filename: str = "Content",
    ) -> dict:
        """
        Create a lesson (session) with full rich-text content.

        Args:
            lesson_data (dict): session metadata, e.g.
                {
                   "name": "Lesson Title",
                   "courseId": "...",
                   "sectionId": "...",
                   "deliveryMode": 4,
                   # optionally: description (short summary/blurb)
                }
            content_html (str): full lesson body (HTML text)
            content_filename (str, optional): filename/title used for content upload

        Returns:
            dict: {
              "lesson": {... response from session creation ...},
              "content": {... response from content upload ...}
            }
        """
        # Step 1: create session
        url = f"{self.base_url}/{orgId}/sessions.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {"session": lesson_data}
        create_resp = requests.post(url, json=payload, headers=headers).json()

        # Step 2: upload content
        session_obj = create_resp.get("session")
        session_id = None
        if isinstance(session_obj, dict):
            session_id = session_obj.get("id") or session_obj.get("sessionId")
        if not session_id:
            raise RuntimeError(f"Failed to find sessionId in response: {create_resp}")

        content_url = f"{self.base_url}/{orgId}/session/{session_id}/createTextFile.json"
        content_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        content_body = {
            "richTextContent": content_html,
            "filename": content_filename
        }
        content_resp = requests.post(content_url, json=content_body, headers=content_headers).json()

        return {
            "lesson": create_resp,
            "content": content_resp
        }

    def get_course_lessons(self, courseId: str, orgId: str, access_token: str) -> dict:
        """
        Fetch all lessons (sessions) under a course.
        
        This is useful for:
        - Listing all lessons in a course
        - Getting lesson IDs before creating tests or other operations
        - Understanding course structure
        
        Steps:
        1. GET /api/v4/{orgId}/courses/{courseId}.json
        → Extract links.sessions
        2. GET the sessions URL
        → Return array of lessons with LLM-friendly fields
        
        Args:
            courseId (str): Course ID
            orgId (str): Organization ID
            access_token (str): OAuth access token
        
        Returns:
            dict: {
                "course": {
                    "courseId": "...",
                    "courseName": "..."
                },
                "lessons": [
                    {
                        "sessionId": "...",
                        "name": "...",
                        "description": "...",
                        "deliveryMode": 4,
                        "links": {...}
                    }
                ],
                "total_lessons": 5
            }
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Get course details to find sessions link
        course_url = f"{self.base_url}/{orgId}/courses/{courseId}.json"
        
        try:
            logger.info(f"Fetching course details: {course_url}")
            course_res = requests.get(course_url, headers=headers)
            course_res.raise_for_status()
            course_data = course_res.json()
            
            # Validate structure
            if "course" not in course_data:
                logger.error("'course' key missing in response")
                return {
                    "error": "'course' key missing in response",
                    "raw": course_data
                }
            
            course_obj = course_data["course"]
            
            # Extract sessions link
            sessions_link = course_obj.get("links", {}).get("sessions")
            if not sessions_link:
                logger.warning("No sessions link found - course may have no lessons")
                return {
                    "course": {
                        "courseId": course_obj.get("courseId"),
                        "courseName": course_obj.get("courseName")
                    },
                    "lessons": [],
                    "total_lessons": 0
                }
            
            # Step 2: Get lessons from sessions endpoint
            # sessions_link is relative, e.g., "/api/v4/{orgId}/course/{courseId}/sessions.json"
            sessions_url = f"{self.base_url.split('/api/v4')[0]}{sessions_link}"
            
            logger.info(f"Fetching lessons: {sessions_url}")
            sessions_res = requests.get(sessions_url, headers=headers)
            sessions_res.raise_for_status()
            sessions_data = sessions_res.json()
            
            # Parse lessons
            lessons_list = []
            for session in sessions_data.get("sessions", []):
                lessons_list.append({
                    "sessionId": session.get("sessionId"),
                    "name": session.get("name"),
                    "description": session.get("description", ""),
                    "deliveryMode": session.get("deliveryMode"),
                    "sectionId": session.get("sectionId"),
                    "links": session.get("links", {})
                })
            
            logger.info(f"Found {len(lessons_list)} lessons")
            
            return {
                "course": {
                    "courseId": course_obj.get("courseId"),
                    "courseName": course_obj.get("courseName")
                },
                "lessons": lessons_list,
                "total_lessons": len(lessons_list)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get course lessons: {e}")
            return {
                "error": f"Failed to retrieve lessons: {str(e)}",
                "courseId": courseId
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "error": f"Unexpected error: {str(e)}",
                "courseId": courseId
            }

    def update_lesson(self, session_id: str, updates: dict, orgId: str, access_token: str) -> dict:
        url = f"{self.base_url}/{orgId}/sessions/{session_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {"session": updates}
        return requests.put(url, json=payload, headers=headers).json()

    def delete_lesson(self, session_id: str, orgId: str, access_token: str) -> dict:
        return self.common.delete_resource("sessions", session_id, orgId, access_token)
