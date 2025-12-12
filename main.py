# from tools.mcp_registry import get_mcp
# import tools.courses.course_handler
# import tools.chapters.chapter_handler
# import tools.lessons.lesson_handler
# import tools.live_workshops.live_workshop_handler
# # import tools.assignments.assignment_handler
# # import tools.tests.test_handler
# # import tools.course_live_workshops.course_live_workshop_handler

# def main():
#     mcp = get_mcp()
#     # mcp.run()
#     mcp.run(
#     transport="http",
#     host="0.0.0.0",
#     port=8000
# )

# if __name__ == "__main__":
#     main()


"""
Enhanced main.py that adds OAuth endpoints for ChatGPT
Minimal changes to your existing structure
"""

import os
from tools.mcp_registry import get_mcp
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
# import tools.assignments.assignment_handler
# import tools.tests.test_handler
# import tools.course_live_workshops.course_live_workshop_handler


def add_oauth_endpoints(mcp_instance):
    """
    Add OAuth discovery endpoints that ChatGPT needs.
    This extends your FastMCP server with the required endpoints.
    """
    from fastapi import FastAPI, Request, Header
    from fastapi.middleware.cors import CORSMiddleware
    from typing import Optional
    import json
    
    # Get the FastAPI app from FastMCP
    app = mcp_instance.app
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configuration
    DOMAIN = os.getenv("DOMAIN", "https://tc-cgpt.onrender.com")
    AUTH_SERVER = "https://accounts.zoho.in"
    
    # OAuth Protected Resource Metadata
    @app.get("/.well-known/oauth-protected-resource")
    async def oauth_metadata():
        return {
            "resource": DOMAIN,
            "authorization_servers": [AUTH_SERVER],
            "scopes_supported": [
                "TrainerCentral.sessionapi.ALL",
                "TrainerCentral.sectionapi.ALL",
                "TrainerCentral.courseapi.ALL",
                "TrainerCentral.userapi.ALL",
                "TrainerCentral.talkapi.ALL",
                "TrainerCentral.portalapi.READ"
            ],
            "resource_documentation": f"{DOMAIN}/docs"
        }
    
    # OAuth Authorization Server Metadata
    @app.get("/.well-known/oauth-authorization-server")
    async def oauth_server():
        return {
            "issuer": AUTH_SERVER,
            "authorization_endpoint": f"{AUTH_SERVER}/oauth/v2/auth",
            "token_endpoint": f"{AUTH_SERVER}/oauth/v2/token",
            "scopes_supported": [
                "TrainerCentral.sessionapi.ALL",
                "TrainerCentral.sectionapi.ALL",
                "TrainerCentral.courseapi.ALL",
                "TrainerCentral.userapi.ALL",
                "TrainerCentral.talkapi.ALL",
                "TrainerCentral.portalapi.READ"
            ],
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"]
        }
    
    # OpenID Connect Discovery (alternative)
    @app.get("/.well-known/openid-configuration")
    async def openid_config():
        return await oauth_server()
    
    # Health check
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "service": "trainercentral-mcp",
            "tools_count": len(mcp_instance._tools)
        }
    
    # Enhance the root endpoint to handle authentication
    original_root = None
    for route in app.routes:
        if route.path == "/" and "POST" in route.methods:
            original_root = route.endpoint
            break
    
    if original_root:
        @app.post("/")
        async def enhanced_root(request: Request, authorization: Optional[str] = Header(None)):
            """Enhanced root endpoint with auth injection"""
            try:
                body = await request.json()
                method = body.get("method")
                
                # Handle tools/call with authentication
                if method == "tools/call":
                    if not authorization or not authorization.startswith("Bearer "):
                        return {
                            "jsonrpc": "2.0",
                            "id": body.get("id"),
                            "result": {
                                "content": [{
                                    "type": "text",
                                    "text": "Authentication required: no access token provided."
                                }],
                                "_meta": {
                                    "mcp/www_authenticate": [
                                        f'Bearer resource_metadata="{DOMAIN}/.well-known/oauth-protected-resource", '
                                        f'error="insufficient_scope", error_description="You need to login to continue"'
                                    ]
                                },
                                "isError": True
                            }
                        }
                    
                    # Inject auth into arguments
                    params = body.get("params", {})
                    arguments = params.get("arguments", {})
                    arguments["orgId"] = os.getenv("ORG_ID", "")
                    arguments["access_token"] = authorization.replace("Bearer ", "")
                    
                    # Update the body
                    body["params"]["arguments"] = arguments
                    
                    # Create a new request with modified body
                    from starlette.datastructures import Headers
                    from starlette.requests import Request as StarletteRequest
                    
                    scope = request.scope.copy()
                    scope["body"] = json.dumps(body).encode()
                    
                    modified_request = StarletteRequest(scope)
                    return await original_root(modified_request, authorization)
                
                # For other methods, call original
                return await original_root(request, authorization)
            
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id") if 'body' in locals() else 1,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }


def main():
    # Get your MCP instance
    mcp = get_mcp()
    
    # Add OAuth endpoints
    add_oauth_endpoints(mcp)
    
    # Run with HTTP transport
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )


if __name__ == "__main__":
    main()