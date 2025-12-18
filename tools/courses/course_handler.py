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
# def tc_get_course(courseId: str, orgId: str, access_token: str) -> dict:
#     """
#     Retrieve a course by its ID.

#     Syntax:
#         tc_get_course("3000094000002000004")

#     Note: Provide orgId and access token of the user, after OAuth, as parameters.  

#     This will call the TrainerCentral Get Course API:
#         GET /api/v4/{orgId}/courses/{courseId}.json

#     Required OAuth scope:
#         TrainerCentral.courseapi.READ

#     Returns:
#         dict containing:
#             - courseId
#             - courseName
#             - description
#             - subTitle
#             - links to sessions, tickets, etc.
#     """
#     return tc.get_course(courseId, orgId, access_token)

def tc_get_course(courseId: str, orgId: str, access_token: str) -> dict:
    """
    Retrieve a course by its ID, returning a UI-widget enabled response.

    The MCP response includes:
      - structuredContent: concise summary for the model
      - content: optional text for the model
      - _meta: full course details for the widget

    Args:
        courseId (str): ID of the course to retrieve.
        orgId (str): Organization ID (from tc_get_org_id)
        access_token (str): OAuth access token

    Returns:
        dict: MCP response with course info for both model and widget.
    """

    # Fetch the course details from the underlying library
    try:
        result = tc.get_course(courseId, orgId, access_token)
    except Exception as e:
        # In case of errors, return a structured error
        error_msg = f"Failed to retrieve course {courseId}: {str(e)}"
        return {
            "structuredContent": {"summary": error_msg},
            "content": [
                {"type": "text", "text": error_msg}
            ],
            "isError": True
        }

    # Result from tc.get_course should be a dict with course details
    course_obj = result if isinstance(result, dict) else {}

    # Build a summary string for the model
    course_name = course_obj.get("courseName") or course_obj.get("name") or courseId
    summary_text = f"Details for course {course_name} (ID: {courseId})."

    # Return MCP widget-ready format
    return {
        # Model sees this
        "structuredContent": {
            "summary": summary_text,
            # Optionally include core fields if you want the model to reason about them
            "course": {
                "id": course_obj.get("courseId") or course_obj.get("id") or courseId,
                "name": course_obj.get("courseName") or course_obj.get("name") or "",
                "description": course_obj.get("description") or "",
                "subTitle": course_obj.get("subTitle") or "",
                "status": course_obj.get("publishStatus") or "",
                "enrolled": course_obj.get("enrolledCount", 0),
            },
        },

        # Optional narrative for model
        "content": [
            {
                "type": "text",
                "text": summary_text
            }
        ],

        # Widget sees full course details here
        "_meta": {
            "course": course_obj
        }
    }



# #@mcp.tool()
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


def tc_list_courses_with_widget(orgId: str, access_token: str, limit: int = None, si: int = None) -> dict:
    """
    List courses WITH interactive ChatGPT widget UI.
    
    Returns data in the official MCP widget format:
    - structuredContent: Concise summary the MODEL reads
    - content: Optional narration for the model
    - _meta: Rich data ONLY for widget (never sent to model)
    """
    
    # Fetch courses from TrainerCentral API
    courses_response = tc.list_courses(orgId, access_token)
    
    courses = courses_response.get("courses", [])
    categories = courses_response.get("courseCategories", [])
    meta = courses_response.get("meta", {})
    total = meta.get("totalCourseCount", len(courses))
    
    # Count by status
    draft_count = sum(1 for c in courses if c.get("publishStatus") in ["DRAFT", "NONE"])
    published_count = sum(1 for c in courses if c.get("publishStatus") == "PUBLISHED")
    
    return {
        # STRUCTURED CONTENT: Concise data the MODEL reads
        "structuredContent": {
            "summary": f"Found {total} courses ({published_count} published, {draft_count} draft)",
            "courses": [
                {
                    "id": c.get("courseId"),
                    "name": c.get("courseName"),
                    "status": c.get("publishStatus"),
                    "enrolled": c.get("enrolledCount", 0)
                }
                for c in courses[:]  # Only show first 5 to model
            ]
        },
        
        # CONTENT: Natural language narration for model
        "content": [
            {
                "type": "text",
                "text": f"You have {total} courses. Use the interactive widget below to browse, filter by status, sort, and manage your courses."
            }
        ],
        
        # META: Full data ONLY for widget (model never sees this!)
        "_meta": {
            # Point to the widget template URI
            "openai/outputTemplate": "ui://widget/courses.html",
            
            # Full courses data for the widget
            "courses": courses,
            "courseCategories": categories,
            "totalCourseCount": total,
            "stats": {
                "total": total,
                "published": published_count,
                "draft": draft_count
            }
        }
    }


# # Plain version without widget
# def tc_list_courses(orgId: str, access_token: str, limit: int = None, si: int = None) -> dict:
#     """List courses without widget UI (plain data only)."""
#     return tc.list_courses(orgId, access_token)


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
