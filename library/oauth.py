import requests
import logging

logger = logging.getLogger(__name__)


def get_user_portals(access_token: str) -> dict:
    """
    Retrieve all portals (organizations) for the authenticated user.
    """
    url = "https://myacademy.trainercentral.in/api/v4/org/portals.json"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        logger.info("Fetching user portals")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        data = resp.json()

        portals = data.get("portals", [])
        logger.info("Retrieved %d portals", len(portals))

        return data

    except requests.RequestException as e:
        logger.exception("Failed to get portals")
        raise RuntimeError("Failed to retrieve portals") from e


def extract_default_org_id(portals_data: dict) -> str:
    """
    Extract the default portal's orgId.
    """
    portals = portals_data.get("portals", [])

    for portal in portals:
        if portal.get("isDefault") == "true":
            org_id = portal.get("id")
            logger.info(
                "Found default portal: %s (%s)",
                org_id,
                portal.get("portalName")
            )
            return org_id

    if portals:
        org_id = portals[0].get("id")
        logger.warning("No default portal, using first: %s", org_id)
        return org_id

    raise ValueError("No portals found for this user")


def extract_all_org_ids(portals_data: dict) -> list[str]:
    """
    Extract all orgIds for the user.
    
    Returns:
        list[str]: ["60058756004", "60061345029"]
    """
    portals = portals_data.get("portals", [])

    org_ids = [
        portal["id"]
        for portal in portals
        if "id" in portal
    ]

    if not org_ids:
        raise ValueError("No orgIds found for this user")

    logger.info("Extracted orgIds: %s", org_ids)
    return org_ids
