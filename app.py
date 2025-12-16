"""
OrgId Management
"""

import os
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import logging

from tools.portals.portal_handler import tc_get_org_id

from tools.courses.course_handler import (
    tc_create_course,
    tc_get_course,
    tc_list_courses,
    tc_update_course,
    tc_delete_course
)
from tools.chapters.chapter_handler import (
    tc_create_chapter,
    tc_update_chapter,
    tc_delete_chapter
)
from tools.lessons.lesson_handler import (
    tc_create_lesson,
    tc_update_lesson,
    tc_delete_lesson
)
from tools.live_workshops.live_workshop_handler import (
    tc_create_workshop,
    tc_update_workshop,
    tc_create_workshop_occurrence,
    tc_update_workshop_occurrence,
    tc_list_all_global_workshops,
    tc_invite_user_to_session
)
from tools.course_live_workshops.course_live_workshop_handler import (
    tc_create_course_live_session,
    tc_list_course_live_sessions,
    tc_delete_course_live_session,
    invite_learner_to_course_or_course_live_session
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TrainerCentral MCP Server")

DOMAIN = "https://tc-gptt.onrender.com"
AUTH_SERVER = "https://accounts.zoho.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TOOL_REGISTRY = {
    # Portal Management 
    "tc_get_org_id": tc_get_org_id,

    # Courses
    "tc_create_course": tc_create_course,
    "tc_get_course": tc_get_course,
    "tc_list_courses": tc_list_courses,
    "tc_update_course": tc_update_course,
    "tc_delete_course": tc_delete_course,
    
    # Chapters
    "tc_create_chapter": tc_create_chapter,
    "tc_update_chapter": tc_update_chapter,
    "tc_delete_chapter": tc_delete_chapter,
    
    # Lessons
    "tc_create_lesson": tc_create_lesson,
    "tc_update_lesson": tc_update_lesson,
    "tc_delete_lesson": tc_delete_lesson,
    
    # Global Workshops
    "tc_create_workshop": tc_create_workshop,
    "tc_update_workshop": tc_update_workshop,
    "tc_create_workshop_occurrence": tc_create_workshop_occurrence,
    "tc_update_workshop_occurrence": tc_update_workshop_occurrence,
    "tc_list_all_global_workshops": tc_list_all_global_workshops,
    "tc_invite_user_to_session": tc_invite_user_to_session,
    
    # Course Live Workshops
    "tc_create_course_live_session": tc_create_course_live_session,
    "tc_list_course_live_sessions": tc_list_course_live_sessions,
    "tc_delete_course_live_session": tc_delete_course_live_session,
    "invite_learner_to_course_or_course_live_session": invite_learner_to_course_or_course_live_session,
}

logger.info(f"Registered {len(TOOL_REGISTRY)} tools")


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


@app.get("/.well-known/openid-configuration")
async def openid_config():
    return await oauth_server()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "trainercentral-mcp",
        "tools_count": len(TOOL_REGISTRY)
    }


@app.post("/mcp")
@app.post("/mcp/")
async def mcp_handler_alias(request: Request, authorization: Optional[str] = Header(None)):
    """Alias for ChatGPT custom connectors that expect /mcp/ path"""
    return await mcp_handler(request, authorization)


