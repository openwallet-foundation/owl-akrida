from pydantic import BaseModel, Field
from typing import Dict, Any


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)


class ProofRequest(BaseModel):
    name: str = Field()
    requested_attributes: dict = Field()
    requested_predicates: dict = Field()
    version: str = Field()


class RequestPresentationV1(BaseModel):
    auto_remove: bool = Field(False)
    auto_verify: bool = Field(True)
    connection_id: str = Field(None)
    comment: str = Field()
    proof_request: ProofRequest = Field()
    trace: bool = Field(True)