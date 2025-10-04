from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str
    code: int
