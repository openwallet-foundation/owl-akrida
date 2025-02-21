from pydantic import BaseModel, Field
from typing import Union, List, Dict, Any


class BaseModel(BaseModel):
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

class Attribute(BaseModel):
    name: str = Field()
    value: str = Field()

class CredentialPreview(BaseModel):
    type: str = Field('issue-credential/2.0/credential-preview', alias='@type')
    attributes: List[Attribute] = Field()

class AnonCredsFilter(BaseModel):
    issuer_id: str = Field()
    cred_def_id: str = Field()

class Filter(BaseModel):
    anoncreds: AnonCredsFilter = Field()

class IssueCredential(BaseModel):
    auto_remove: bool = Field(False)
    connection_id: str = Field()
    credential_preview: CredentialPreview = Field()
    filter: Filter = Field()

class NonRevocationInterval(BaseModel):
    from_: int = Field(alias='from')
    to_: int = Field(alias='to')

class Restriction(BaseModel):
    issuer_id: str = Field(None)
    schema_id: str = Field(None)
    cred_def_id: str = Field(None)

class RequestedAttributes(BaseModel):
    name: str = Field(None)
    names: List[str] = Field(None)
    non_revoked: NonRevocationInterval = Field(None)
    restrictions: List[Restriction] = Field(None)

class RequestedPredicates(BaseModel):
    name: str = Field(None)
    non_revoked: NonRevocationInterval = Field(None)
    restrictions: List[Restriction] = Field(None)
    p_type: str = Field()
    p_value: int = Field()

class AnonCredsRequest(BaseModel):
    name: str = Field('Proof Request')
    nonce: str = Field()
    version: str = Field('1.0')
    non_revoked: Union[Dict[str, str], NonRevocationInterval] = Field(None)
    requested_attributes: Dict[str, RequestedAttributes] = Field(None)
    requested_predicates: Dict[str, RequestedPredicates] = Field(None)

class PresentationRequest(BaseModel):
    anoncreds: AnonCredsRequest = Field()

class RequestPresentation(BaseModel):
    auto_remove: bool = Field(False)
    connection_id: str = Field()
    presentation_request: PresentationRequest = Field()