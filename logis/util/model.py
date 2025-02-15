from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
