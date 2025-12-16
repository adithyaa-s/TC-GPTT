"""
Portal management tools
"""

from library.oauth import (
    get_user_portals,
    extract_default_org_id,
    extract_all_org_ids,
)


def tc_get_org_id(access_token: str) -> dict:
    """
    Get all portals (organizations) for the authenticated user.

    This tool should be called ONCE at the start of a conversation to:
    1. Retrieve all available portals for the user
    2. Get the default portal's orgId
    3. Store orgIds for use in subsequent tool calls

    Returns:
        dict: {
            "portals": [...],
            "default_org_id": "60058756004",
            "all_org_ids": ["60058756004", "60061345029"],
            "total_portals": 2
        }
    """
    portals_data = get_user_portals(access_token)

    default_org_id = extract_default_org_id(portals_data)
    all_org_ids = extract_all_org_ids(portals_data)

    portals = portals_data.get("portals", [])

    return {
        "portals": portals,
        "default_org_id": default_org_id,
        "all_org_ids": all_org_ids,
        "total_portals": len(portals),
    }
