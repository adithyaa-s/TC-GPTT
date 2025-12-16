"""
FastMCP tools that expose TrainerCentral lesson (session) APIs.
"""

from tools.mcp_registry import mcp
from library.lessons import TrainerCentralLessons

tc_lessons = TrainerCentralLessons()


# #@mcp.tool()
# def tc_create_lesson(session_data: dict) -> dict:
#     """
#     Create a new lesson under a course/chapter.

#     Syntax:
#         tc_create_lesson({
#             "name": "Lesson Title",
#             "courseId": "3000094000002000004",
#             "sectionId": "3200000000002000012",
#             "deliveryMode": 4  # 4 = on-demand, 3 = live
#         })

#     Required OAuth scope:
#         TrainerCentral.sessionapi.CREATE

#     Args:
#         session_data (dict): Fields required for the lesson.

#     Returns:
#         dict: API response for the created session.
#     """
#     return tc_lessons.create_lesson(session_data)

#@mcp.tool()
def tc_create_lesson(
    session_data: dict,
    content_html: str,
    orgId: str,
    access_token: str,
    content_filename: str = "Content"
) -> dict:
    """
    Create a lesson under a course/chapter, with full rich-text content.

    Args:
        session_data (dict): metadata for lesson (name, courseId, sectionId, deliveryMode, etc.)
        content_html (str): full HTML/text body of lesson
        content_filename (str, optional): title/filename for upload (default: "Content")

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
        dict: { "lesson": ..., "content": ... }
    """
    return tc_lessons.create_lesson_with_content(session_data, content_html, orgId, access_token, content_filename)

def tc_get_course_lessons(courseId: str, orgId: str, access_token: str) -> dict:
    """
    Get all lessons (sessions) for a specific course.
    
    This is useful for:
    - Listing all lessons in a course before creating tests
    - Understanding course structure
    - Getting lesson IDs for update/delete operations
    
    TrainerCentral API Flow:
    1. GET /api/v4/{orgId}/courses/{courseId}.json
       → Extract sessions link
    2. GET the sessions URL
       → Returns list of all lessons
    
    Usage Example:
        # First get the course lessons
        lessons = tc_get_course_lessons(
            courseId="19208000000009003",
            orgId="60058756004",
            access_token="..."
        )
        
        # Then you can:
        # - Create tests for specific lessons
        # - Update lesson content
        # - Delete lessons
        # - Get lesson details
    
    Args:
        courseId (str): Course ID to get lessons from
        orgId (str): Organization ID (from tc_get_org_id)
        access_token (str): OAuth access token
    
    Returns:
        dict: {
            "course": {
                "courseId": "19208000000009003",
                "courseName": "Python Mastery"
            },
            "lessons": [
                {
                    "sessionId": "19208000000017003",
                    "name": "Error Handling Basics",
                    "description": "Learn error handling...",
                    "deliveryMode": 4,
                    "sectionId": "19208000000015001",
                    "links": {
                        "tests": "/api/v4/.../tests.json",
                        ...
                    }
                },
                ...
            ],
            "total_lessons": 5
        }
    
    Note: 
        - Provide orgId from tc_get_org_id() tool
        - OAuth scope required: TrainerCentral.sessionapi.READ
    """
    return lessons.get_course_lessons(courseId, orgId, access_token)


#@mcp.tool()
def tc_update_lesson(session_id: str, updates: dict, orgId: str, access_token: str) -> dict:
    """
    Update an existing lesson in TrainerCentral.

    Syntax:
        tc_update_lesson(
            "3300000000002000020",  # sessionId
            {
                "name": "New Lesson Title",
                "description": "Updated description",
                "sectionId": "3200000000002000012",
                "sessionIndex": 1
            }
        )

    Required OAuth scope:
        TrainerCentral.sessionapi.UPDATE

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Args:
        session_id (str): ID of the session (lesson) to update.
        updates (dict): Fields to update.

    Returns:
        dict: API response containing the updated session.
    """
    return tc_lessons.update_lesson(session_id, updates, orgId, access_token)


#@mcp.tool()
def tc_delete_lesson(session_id: str, orgId: str, access_token: str) -> dict:
    """
    Delete a lesson (or live session) by session ID.

    Syntax:
        tc_delete_lesson("3300000000002000020")

    Required OAuth scope:
        TrainerCentral.sessionapi.DELETE

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Args:
        session_id (str): ID of the session to delete.

    Returns:
        dict: API response for the delete operation.
    """
    return tc_lessons.delete_lesson(session_id, orgId, access_token)
