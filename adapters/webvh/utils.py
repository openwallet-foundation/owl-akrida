from models.protocols import (
    IssueCredential, 
    CredentialPreview, 
    Attribute, 
    Filter, 
    AnonCredsFilter
)
from models.protocols import (
    RequestPresentation, 
    PresentationProposal, 
    RequestedAttributes, 
    RequestedPredicates, 
    AnonCredsProposal,
    Restriction,
    NonRevocationInterval
)
from random import randint

def create_issue_credential_payload(issuer_id, cred_def_id, connection_id, attributes):
    return IssueCredential(
        connection_id=connection_id,
        credential_preview=CredentialPreview(
            attributes=[Attribute(
                name=attribute, value=attributes[attribute]
            ) for attribute in attributes]
        ),
        filter=Filter(
            anoncreds=AnonCredsFilter(
                issuer_id=issuer_id,
                cred_def_id=cred_def_id,
            ))
    ).model_dump()

def create_request_presentation_payload(cred_def_id, connection_id, attributes, predicate, timestamp):
    return RequestPresentation(
        connection_id=connection_id,
        presentation_proposal=PresentationProposal(
            anoncreds=AnonCredsProposal(
                nonce=str(randint(4, 4)),
                non_revoked={
                    'to': timestamp,
                    'from': timestamp
                },
                requested_attributes={
                    'requestedAttributes': RequestedAttributes(
                        names=attributes,
                        restrictions=[Restriction(
                            cred_def_id=cred_def_id
                        )]
                    )
                },
                requested_predicates={
                    'requestedPredicates': RequestedPredicates(
                        name=predicate[0],
                        p_type=predicate[1],
                        p_value=predicate[2]
                    )
                }
            )
        )
    ).model_dump()