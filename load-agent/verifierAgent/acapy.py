from .base import BaseVerifier
import json
import os
import requests

class AcapyVerifier(BaseVerifier):

        def get_invite(self):
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                headers["Content-Type"] = "application/json"
                # r = requests.post(
                #     os.getenv("ISSUER_URL") + "/out-of-band/create-invitation?auto_accept=true", 
                #     json={
                #         "metadata": {}, 
                #         "handshake_protocols": ["https://didcomm.org/didexchange/1.0"],
                #         "use_public_did": False
                #     },
                #     headers=headers
                # )
                #print("r is ", r, " and r.json is ", r.json())
                r = requests.post(
                        os.getenv("VERIFIER_URL") + "/connections/create-invitation?auto_accept=true",
                        json={"metadata": {}, "my_label": "Test"},
                        headers=headers,
                )
                try:
                        try_var = r.json()["invitation_url"]
                except Exception:
                        raise Exception("Failed to get invitation url. Request: ", r.json())
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {'invitation_url': r['invitation_url'], 'connection_id': r['connection_id']}

        def is_up(self):
                try:
                        headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                        headers["Content-Type"] = "application/json"
                        r = requests.get(
                        os.getenv("VERIFIER_URL") + "/status",
                        json={"metadata": {}, "my_label": "Test"},
                        headers=headers,
                        )
                        if r.status_code != 200:
                        raise Exception(r.content)

                        r = r.json()
                except:
                        return False

                return True

        def request_verification(self, ):
                # From verification side
                headers = json.loads(os.getenv("ISSUER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"

                verifier_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")

                # Might need to change nonce
                # TO DO: Generalize schema parts
                r = requests.post(
                os.getenv("VERIFIER_URL") + "/present-proof/send-request",
                json={
                        "auto_remove": False,
                        "auto_verify": True,
                        "comment": "Performance Verification",
                        "connection_id": connection_id,
                        "proof_request": {
                        "name": "PerfScore",
                        "requested_attributes": {
                                item["name"]: {"name": item["name"]}
                                for item in json.loads(os.getenv("CRED_ATTR"))
                        },
                        "requested_predicates": {},
                        "version": "1.0",
                        },
                        "trace": True,
                },
                headers=headers,
                )

                try:
                if r.status_code != 200:
                        raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError as e:
                raise Exception(
                        "Encountered JSONDecodeError while parsing the request: ", r
                )                