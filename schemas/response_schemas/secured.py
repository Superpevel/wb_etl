from pydantic import BaseModel

class SecuredResponse(BaseModel):
    id: int
