import os
import httpx
import dotenv

from fastapi import status, Header
from fastapi import HTTPException

from .schemas import User

async def authorize(authorization: str | None = Header(default=None)) -> User:
    # dotenv.load_dotenv()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing"
        )

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                # os.environ["AUTH_BE"] + "/users/me",
                "http://localhost:8002" + "/users/me",
                headers={
                    "Authorization": authorization
                }
            )

            if resp.status_code >= 500:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            elif resp.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization error: invalid token"
                )
            else:
                return User.model_validate(resp.json())
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

