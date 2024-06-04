import httpx
import dotenv
import json
import os

from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from dependencies import authorize, generate_rerouter
from dependencies.schemas import User
from course.routes import get_course
from starlette.datastructures import MutableHeaders

dotenv.load_dotenv()
SERVICE_URL = os.environ["TRANSACTION_BE"]
COURSE_SERVICE_URL = os.environ["COURSE_BE"]


transaction_router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"],
    responses={404: {"description": "Not Found"}},
)

async def rerouter(request: Request):
    return await generate_rerouter(SERVICE_URL, request)


from fastapi.openapi.docs import (
    get_swagger_ui_html
)

# DONE
@transaction_router.get("/docs", description="Transaction Service Documentation")
async def docs():
    return get_swagger_ui_html(
        openapi_url=f"{SERVICE_URL}/openapi.json",
        title= transaction_router.tags[0] + " - Swagger UI",
        oauth2_redirect_url=f"{SERVICE_URL}/docs/oauth2-redirect",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
    )

# --- Endpoints for the microservice rerouting ---
# DONE
@transaction_router.get("/cart")
async def get_cart(user: User = Depends(authorize)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                    url = SERVICE_URL + f"/transaction/cart/{user.email}"
                )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=resp.json()['message']
                )
            else:
                courses = resp.json()["courses_in_cart"]

                course_responses = []
                for course in courses:
                    course_id = course["course_id"]
                    resp = await client.get(
                        url = COURSE_SERVICE_URL + f"/course/detail/{course_id}"
                    )
                    if resp.status_code != 200:
                        raise HTTPException(
                            status_code=resp.status_code,
                            detail=resp.json()['detail']
                        )
                    else:
                        print(resp.json())

                        course_responses.append(resp.json())
        except Exception as e:
            print(e)
        return course_responses
    

                



# DONE    
@transaction_router.get("/course_owned")
async def get_owned_courses(user: User = Depends(authorize)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
                url = SERVICE_URL + f"/transaction/course_owned/{user.email}"
            )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=resp.json()['message']
            )
        else:
            courses = resp.json()["course_list"]

            course_responses = []
            for course in courses:
                course_id = course["course_id"]
                resp = await client.get(
                    url = COURSE_SERVICE_URL + f"/course/detail/{course_id}"
                )
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=resp.json()['detail']
                    )
                else:
                    course_responses.append(resp.json())
        return course_responses

# DONE 
@transaction_router.get("/")
async def get_transaction_list(user: User = Depends(authorize)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
                url = SERVICE_URL + f"/transaction/{user.email}"
            )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=resp.json()['message']
            )
        else:
            return resp.json()

# DONE
@transaction_router.get("/status/{id}")
async def get_transaction_list(id: str, user: User = Depends(authorize)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
                url = SERVICE_URL + f"/transaction/status/{id}"
            )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=resp.json()['message']
            )
        else:
            transaction = resp.json()["transaction_status"]
            if transaction["email"] != user.email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="You can not view this transaction"
                )
            course_ids = transaction["course_ids"]
            course_responses = []
            for course_id in course_ids:
                resp = await client.get(
                    url = COURSE_SERVICE_URL + f"/course/detail/{course_id}"
                )
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=resp.status_code,
                        detail=resp.json()['detail']
                    )
                else:
                    course_responses.append(resp.json())
            transaction["course_list"] = course_responses

            return transaction



# DONE
@transaction_router.post("/cart/add")
async def create(request: Request, user: User = Depends(authorize)):
    body = await request.body()
    try:
        body_dict: dict = json.loads(body)
        body_dict["email"] = user.email
        body_dict["course_id"] = str(body_dict["course_id"])
        request._body = json.dumps(body_dict).encode()

        mutable_headers = MutableHeaders(request._headers)
        mutable_headers["content-length"] = str(len(request._body))
    
        request._headers = mutable_headers
        request.scope.update(headers=mutable_headers.raw)
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not a valid JSON"
        )

    return await rerouter(request=request)

# DONE
@transaction_router.post("/confirm")
async def create(request: Request, user: User = Depends(authorize)):
    body = await request.body()
    try:
        body_dict: dict = json.loads(body)
        body_dict["customer_details"] = {
            "email": user.email,
            "first_name": user.username
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not a valid JSON"
        )


    transaction_type = body_dict.get("type")
    async with httpx.AsyncClient() as client:
    
        if transaction_type == "CART": # else would be SINGLE
            print("CART")
            resp = await client.get(
                url = SERVICE_URL + f"/transaction/cart/{user.email}"
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=resp.json()['message']
                )
            else:
                courses = resp.json()["courses_in_cart"]

                course_responses = []
                total_price = 0
                for course in courses:
                    course_id = course["course_id"]

                    resp = await client.get(
                        url = COURSE_SERVICE_URL + f"/course/detail/{course_id}"
                    )
                    if resp.status_code != 200:
                        raise HTTPException(
                            status_code=resp.status_code,
                            detail=resp.json()['detail']
                        )
                    else:
                        course_responses.append(resp.json())
                        total_price += resp.json()["price"]
                body_dict["item_details"] = [
                    {
                        "id": str(course["id"]),
                        "quantity": 1,
                        "price": course["price"],
                        "name": course["title"],
                    } for course in course_responses
                ]

                body_dict["transaction_details"] = {
                    "gross_amount": total_price
                }
                print(body_dict)
        else:
            print("SINGLE")
            course_id = body_dict.get("id")
            resp = await client.get(
                url = COURSE_SERVICE_URL + f"/course/detail/{course_id}"
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=resp.json()['detail']
                )
            else:
                course = resp.json()
                body_dict["item_details"] = [
                    {
                        "id": str(course_id),
                        "quantity": 1,
                        "price": course["price"],
                        "name": course["title"],
                    }
                ]

                body_dict["transaction_details"] = {
                    "gross_amount": course["price"]
                }

            

            body_dict.pop("type")
            body_dict.pop("id") 

        request._body = json.dumps(body_dict).encode()

        mutable_headers = MutableHeaders(request._headers)
        mutable_headers["content-length"] = str(len(request._body))

        request._headers = mutable_headers
        request.scope.update(headers=mutable_headers.raw)


        # return await rerouter(request=request)
        # print(path)
        url = SERVICE_URL + request.url.path
        headers = request.headers.raw
        method = request.method
        body = json.dumps(body_dict).encode()

        
        resp = await client.request(
            method = method,
            url = url,
            headers = headers,
            content = body
        )
        print(resp.content)
        print(resp.status_code)
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp.headers,
        )

# DONE
@transaction_router.delete("/cart/remove")
async def create(request: Request, user: User = Depends(authorize)):
    body = await request.body()
    try:
        body_dict: dict = json.loads(body)
        body_dict["email"] = user.email
        body_dict["course_id"] = str(body_dict["course_id"])
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

# DONE
@transaction_router.delete("/cart/remove_all")
async def create(request: Request, user: User = Depends(authorize)):

    body_dict = {
        "email": user.email
    }
    request._body = json.dumps(body_dict).encode()

    mutable_headers = MutableHeaders(request._headers)
    mutable_headers["content-length"] = str(len(request._body))

    request._headers = mutable_headers
    request.scope.update(headers=mutable_headers.raw)

    return await rerouter(request=request)