@app.post("/")
async def mcp_handler(request: Request, authorization: Optional[str] = Header(None)):
    """Main MCP endpoint that handles JSON-RPC 2.0 requests"""
    try:
        body = await request.json()
    except Exception:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"}
        }
    
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    logger.info("=" * 80)
    logger.info(f"MCP Request: method={method}")
    logger.info(f"Authorization: {authorization[:50] if authorization else 'None'}...")
    logger.info("=" * 80)

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
        tools_list = [
            # PORTAL MANAGEMENT 
            {
                "name": "tc_get_org_id",
                "description": "Get all portals (organizations) for the authenticated user. IMPORTANT: Call this tool FIRST at the start of every conversation to get the orgId, then use that orgId for all subsequent operations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            
            # COURSES (require orgId)
            {
                "name": "tc_create_course",
                "description": "Create a new course in TrainerCentral. Requires orgId from tc_get_org_id.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string", "description": "Organization ID from tc_get_org_id"},
                        "course_data": {"type": "object", "description": "Course details"}
                    },
                    "required": ["orgId", "course_data"]
                }
            },
            {
                "name": "tc_get_course",
                "description": "Get course details by ID. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"}
                    },
                    "required": ["orgId", "courseId"]
                }
            },
            {
                "name": "tc_list_courses",
                "description": "List all courses. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "limit": {"type": "integer"},
                        "si": {"type": "integer"}
                    },
                    "required": ["orgId"]
                }
            },
            {
                "name": "tc_update_course",
                "description": "Update a course. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["orgId", "courseId", "updates"]
                }
            },
            {
                "name": "tc_delete_course",
                "description": "Delete a course. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"}
                    },
                    "required": ["orgId", "courseId"]
                }
            },
            
            # CHAPTERS (require orgId)
            {
                "name": "tc_create_chapter",
                "description": "Create a chapter. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "section_data": {"type": "object"}
                    },
                    "required": ["orgId", "section_data"]
                }
            },
            {
                "name": "tc_update_chapter",
                "description": "Update a chapter. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"},
                        "section_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["orgId", "courseId", "section_id", "updates"]
                }
            },
            {
                "name": "tc_delete_chapter",
                "description": "Delete a chapter. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"},
                        "section_id": {"type": "string"}
                    },
                    "required": ["orgId", "courseId", "section_id"]
                }
            },
            
            # LESSONS (require orgId)
            {
                "name": "tc_create_lesson",
                "description": "Create a lesson. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_data": {"type": "object"},
                        "content_html": {"type": "string"},
                        "content_filename": {"type": "string"}
                    },
                    "required": ["orgId", "session_data", "content_html"]
                }
            },
            {
                "name": "tc_update_lesson",
                "description": "Update a lesson. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["orgId", "session_id", "updates"]
                }
            },
            {
                "name": "tc_delete_lesson",
                "description": "Delete a lesson. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["orgId", "session_id"]
                }
            },
            
            # WORKSHOPS (require orgId)
            {
                "name": "tc_create_workshop",
                "description": "Create a global workshop. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_data": {"type": "object"}
                    },
                    "required": ["orgId", "session_data"]
                }
            },
            {
                "name": "tc_update_workshop",
                "description": "Update a workshop. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["orgId", "session_id", "updates"]
                }
            },
            {
                "name": "tc_create_workshop_occurrence",
                "description": "Create workshop occurrence. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "talk_data": {"type": "object"}
                    },
                    "required": ["orgId", "talk_data"]
                }
            },
            {
                "name": "tc_update_workshop_occurrence",
                "description": "Update workshop occurrence. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "talk_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["orgId", "talk_id", "updates"]
                }
            },
            {
                "name": "tc_list_all_global_workshops",
                "description": "List workshops. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "filter_type": {"type": "integer"},
                        "limit": {"type": "integer"},
                        "si": {"type": "integer"}
                    },
                    "required": ["orgId"]
                }
            },
            {
                "name": "tc_invite_user_to_session",
                "description": "Invite user. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_id": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "integer"},
                        "source": {"type": "integer"}
                    },
                    "required": ["orgId", "session_id", "email"]
                }
            },
            
            # COURSE LIVE WORKSHOPS (require orgId)
            {
                "name": "tc_create_course_live_session",
                "description": "Create course live session. Requires orgId. Date format: DD-MM-YYYY HH:MMAM/PM",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "courseId": {"type": "string"},
                        "name": {"type": "string"},
                        "description_html": {"type": "string"},
                        "start_time": {"type": "string"},
                        "end_time": {"type": "string"}
                    },
                    "required": ["orgId", "courseId", "name", "description_html", "start_time", "end_time"]
                }
            },
            {
                "name": "tc_list_course_live_sessions",
                "description": "List course live sessions. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "filter_type": {"type": "integer"},
                        "limit": {"type": "integer"},
                        "si": {"type": "integer"}
                    },
                    "required": ["orgId"]
                }
            },
            {
                "name": "tc_delete_course_live_session",
                "description": "Delete course live session. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["orgId", "session_id"]
                }
            },
            {
                "name": "invite_learner_to_course_or_course_live_session",
                "description": "Invite learner. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "courseId": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["orgId", "email", "first_name", "last_name"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_list}
        }
    
    # =========================================================================
    # HANDLE: tools/call - THE KEY SECTION
    # =========================================================================
    elif method == "tools/call":
        # Check authentication
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("No authorization header")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": "Authentication required"}],
                    "_meta": {"mcp/www_authenticate": [f'Bearer resource_metadata="{DOMAIN}/.well-known/oauth-protected-resource"']},
                    "isError": True
                }
            }
        
     
        access_token = authorization.replace("Bearer ", "").strip()
        logger.info(f"Access token: {access_token[:20]}...")
        
        # Get tool info
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool: {tool_name}")
        logger.info(f"Args from ChatGPT: {arguments}")
        
        if tool_name == "tc_get_org_id":
            # Only inject access_token
            arguments["access_token"] = access_token
            logger.info("Special handling for tc_get_org_id - no orgId injection")
        else:
            # For ALL other tools: inject access_token, expect orgId from ChatGPT
            arguments["access_token"] = access_token
            
            # Verify ChatGPT provided orgId
            if "orgId" not in arguments:
                logger.warning(f"⚠️ Tool {tool_name} called without orgId!")
                logger.warning("ChatGPT should call tc_get_org_id first and pass orgId")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": "Error: orgId is required. Please call tc_get_org_id() first to get your organization ID, then pass it to this tool."
                        }],
                        "isError": True
                    }
                }
        
        logger.info(f"Final args: {arguments}")
        
        # Call the tool
        try:
            if tool_name not in TOOL_REGISTRY:
                logger.error(f"Tool not found: {tool_name}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }
            
            tool_func = TOOL_REGISTRY[tool_name]
            result = tool_func(**arguments)
            
            logger.info(f"✅ Tool {tool_name} executed successfully")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
            
        except TypeError as e:
            logger.error(f"❌ TypeError: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Parameter mismatch: {str(e)}"}],
                    "isError": True
                }
            }
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True
                }
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


