from pydantic import BaseModel


class Model(BaseModel):
    class Config:
        arbitrary_types_allowed = True
