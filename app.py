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
App.py for uvicorn - properly initializes FastMCP with HTTP transport
"""

import os
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json

from tools.mcp_registry import get_mcp

# Import all your handlers to register tools
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
import tools.course_live_workshops.course_live_workshop_handler

# Get MCP instance
mcp = get_mcp()

# Initialize FastMCP with HTTP transport to create the app
# This is the key - we need to call _create_http_server() to get the app
from fastapi import FastAPI
app = FastAPI(title="TrainerCentral MCP Server")

# Configuration
DOMAIN = os.getenv("DOMAIN", "https://tc-tgpt-auth.onrender.com")
AUTH_SERVER = "https://accounts.zoho.in"

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# OpenID Connect Discovery
@app.get("/.well-known/openid-configuration")
async def openid_config():
    return await oauth_server()

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "trainercentral-mcp"
    }

# Main MCP endpoint - handles all tool calls
@app.post("/")
async def mcp_handler(request: Request, authorization: Optional[str] = Header(None)):
    """
    Main MCP endpoint that handles JSON-RPC 2.0 requests
    """
    try:
        body = await request.json()
    except Exception:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }
    
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    # Handle MCP protocol methods
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "trainercentral-fastmcp",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "tools/list":
        # Get all registered FastMCP tools
        tools_list = []
        
        for tool_name, tool_func in mcp._tools.items():
            tool_schema = {
                "name": tool_name,
                "description": tool_func.__doc__ or f"Execute {tool_name}",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add OAuth requirement
            tool_schema["securitySchemes"] = [{
                "type": "oauth2",
                "scopes": [
                    "TrainerCentral.sessionapi.ALL",
                    "TrainerCentral.sectionapi.ALL",
                    "TrainerCentral.courseapi.ALL",
                    "TrainerCentral.userapi.ALL",
                    "TrainerCentral.talkapi.ALL",
                    "TrainerCentral.portalapi.READ"
                ]
            }]
            
            tools_list.append(tool_schema)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_list}
        }
    
    elif method == "tools/call":
        # Check authentication
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
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
        
        # Extract tool name and arguments
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Add auth info to arguments
        access_token = authorization.replace("Bearer ", "")
        org_id = os.getenv("ORG_ID", "")
        
        arguments["orgId"] = org_id
        arguments["access_token"] = access_token
        
        try:
            # Call the FastMCP tool
            if tool_name in mcp._tools:
                result = mcp._tools[tool_name](**arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }],
                    "isError": True
                }
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

@app.get("/")
async def root():
    """Root endpoint - server info"""
    return {
        "name": "TrainerCentral MCP Server",
        "version": "1.0.0",
        "protocol": "mcp"
    }


# For running directly with python app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)