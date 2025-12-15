"""
COMPLETE WORKING APP.PY WITH CONSISTENT AUTH INJECTION

Key Changes:
1. ALL functions now consistently use 'orgId' and 'access_token' as LAST two parameters
2. Auth injection works for ALL tools
3. Proper logging
"""

import os
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import logging
from fastapi.responses import JSONResponse

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
from library.oauth import get_orgId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="TrainerCentral MCP Server")


DOMAIN = os.getenv("DOMAIN", "https://tc-tgpt-auth.onrender.com")
AUTH_SERVER = "https://accounts.zoho.in"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TOOL_REGISTRY = {
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
        "service": "trainercentral-mcp",
        "tools_count": len(TOOL_REGISTRY)
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
    
    # Log the request
    logger.info("=" * 80)
    logger.info(f"MCP Request: method={method}")
    logger.info(f"Authorization header: {authorization}")
    logger.info("=" * 80)
    
    # Handle MCP protocol methods that DON'T need auth
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
        # Return tool schemas (no auth needed)
        tools_list = [
            # COURSES
            {"name": "tc_create_course", "description": "Create a new course in TrainerCentral", 
             "inputSchema": {"type": "object", "properties": {"course_data": {"type": "object"}}, "required": ["course_data"]}},
            {"name": "tc_get_course", "description": "Get course details by ID", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}}, "required": ["course_id"]}},
            {"name": "tc_list_courses", "description": "List all courses", 
             "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}, "si": {"type": "integer"}}}},
            {"name": "tc_update_course", "description": "Update a course", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["course_id", "updates"]}},
            {"name": "tc_delete_course", "description": "Delete a course", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}}, "required": ["course_id"]}},
            
            # CHAPTERS
            {"name": "tc_create_chapter", "description": "Create a chapter under a course", 
             "inputSchema": {"type": "object", "properties": {"section_data": {"type": "object"}}, "required": ["section_data"]}},
            {"name": "tc_update_chapter", "description": "Update a chapter", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}, "section_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["course_id", "section_id", "updates"]}},
            {"name": "tc_delete_chapter", "description": "Delete a chapter", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}, "section_id": {"type": "string"}}, "required": ["course_id", "section_id"]}},
            
            # LESSONS
            {"name": "tc_create_lesson", "description": "Create a lesson with content", 
             "inputSchema": {"type": "object", "properties": {"session_data": {"type": "object"}, "content_html": {"type": "string"}, "content_filename": {"type": "string"}}, "required": ["session_data", "content_html"]}},
            {"name": "tc_update_lesson", "description": "Update a lesson", 
             "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["session_id", "updates"]}},
            {"name": "tc_delete_lesson", "description": "Delete a lesson", 
             "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]}},
            
            # GLOBAL WORKSHOPS
            {"name": "tc_create_workshop", "description": "Create a global live workshop", 
             "inputSchema": {"type": "object", "properties": {"session_data": {"type": "object"}}, "required": ["session_data"]}},
            {"name": "tc_update_workshop", "description": "Update a workshop", 
             "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["session_id", "updates"]}},
            {"name": "tc_create_workshop_occurrence", "description": "Create a workshop occurrence", 
             "inputSchema": {"type": "object", "properties": {"talk_data": {"type": "object"}}, "required": ["talk_data"]}},
            {"name": "tc_update_workshop_occurrence", "description": "Update a workshop occurrence", 
             "inputSchema": {"type": "object", "properties": {"talk_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["talk_id", "updates"]}},
            {"name": "tc_list_all_global_workshops", "description": "List all upcoming global workshops", 
             "inputSchema": {"type": "object", "properties": {"filter_type": {"type": "integer"}, "limit": {"type": "integer"}, "si": {"type": "integer"}}}},
            {"name": "tc_invite_user_to_session", "description": "Invite user to a session", 
             "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}, "email": {"type": "string"}, "role": {"type": "integer"}, "source": {"type": "integer"}}, "required": ["session_id", "email"]}},
            
            # COURSE LIVE WORKSHOPS
            {"name": "tc_create_course_live_session", "description": "Create a live workshop inside a course. Date format: DD-MM-YYYY HH:MMAM/PM", 
             "inputSchema": {"type": "object", "properties": {"course_id": {"type": "string"}, "name": {"type": "string"}, "description_html": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}, "required": ["course_id", "name", "description_html", "start_time", "end_time"]}},
            {"name": "tc_list_course_live_sessions", "description": "List upcoming course live sessions", 
             "inputSchema": {"type": "object", "properties": {"filter_type": {"type": "integer"}, "limit": {"type": "integer"}, "si": {"type": "integer"}}}},
            {"name": "tc_delete_course_live_session", "description": "Delete a course live session", 
             "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]}},
            {"name": "invite_learner_to_course_or_course_live_session", "description": "Invite a learner to a course or course live session", 
             "inputSchema": {"type": "object", "properties": {"email": {"type": "string"}, "first_name": {"type": "string"}, "last_name": {"type": "string"}, "course_id": {"type": "string"}, "session_id": {"type": "string"}}, "required": ["email", "first_name", "last_name"]}},
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools_list}
        }
    
    elif method == "tools/call":
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("No authorization header provided")
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
        
        try:
            orgId = get_orgId(access_token)
            logger.info(f"Retrieved orgId: {orgId}")
        except Exception as e:
            logger.error(f"Failed to get orgId: {str(e)}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Failed to retrieve organization ID: {str(e)}"}],
                    "isError": True
                }
            }
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool: {tool_name}")
        logger.info(f"Args from ChatGPT: {arguments}")
        
        arguments["orgId"] = orgId
        arguments["access_token"] = access_token
        
        logger.info(f"Args after injection: {arguments}")
        
        try:
            if tool_name not in TOOL_REGISTRY:
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
            logger.error(f"Function signature mismatch for {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": f"Parameter mismatch: {str(e)}"}],
                    "isError": True
                }
            }
        except Exception as e:
            logger.error(f"❌ Error executing {tool_name}: {str(e)}", exc_info=True)
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
        "tools": list(TOOL_REGISTRY.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)