@app.get("/")
async def root():
    """Root endpoint with instructions for ChatGPT"""
    return {
        "name": "TrainerCentral MCP Server",
        "version": "1.0.0",
        "protocol": "mcp",
        "tools_count": len(TOOL_REGISTRY),
        "tools": list(TOOL_REGISTRY.keys()),
        
        "instructions": """
CRITICAL WORKFLOW FOR ALL CONVERSATIONS:

1. START EVERY CONVERSATION:
   - First action: Call tc_get_org_id() to get user's organization(s)
   - Response: {default_org_id: "...", portals: [...], total_portals: N}

2. IF USER HAS MULTIPLE ORGANIZATIONS (total_portals > 1):
   - Show user the list: "I found 2 organizations: 1) Test (60058756004), 2) Secondary (60061345029)"
   - Ask: "Which organization would you like to use?"
   - Wait for user response
   - Store their chosen orgId

3. IF USER HAS SINGLE ORGANIZATION (total_portals = 1):
   - Automatically use the default_org_id
   - Store it in conversation context
   - Proceed with user's request without asking

4. FOR ALL SUBSEQUENT TOOL CALLS:
   - ALWAYS pass the stored orgId as a parameter
   - Example: tc_create_course(orgId="60058756004", course_data={...})
   - Example: tc_list_courses(orgId="60058756004")

5. MEMORY - CRITICAL:
   - Store orgId in conversation context for the ENTIRE chat session
   - DO NOT call tc_get_org_id() on every request
   - Only call it again if user wants to switch organizations

EXAMPLE CONVERSATION:
User: "Create a Python course"
→ Step 1: Call tc_get_org_id()
→ Step 2: Get {total_portals: 1, default_org_id: "60058756004"}
→ Step 3: Store orgId = "60058756004"
→ Step 4: Call tc_create_course(orgId="60058756004", course_data={...})

User (later): "List my courses"
→ Use stored orgId: "60058756004"
→ Call tc_list_courses(orgId="60058756004")
→ DO NOT call tc_get_org_id() again

IMPORTANT: Call tc_get_org_id() ONCE per conversation, not on every tool call.
        """
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)