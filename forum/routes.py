import httpx
import dotenv
import json
import os

from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from dependencies import authorize, generate_rerouter
from dependencies.schemas import User
from starlette.datastructures import MutableHeaders

dotenv.load_dotenv()
SERVICE_URL = os.environ["FORUM_BE"]

forum_router = APIRouter(
    prefix="/forum",
    tags=["forum"],
    responses={404: {"description": "Not Found"}},
)

async def rerouter(request: Request):
    return await generate_rerouter(SERVICE_URL, request, forum_router.prefix)

from fastapi.openapi.docs import (
    get_swagger_ui_html
)

@forum_router.get("/docs", description="Forum Service Documentation")
async def docs():
    return get_swagger_ui_html(
        openapi_url=f"{SERVICE_URL}/openapi.json",
        title= forum_router.tags[0] + " - Swagger UI",
        oauth2_redirect_url=f"{SERVICE_URL}/docs/oauth2-redirect",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
    )

@forum_router.get("/questions")
async def get_question(result = Depends(rerouter)):
    return result

@forum_router.get("/questions/{question_id}")
async def get_question(result = Depends(rerouter)):
    return result

@forum_router.post("/questions")
async def create_question(request = Request, user: User = Depends(authorize)):
    try:
        username = user.username
        body = await request.body()
        body_dict: dict = json.loads(body)
        body_dict["owner"] = username

        mutable_headers = MutableHeaders(request._headers)
        mutable_headers["content-length"] = str(len(request._body))
    
        request._headers = mutable_headers
        request.scope.update(headers=mutable_headers.raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not a valid JSON"
        )   
    
    return await rerouter(request=request)

@forum_router.get("/answers")
async def get_answer(result = Depends(rerouter)):
    return result

@forum_router.post("/answers")
async def create_answer(request = Request, user: User = Depends(authorize)):
    try:
        username = user.username
        body = await request.body()
        body_dict: dict = json.loads(body)
        body_dict["owner"] = username

        mutable_headers = MutableHeaders(request._headers)
        mutable_headers["content-length"] = str(len(request._body))
    
        request._headers = mutable_headers
        request.scope.update(headers=mutable_headers.raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not a valid JSON"
        )   
    
    return await rerouter(request=request)

@forum_router.get("/comments")
async def get_comments(result = Depends(rerouter)):
    return result

@forum_router.post("/comments")
async def create_comments(request = Request, user: User = Depends(authorize)):
    try:
        username = user.username
        body = await request.body()
        body_dict: dict = json.loads(body)
        body_dict["owner"] = username

        mutable_headers = MutableHeaders(request._headers)
        mutable_headers["content-length"] = str(len(request._body))
    
        request._headers = mutable_headers
        request.scope.update(headers=mutable_headers.raw)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not a valid JSON"
        )   
    
    return await rerouter(request=request)
