from tools.mcp_registry import mcp
from library.live_workshops import TrainerCentralLiveWorkshops

workshops = TrainerCentralLiveWorkshops()


@mcp.tool()
def tc_create_workshop(session_data: dict, orgId: str, access_token: str) -> dict:
    """
    Create a GLOBAL Live Workshop (deliveryMode = 3).

    Supported recurring types:
      0 → Single session
      1 → Daily (requires recurrence.repeatEvery)
      2 → Weekly (requires weeklyOccurences)
      3 → Monthly (requires monthlyOccurences)

    Example session_data:
      {
        "name": "AI Masterclass",
        "scheduledTime": 1732670000000,
        "scheduledEndTime": 1732673600000,
        "deliveryMode": 3,
        "description": "<div>Learn AI</div>",
        "sessionSettings": {
            "registrationRequired": true,
            "recurringType": 0
        }
      }

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
        dict: workshop creation response
    """
    return workshops.create_global_workshop(session_data, orgId, access_token)


@mcp.tool()
def tc_update_workshop(session_id: str, updates: dict, orgId: str, access_token: str) -> dict:
    """
    Update an existing global workshop.

    Example updates:
      {
        "name": "Updated Name",
        "scheduledTime": 1732670000000,
        "scheduledEndTime": 1732673600000,
        "description": "<div>Updated</div>"
      }

    To cancel:
      { "isCancelled": true }

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
        dict
    """
    return workshops.update_workshop(session_id, updates, orgId, access_token)


@mcp.tool()
def tc_create_workshop_occurrence(talk_data: dict, orgId: str, access_token: str) -> dict:
    """
    Create a new occurrence (talk) for a workshop.

    Example talk_data:
      {
        "sessionId": "19208000000012301",
        "scheduledTime": 1733000000000,
        "scheduledEndTime": 1733003600000,
        "durationTime": 3600000
      }

    Note: Provide orgId and access token of the user, after OAuth, as parameters.    
    
    Returns:
        dict
    """
    return workshops.create_occurrence(talk_data, orgId, access_token)


@mcp.tool()
def tc_update_workshop_occurrence(talk_id: str, updates: dict, orgId: str, access_token: str) -> dict:
    """
    Update a workshop occurrence.

    Example updates:
      {
        "scheduledTime": 1733000000000,
        "scheduledEndTime": 1733003600000,
        "informRegistrants": true
      }

    To cancel occurrence:
      { "isCancelled": true }

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
        dict
    """
    return workshops.update_occurrence(talk_id, updates, orgId, access_token)

@mcp.tool()
def tc_list_all_global_workshops(org_id: str, access_token: str, filter_type: int = 5, limit: int = 50, si: int = 0) -> dict:
    """
    List upcoming global live workshops (not tied to any course).

    Args:
        filter_type (int): 1 = your upcoming, 5 = all upcoming.
        limit (int): Max number of workshops.
        si (int): Start index for pagination.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
        dict: API response with workshop list.
    """
    return workshops.list_all_upcoming_workshops(org_id, access_token, filter_type, limit, si)


@mcp.tool()
def tc_invite_user_to_session(session_id: str, email: str, orgId: str, access_token: str, role: int = 3, source: int = 1) -> dict:
    """
    Invite an existing user (by email) to a course-linked live workshop session.

    Args:
      session_id (str): ID of the session / live workshop.
      email (str): Email ID of the user to invite.
      role (int, optional): Session role for the user (default = 3 → attendee).
      source (int, optional): Source code as per API spec (default = 1).

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Returns:
      dict: JSON response from TrainerCentral API.
    """
    return workshops.invite_user_to_workshop(session_id, email, orgId, access_token, role, source)
