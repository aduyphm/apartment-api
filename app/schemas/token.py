from pydantic import BaseModel


class TokenInspectOutput(BaseModel):
    valid: bool
    status_code: int
    detail: str
