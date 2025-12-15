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
#     host="127.0.0.1",
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
import logging
from fastapi.responses import JSONResponse

from tools.mcp_registry import get_mcp

# Import all your handlers to register tools
import tools.courses.course_handler
import tools.chapters.chapter_handler
import tools.lessons.lesson_handler
import tools.live_workshops.live_workshop_handler
import tools.course_live_workshops.course_live_workshop_handler


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MCP instance
mcp = get_mcp()

# Initialize FastMCP with HTTP transport to create the app
# This is the key - we need to call _create_http_server() to get the app
from fastapi import FastAPI
app = FastAPI(title="TrainerCentral MCP Server")

# Configuration
DOMAIN = os.getenv("DOMAIN", "https://tc-cgpt.onrender.com")
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

# # Health check
# @app.get("/health")
# async def health():
#     return {
#         "status": "healthy",
#         "service": "trainercentral-mcp"
#     }

# # Main MCP endpoint - handles all tool calls
# @app.post("/")
# async def mcp_handler(request: Request, authorization: Optional[str] = Header(None)):
#     """
#     Main MCP endpoint that handles JSON-RPC 2.0 requests
#     """
#     try:
#         body = await request.json()
#     except Exception:
#         return {
#             "jsonrpc": "2.0",
#             "error": {
#                 "code": -32700,
#                 "message": "Parse error"
#             }
#         }
    
#     method = body.get("method")
#     params = body.get("params", {})
#     request_id = body.get("id")
    
#     # Handle MCP protocol methods
#     if method == "initialize":
#         return {
#             "jsonrpc": "2.0",
#             "id": request_id,
#             "result": {
#                 "protocolVersion": "2024-11-05",
#                 "capabilities": {"tools": {}},
#                 "serverInfo": {
#                     "name": "trainercentral-fastmcp",
#                     "version": "1.0.0"
#                 }
#             }
#         }
    
#     elif method == "tools/list":
#         # Get all registered FastMCP tools
#         tools_list = []
        
#         for tool_name, tool_func in mcp._tools.items():
#             tool_schema = {
#                 "name": tool_name,
#                 "description": tool_func.__doc__ or f"Execute {tool_name}",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {},
#                     "required": []
#                 }
#             }
            
#             # Add OAuth requirement
#             tool_schema["securitySchemes"] = [{
#                 "type": "oauth2",
#                 "scopes": [
#                     "TrainerCentral.sessionapi.ALL",
#                     "TrainerCentral.sectionapi.ALL",
#                     "TrainerCentral.courseapi.ALL",
#                     "TrainerCentral.userapi.ALL",
#                     "TrainerCentral.talkapi.ALL",
#                     "TrainerCentral.portalapi.READ"
#                 ]
#             }]
            
#             tools_list.append(tool_schema)
        
#         return {
#             "jsonrpc": "2.0",
#             "id": request_id,
#             "result": {"tools": tools_list}
#         }
    
#     elif method == "tools/call":
#         # Check authentication
#         if not authorization or not authorization.startswith("Bearer "):
#             return {
#                 "jsonrpc": "2.0",
#                 "id": request_id,
#                 "result": {
#                     "content": [{
#                         "type": "text",
#                         "text": "Authentication required: no access token provided."
#                     }],
#                     "_meta": {
#                         "mcp/www_authenticate": [
#                             f'Bearer resource_metadata="{DOMAIN}/.well-known/oauth-protected-resource", '
#                             f'error="insufficient_scope", error_description="You need to login to continue"'
#                         ]
#                     },
#                     "isError": True
#                 }
#             }
        
#         # Extract tool name and arguments
#         tool_name = params.get("name")
#         arguments = params.get("arguments", {})
        
#         # Add auth info to arguments
#         access_token = authorization.replace("Bearer ", "")
#         org_id = os.getenv("ORG_ID", "")
        
#         arguments["orgId"] = org_id
#         arguments["access_token"] = access_token
        
#         try:
#             # Call the FastMCP tool
#             if tool_name in mcp._tools:
#                 result = mcp._tools[tool_name](**arguments)
                
#                 return {
#                     "jsonrpc": "2.0",
#                     "id": request_id,
#                     "result": {
#                         "content": [{
#                             "type": "text",
#                             "text": json.dumps(result, indent=2)
#                         }]
#                     }
#                 }
#             else:
#                 return {
#                     "jsonrpc": "2.0",
#                     "id": request_id,
#                     "error": {
#                         "code": -32601,
#                         "message": f"Tool not found: {tool_name}"
#                     }
#                 }
#         except Exception as e:
#             return {
#                 "jsonrpc": "2.0",
#                 "id": request_id,
#                 "result": {
#                     "content": [{
#                         "type": "text",
#                         "text": f"Error executing {tool_name}: {str(e)}"
#                     }],
#                     "isError": True
#                 }
#             }
    
