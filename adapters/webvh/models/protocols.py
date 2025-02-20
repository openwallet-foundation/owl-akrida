from pydantic import BaseModel
from typing import Field, List, Dict, Any
from random import randint


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
    _from: int = Field(alias='from')
    _to: int = Field(alias='to')

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

class AnonCredsProposal(BaseModel):
    name: str = Field('Proof Request')
    nonce: str = Field(str(randint(16)))
    version: str = Field('1.0')
    non_revoked: NonRevocationInterval = Field(None)
    requested_attributes: Dict[str, RequestedAttributes] = Field(None)
    requested_predicates: Dict[str, RequestedPredicates] = Field(None)

class PresentationProposal(BaseModel):
    anoncreds: AnonCredsProposal = Field()

class RequestPresentation(BaseModel):
    auto_remove: bool = Field(False)
    connection_id: str = Field()
    presentation_proposal: PresentationProposal = Field()