from fastapi import Request
from fastapi.responses import Response
import httpx

async def generate_rerouter(microservice_url: str, request: Request):
    path = request.url.path
    queries = request.query_params._dict
    headers = request.headers.raw
    cookies = request.cookies
    method = request.method
    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method = method,
            url = microservice_url + path,
            params=queries,
            headers = headers,
            cookies = cookies,
            content = body
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp.headers,
        )