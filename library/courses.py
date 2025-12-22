"""
TrainerCentral Course Management API Wrapper 
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)


class TrainerCentralCourses:
    """
    Provides helper functions to interact with TrainerCentral's course APIs.
    """

    def __init__(self):
        tc_api = os.getenv("TC_API_BASE_URL")
        self.base_url = f"{tc_api}/api/v4"

    def post_course(self, course_data: dict, orgId: str, access_token: str):
        """
        Create a new course in TrainerCentral.
        """
        request_url = f"{self.base_url}/{orgId}/courses.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        cleaned_data = course_data.copy()
        if "courseCategories" in cleaned_data and not cleaned_data["courseCategories"]:
            del cleaned_data["courseCategories"]
        
        data = {"course": cleaned_data}

        logger.info("=" * 80)
        logger.info("CREATING COURSE IN TRAINERCENTRAL")
        logger.info(f"URL: {request_url}")
        logger.info(f"Payload: {data}")
        logger.info("=" * 80)
        
        try:
            response = requests.post(request_url, json=data, headers=headers)
            
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
            
            # Check if request was successful
            if response.status_code >= 400:
                logger.error(f"❌ TrainerCentral API Error: {response.status_code}")
                logger.error(f"Error Response: {response.text}")
            else:
                logger.info("✅ Course created successfully")
            
            response_json = response.json()
            return response_json
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ HTTP Request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise

    def get_course(self, courseId: str, orgId: str, access_token: str):
        """
        Fetch the details of a single course.
        """
        request_url = f"{self.base_url}/{orgId}/courses/{courseId}.json"
        headers = {"Authorization": f"Bearer {access_token}"}

        logger.info(f"Getting course: {request_url}")
        response = requests.get(request_url, headers=headers)
        logger.info(f"Get course status: {response.status_code}")
        
        return response.json()

    def list_courses(self, orgId: str, access_token: str):
        """
        List all courses (or paginated subset) from TrainerCentral.
        """
        request_url = f"{self.base_url}/{orgId}/courses.json"
        headers = {"Authorization": f"Bearer {access_token}"}

        logger.info(f"Listing courses: {request_url}")
        response = requests.get(request_url, headers=headers)
        logger.info(f"List courses status: {response.status_code}")
        
        return response.json()

    def update_course(self, courseId: str, updates: dict, orgId: str, access_token: str):
        """
        Edit/update an existing TrainerCentral course.
        """
        request_url = f"{self.base_url}/{orgId}/courses/{courseId}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data = {"course": updates}

        logger.info(f"Updating course: {request_url}")
        logger.info(f"Update data: {data}")
        
        response = requests.put(request_url, json=data, headers=headers)
        logger.info(f"Update course status: {response.status_code}")
        logger.info(f"Update response: {response.text}")
        
        return response.json()

    def delete_course(self, courseId: str, orgId: str, access_token: str):
        """
        Permanently delete a TrainerCentral course.
        """
        request_url = f"{self.base_url}/{orgId}/courses/{courseId}.json"
        headers = {"Authorization": f"Bearer {access_token}"}

        logger.info(f"Deleting course: {response.status_code}")
        response = requests.delete(request_url, headers=headers)
        logger.info(f"Delete course status: {response.status_code}")
        
        return response.json()

    
    def view_course_access_requests(self, courseId: str, orgId: str, access_token: str, limit: int = 15):
        """
        Get view course requests for a TrainerCentral course.
        """
        request_url = f"{self.base_url}/{orgId}/course/{courseId}/courseMembers.json?filter=2&limit={limit}"
        headers = {"Authorization": f"Bearer {access_token}"}

        logger.info(f"Requesting course access requests from: {request_url}")
        response = requests.get(request_url, headers=headers)
        logger.info(f"Getting course access status: {response.status_code}")
        
        return response.json()

    def accept_or_reject_course_view_access_request(self, courseId: str, orgId: str, access_token: str, responseStatus: int):
        """
        Accept or Reject a user's course view access request.
        """
        request_url = f"{self.base_url}/{orgId}/updateCourseAttendee/{courseId}.json"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"courseMembers": [{"status": responseStatus}]}

        logger.info(f"Sending request to accept/reject course access to: {request_url}")
        response = requests.post(request_url, headers=headers, json=data)  # Changed to POST
        logger.info(f"Accept/Reject course access status: {response.status_code}")

        return response.json()