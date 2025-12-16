"""
FastMCP tools that expose TrainerCentral course APIs.
"""

from library.courses import TrainerCentralCourses
from tools.mcp_registry import mcp 

tc = TrainerCentralCourses()


#@mcp.tool()
def tc_create_course(course_data: dict, orgId: str, access_token: str) -> dict:
    """
    Create a new course in TrainerCentral.

    Syntax:
        tc_create_course({
            "courseName": "My Course",
            "subTitle": "Catchy Subtitle",
            "description": "Detailed description",
            "courseCategories": [
                {"categoryName": "Business"},
                {"categoryName": "Software"}
            ]
        })

    This will call the TrainerCentral Create Course API with a body like:
        {
            "course": {
                "courseName": "My Course",
                "subTitle": "Catchy Subtitle",
                "description": "Detailed description",
                "courseCategories": [
                    {"categoryName": "Business"},
                    {"categoryName": "Software"}
                ]
            }
        }

    Course Category: 
    Default Category List

    {name: "Art & Photos"},
    {name: "Automotive"},
    {name: "Business"},
    {name: "Career"},
    {name: "Data & Analytics"},
    {name: "Design"},
    {name: "Devices & Hardware"},
    {name: "Economy & Finance"},
    {name: "Education"},
    {name: "Engineering"},
    {name: "Entertainment & Humor"},
    {name: "Environment"},
    {name: "Food"},
    {name: "Government & Nonprofit"},
    {name: "Health & Medicine"},
    {name: "Healthcare"},
    {name: "Internet"},
    {name: "Investor Relations"}
    {name: "Law"}
    {name: "Leadership & Management"}
    {name: "Lifestyle"}
    {name: "Marketing"}
    {name: "Mobile"}
    {name: "News & Politics"}
    {name: "Presentations & Public Speaking"}
    {name: "Real Estate"}
    {name: "Recruiting & HR"}
    {name: "Sales"}
    {name: "Science"}
    {name: "Self Improvement"}
    {name: "Services"}
    {name: "Small Business & Entrepreneurship"}
    {name: "Social Media"}
    {name: "Software"}
    {name: "Spiritual"}
    {name: "Sports"}
    {name: "Technology"}
    {name: "Travel"} 


    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Required OAuth scope:
        TrainerCentral.courseapi.CREATE

    Returns:
        dict: API response, including:
            - ticket
            - course
    """
    return tc.post_course(course_data, orgId, access_token)


#@mcp.tool()
def tc_get_course(courseId: str, orgId: str, access_token: str) -> dict:
    """
    Retrieve a course by its ID.

    Syntax:
        tc_get_course("3000094000002000004")

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    This will call the TrainerCentral Get Course API:
        GET /api/v4/{orgId}/courses/{courseId}.json

    Required OAuth scope:
        TrainerCentral.courseapi.READ

    Returns:
        dict containing:
            - courseId
            - courseName
            - description
            - subTitle
            - links to sessions, tickets, etc.
    """
    return tc.get_course(courseId, orgId, access_token)


#@mcp.tool()
def tc_list_courses(orgId: str, access_token: str, limit: int = None, si: int = None) -> dict:
    """
    List all courses (or a paginated subset).

    Syntax:
        tc_list_courses(orgId, access_token)
        tc_list_courses(orgId, access_token, limit=30)
        tc_list_courses(orgId, access_token, limit=20, si=10)
        

    Note:
        Note: Provide orgId and access token of the user, after OAuth, as parameters.  
        TrainerCentral uses `limit` and `si` as query parameters.
        Current implementation returns all courses — pagination support
        can be added later.

    Required OAuth scope:
        TrainerCentral.courseapi.READ

    Returns:
        dict with:
            - courses []
            - courseCategories []
            - meta { totalCourseCount }
    """
    return tc.list_courses(orgId, access_token)


#@mcp.tool()
def tc_update_course(courseId: str, updates: dict, orgId: str, access_token: str) -> dict:
    """
    Update an existing course.

    Syntax:
        tc_update_course(
            "3000094000002000004",
            {
                "courseName": "New Name",
                "subTitle": "New Subtitle",
                "description": "Updated detail",
                "courseCategories": [
                    {"categoryName": "Business"},
                    {"categoryName": "Leadership"}
                ]
            }
        )

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
        
    This will call the TrainerCentral Update Course API with:
        {
            "course": {
                "courseName": "New Name",
                "subTitle": "New Subtitle",
                "description": "Updated detail",
                "courseCategories": [...]
            }
        }

    Required OAuth scope:
        TrainerCentral.courseapi.UPDATE

    Returns:
        dict: Updated course object.
    """
    return tc.update_course(courseId, updates, orgId, access_token)


#@mcp.tool()
def tc_delete_course(courseId: str, orgId: str, access_token: str) -> dict:
    """
    Delete a course permanently.

    Syntax:
        tc_delete_course("3000094000002000004")

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    This will call the TrainerCentral Delete Course API:
        DELETE /api/v4/{orgId}/courses/{courseId}.json

    Required OAuth scope:
        TrainerCentral.courseapi.DELETE

    Returns:
        dict: API delete response.
    """
    return tc.delete_course(courseId, orgId, access_token)
