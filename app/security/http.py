from typing import Optional

from pydantic import BaseModel
from starlette.requests import Request
from fastapi.security import HTTPBasic


class HTTPClientCredentials(BaseModel):
    client_id: str
    client_secret: str


class HTTPBasicClientCredentials(HTTPBasic):
    async def __call__(self, request: Request) -> Optional[HTTPClientCredentials]:
        basic = await super().__call__(request)
        if not basic:
            return None
        return HTTPClientCredentials(client_id=basic.username, client_secret=basic.password)
