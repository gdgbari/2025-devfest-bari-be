from pydantic import BaseModel

class OkResponse(BaseModel):
    detail: str = "OK"