import uuid


def get_jsonld_verification_payload(connection_id):
  return {
        "auto_remove": True,
        "connection_id": connection_id,
        "auto_verify": True,
        "trace": True,
        "comment": "Degree certificate verification using Aries Akrida",
        "presentation_request": {
            "dif": {
                "presentation_definition": {
                    "id": str(uuid.uuid4()),
                    "format": {
                        "ldp_vp": {
                            "proof_type": [
                                "Ed25519Signature2018"
                            ]
                        }
                    },
                    "input_descriptors": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "registration card",
                            "schema": [
                                {
                                    "uri": "https://www.w3.org/2018/credentials/examples/v1"
                                }
                            ],
                            "constraints": {
                                "fields": [
                                    {
                                        "path": [
                                            "$.credentialSubject.degree.type"
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
