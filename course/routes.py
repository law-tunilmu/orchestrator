import httpx
import pydantic
import json
import os

from fastapi import APIRouter, Request, Depends, HTTPException, status
from dependencies import authorize, generate_rerouter
from dependencies.schemas import User, USER_ROLES
from starlette.datastructures import MutableHeaders
from .schemas import Course, CourseFromUser

SERVICE_URL = os.environ["COURSE_BE"]

course_router = APIRouter(
    prefix="/course",
    tags=["course"],
    responses={404: {"description" : "Not Found"}}
)

async def rerouter(request: Request):
    return await generate_rerouter(SERVICE_URL, request)

async def get_course(id: int, request: Request) -> Course:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url = SERVICE_URL + f"/course/detail/{id}"
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=resp.json()['detail']
            )
        else:
            return Course.model_validate(resp.json())

@course_router.get("/docs")
async def docs(result = Depends(rerouter)):
    return result

@course_router.get("/list")
async def list(result = Depends(rerouter)):
    return result

@course_router.get("/detail/{id}")
async def get(result = Depends(rerouter)):
    return result

@course_router.get("/search")
async def search(result = Depends(rerouter)):
    return result

@course_router.get("/created_by")
async def search(result = Depends(rerouter)):
    return result

@course_router.post("/create")
async def create(request: Request, user: User = Depends(authorize)):
    if user.role != USER_ROLES.MENTOR.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student can not create a course"
        )
    body = await request.body()
    try:
        body_dict: dict = json.loads(body)
        body_dict["creator"] = user.username
        request._body = json.dumps(body_dict).encode()

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

@course_router.put("/edit")
async def edit(course: CourseFromUser, request: Request, user: User = Depends(authorize)):
    in_db_course = await get_course(course.id, request)

    if user.username != in_db_course.creator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can not edit this course"
        )

    return await rerouter(request=request)

@course_router.delete("/delete")
async def delete(id: int, request: Request, user: User = Depends(authorize)):

    in_db_course = await get_course(id, request)

    if user.username != in_db_course.creator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You can not delete this course"
        )

    return await rerouter(request=request)
