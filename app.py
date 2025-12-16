"""
COMPLETE WORKING APP.PY - No Syntax Errors
Fixed domain configuration and proper orgId handling
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
    tc_get_course_lessons,
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


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://tc-gptt.onrender.com")
TC_API_BASE_URL = os.getenv("TC_API_BASE_URL", "https://myacademy.trainercentral.in")
AUTH_SERVER = "https://accounts.zoho.in"

logger.info(f"MCP Server: {MCP_SERVER_URL}")
logger.info(f"TC API: {TC_API_BASE_URL}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TOOL_REGISTRY = {
    "tc_get_org_id": tc_get_org_id,
    "tc_create_course": tc_create_course,
    "tc_get_course": tc_get_course,
    "tc_list_courses": tc_list_courses,
    "tc_update_course": tc_update_course,
    "tc_delete_course": tc_delete_course,
    "tc_create_chapter": tc_create_chapter,
    "tc_update_chapter": tc_update_chapter,
    "tc_delete_chapter": tc_delete_chapter,
    "tc_create_lesson": tc_create_lesson,
    "tc_get_course_lessons": tc_get_course_lessons,
    "tc_update_lesson": tc_update_lesson,
    "tc_delete_lesson": tc_delete_lesson,
    "tc_create_workshop": tc_create_workshop,
    "tc_update_workshop": tc_update_workshop,
    "tc_create_workshop_occurrence": tc_create_workshop_occurrence,
    "tc_update_workshop_occurrence": tc_update_workshop_occurrence,
    "tc_list_all_global_workshops": tc_list_all_global_workshops,
    "tc_invite_user_to_session": tc_invite_user_to_session,
    "tc_create_course_live_session": tc_create_course_live_session,
    "tc_list_course_live_sessions": tc_list_course_live_sessions,
    "tc_delete_course_live_session": tc_delete_course_live_session,
    "invite_learner_to_course_or_course_live_session": invite_learner_to_course_or_course_live_session,
}

logger.info(f"Registered {len(TOOL_REGISTRY)} tools")


@app.get("/.well-known/oauth-protected-resource")
async def oauth_metadata():
    return {
        "resource": MCP_SERVER_URL,
        "authorization_servers": [AUTH_SERVER],
        "scopes_supported": [
            "TrainerCentral.sessionapi.ALL",
            "TrainerCentral.sectionapi.ALL",
            "TrainerCentral.courseapi.ALL",
            "TrainerCentral.userapi.ALL",
            "TrainerCentral.talkapi.ALL",
            "TrainerCentral.portalapi.READ"
        ],
        "resource_documentation": f"{MCP_SERVER_URL}/docs"
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
    return await mcp_handler(request, authorization)


@app.post("/")
async def mcp_handler(request: Request, authorization: Optional[str] = Header(None)):
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
    logger.info(f"Method: {method}")
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
            {
                "name": "tc_get_org_id",
                "description": "Get organizations. Call FIRST in every conversation.",
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "tc_create_course",
                "description": "Create course. Requires orgId.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string"},
                        "course_data": {"type": "object"}
                    },
                    "required": ["orgId", "course_data"]
                }
            },
            {
                "name": "tc_get_course",
                "description": "Get course. Requires orgId.",
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
                "description": "List courses. Requires orgId.",
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
                "description": "Update course. Requires orgId.",
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
                "description": "Delete course. Requires orgId.",
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
                "name": "tc_create_chapter",
                "description": "Create chapter. Requires orgId.",
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
                "description": "Update chapter. Requires orgId.",
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
                "description": "Delete chapter. Requires orgId.",
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
            {
                "name": "tc_create_lesson",
                "description": "Create lesson. Requires orgId.",
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
                "name": "tc_get_course_lessons",
                "description": "Get all lessons (sessions) for a specific course. Useful before creating tests or understanding course structure.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orgId": {"type": "string", "description": "Organization ID from tc_get_org_id"},
                        "courseId": {"type": "string", "description": "Course ID"}
                    },
                    "required": ["orgId", "courseId"]
                }
            },
            {
                "name": "tc_update_lesson",
                "description": "Update lesson. Requires orgId.",
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
                "description": "Delete lesson. Requires orgId.",
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
                "name": "tc_create_workshop",
                "description": "Create workshop. Requires orgId.",
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
                "description": "Update workshop. Requires orgId.",
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
            {
                "name": "tc_create_course_live_session",
                "description": "Create course live session. Requires orgId.",
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
    
    elif method == "tools/call":
        if not authorization or not authorization.startswith("Bearer "):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": "Authentication required"}],
                    "isError": True
                }
            }
        
        access_token = authorization.replace("Bearer ", "").strip()
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool: {tool_name}")
        logger.info(f"Args: {arguments}")
        
        if tool_name == "tc_get_org_id":
            arguments["access_token"] = access_token
        else:
            arguments["access_token"] = access_token
            if "orgId" not in arguments:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": "orgId required. Call tc_get_org_id() first."}],
                        "isError": True
                    }
                }
        
        try:
            if tool_name not in TOOL_REGISTRY:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }
            
            tool_func = TOOL_REGISTRY[tool_name]
            result = tool_func(**arguments)
            
            logger.info(f"✅ Success")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
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
    return {
        "name": "TrainerCentral MCP Server",
        "version": "1.0.0",
        "protocol": "mcp",
        "tools_count": len(TOOL_REGISTRY),
        "tools": list(TOOL_REGISTRY.keys()),
        "instructions": "Call tc_get_org_id() first to get orgId, then pass it to all other tools."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)