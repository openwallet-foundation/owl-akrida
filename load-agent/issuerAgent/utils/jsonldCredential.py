def get_jsonld_credential_payload(connection_id, issuer_did):
  return {
    "connection_id": connection_id,
    "filter": {
            "ld_proof": {
            "credential": {
                    "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/examples/v1"
                    ],
                    "type": [
                    "VerifiableCredential",
                    "UniversityDegreeCredential"
                    ],
                    "issuer": {
                    "id": issuer_did
                    },
                    "issuanceDate": "2019-10-12T07:20:50.52Z",
                    "credentialSubject": {
                    "id": "did:key:z6Mkty8b4M1arFSmxYVtM3nsoQvyFurHPhRxRms7vZ6cVZbN",
                    "degree": {
                            "type": "BachelorDegree",
                            "name": "Bachelor of Science and Arts"
                    }
                    }
            },
            "options": {
                    "proofType": "Ed25519Signature2018",
                    "proofPurpose": "assertionMethod"
            }
            }
    }
  }