#     else:
#         return {
#             "jsonrpc": "2.0",
#             "id": request_id,
#             "error": {
#                 "code": -32601,
#                 "message": f"Method not found: {method}"
#             }
#         }


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
        # Manually define tool schemas for ChatGPT
        # This ensures ChatGPT knows exactly how to call each tool
        tools_list = [
            # COURSES
            {
                "name": "tc_create_course",
                "description": "Create a new course in TrainerCentral",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_data": {
                            "type": "object",
                            "description": "Course details (courseName, subTitle, description, courseCategories)"
                        }
                    },
                    "required": ["course_data"]
                }
            },
            {
                "name": "tc_get_course",
                "description": "Get course details by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"}
                    },
                    "required": ["course_id"]
                }
            },
            {
                "name": "tc_list_courses",
                "description": "List all courses",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer"},
                        "si": {"type": "integer"}
                    }
                }
            },
            {
                "name": "tc_update_course",
                "description": "Update a course",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["course_id", "updates"]
                }
            },
            {
                "name": "tc_delete_course",
                "description": "Delete a course",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"}
                    },
                    "required": ["course_id"]
                }
            },
            
            # CHAPTERS
            {
                "name": "tc_create_chapter",
                "description": "Create a chapter under a course",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "section_data": {
                            "type": "object",
                            "properties": {
                                "courseId": {"type": "string"},
                                "name": {"type": "string"}
                            },
                            "required": ["courseId", "name"]
                        }
                    },
                    "required": ["section_data"]
                }
            },
            {
                "name": "tc_update_chapter",
                "description": "Update a chapter",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "section_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["course_id", "section_id", "updates"]
                }
            },
            {
                "name": "tc_delete_chapter",
                "description": "Delete a chapter",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "section_id": {"type": "string"}
                    },
                    "required": ["course_id", "section_id"]
                }
            },
            
            # LESSONS
            {
                "name": "tc_create_lesson",
                "description": "Create a lesson with content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_data": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "courseId": {"type": "string"},
                                "sectionId": {"type": "string"},
                                "deliveryMode": {"type": "integer", "default": 4}
                            },
                            "required": ["name", "courseId"]
                        },
                        "content_html": {"type": "string"},
                        "content_filename": {"type": "string", "default": "Content"}
                    },
                    "required": ["session_data", "content_html"]
                }
            },
            {
                "name": "tc_update_lesson",
                "description": "Update a lesson",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["session_id", "updates"]
                }
            },
            {
                "name": "tc_delete_lesson",
                "description": "Delete a lesson",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                }
            },
            
            # LIVE WORKSHOPS (GLOBAL)
            {
                "name": "tc_create_workshop",
                "description": "Create a global live workshop",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_data": {"type": "object"}
                    },
                    "required": ["session_data"]
                }
            },
            {
                "name": "tc_update_workshop",
                "description": "Update a workshop",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["session_id", "updates"]
                }
            },
            {
                "name": "tc_create_workshop_occurrence",
                "description": "Create a workshop occurrence",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "talk_data": {"type": "object"}
                    },
                    "required": ["talk_data"]
                }
            },
            {
                "name": "tc_update_workshop_occurrence",
                "description": "Update a workshop occurrence",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "talk_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["talk_id", "updates"]
                }
            },
            {
                "name": "tc_list_all_global_workshops",
                "description": "List all upcoming global workshops",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "org_id": {"type": "string"},
                        "filter_type": {"type": "integer", "default": 5},
                        "limit": {"type": "integer", "default": 50},
                        "si": {"type": "integer", "default": 0}
                    },
                    "required": ["org_id"]
                }
            },
            {
                "name": "tc_invite_user_to_session",
                "description": "Invite user to a session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "integer", "default": 3},
                        "source": {"type": "integer", "default": 1}
                    },
                    "required": ["session_id", "email"]
                }
            },
            
            # COURSE LIVE WORKSHOPS
            {
                "name": "tc_create_course_live_session",
                "description": "Create a live workshop inside a course. Date format: DD-MM-YYYY HH:MMAM/PM",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description_html": {"type": "string"},
                        "start_time": {"type": "string", "description": "Format: DD-MM-YYYY HH:MMAM/PM"},
                        "end_time": {"type": "string", "description": "Format: DD-MM-YYYY HH:MMAM/PM"}
                    },
                    "required": ["course_id", "name", "description_html", "start_time", "end_time"]
                }
            },
            {
                "name": "tc_list_course_live_sessions",
                "description": "List upcoming course live sessions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter_type": {"type": "integer", "default": 5},
                        "limit": {"type": "integer", "default": 50},
                        "si": {"type": "integer", "default": 0}
                    }
                }
            },
            {
                "name": "tc_delete_course_live_session",
                "description": "Delete a course live session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "invite_learner_to_course_or_course_live_session",
                "description": "Invite a learner to a course or course live session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "course_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "is_access_granted": {"type": "boolean", "default": True},
                        "expiry_time": {"type": "integer"},
                        "expiry_duration": {"type": "string"}
                    },
                    "required": ["email", "first_name", "last_name"]
                }
            }
        ]
        
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
            if tool_name in mcp._mcp_tools:
                result = mcp._mcp_tools[tool_name](**arguments)
                
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
