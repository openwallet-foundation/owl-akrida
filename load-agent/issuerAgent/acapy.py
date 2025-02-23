from .base import BaseIssuer
import json
import os
import requests
import time
from .models import IssueCredentialV1, CredentialProposalV1, AnonCredsRevocation

class AcapyIssuer(BaseIssuer):
        def __init__(self):
                self.agent_url = os.getenv("ISSUER_URL")
                self.headers = json.loads(os.getenv("ISSUER_HEADERS"))
                self.headers['Content-Type'] = "application/json"
                self.cred_def_id = os.getenv("CRED_DEF")
                self.schema_id = os.getenv("SCHEMA")
                self.cred_attributes = json.loads(os.getenv("CRED_ATTR"))
        
<<<<<<< HEAD
        def get_invite(self):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"

                # Out of Band Connection 
                r = requests.post(
                        os.getenv("ISSUER_URL") + "/out-of-band/create-invitation?auto_accept=true", 
                        json={
                        "metadata": {}, 
                        "handshake_protocols": ["did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0"]
                        },
                        headers=headers
                )

                r = r.json()

                invitation_msg_id = r['invi_msg_id']
                g = requests.get(
                        os.getenv("ISSUER_URL") + "/connections",
                        params={"invitation_msg_id": invitation_msg_id},
                        headers=headers,
                )
                # Returns only one
                connection_id = g.json()['results'][0]['connection_id']
                r['connection_id'] = connection_id 
=======
        def get_invite(self, out_of_band=False):
                if out_of_band:
                        # Out of Band Connection 
                        # (ACA-Py v10.4 - only works with connections protocol, not DIDExchange) 
                        r = requests.post(
                                f"{self.agent_url}/out-of-band/create-invitation?auto_accept=true", 
                                json={
                                "metadata": {}, 
                                "handshake_protocols": ["https://didcomm.org/connections/1.0"]
                                },
                                headers=self.headers
                        )
                else:
                        # Regular Connection
                        r = requests.post(
                                f"{self.agent_url}/connections/create-invitation?auto_accept=true",
                                json={"metadata": {}, "my_label": "Test"},
                                headers=self.headers,
                        )

                        # Ensure the request worked
                        try:
                                r.json()["invitation_url"]
                        except Exception:
                                raise Exception("Failed to get invitation url. Request: ", r.text)
                        if r.status_code != 200:
                                raise Exception(r.content)

                r = r.json()

                # If OOB, need to grab connection_id
                if out_of_band:
                        invitation_msg_id = r['invi_msg_id']
                        g = requests.get(
                                f"{self.agent_url}/connections",
                                params={"invitation_msg_id": invitation_msg_id},
                                headers=self.headers,
                        )
                        # Returns only one
                        connection_id = g.json()['results'][0]['connection_id']
                        r['connection_id'] = connection_id 
>>>>>>> 50f1134 (add parametrized settings for load agent, models for protocol exchanges and locust files subdirectory)
                
                return {
                        'invitation_url': r['invitation_url'], 
                        'connection_id': r['connection_id']
                }

        def is_up(self):
                try:
                        r = requests.get(
                                f"{self.agent_url}/status",
                                json={"metadata": {}, "my_label": "Test"},
                                headers=self.headers,
                        )
                        if r.status_code != 200:
                                raise Exception(r.content)

                        r = r.json()
                except Exception:
                        return False

                return True

        def issue_credential(self, connection_id):
                issuer_did = self.cred_def_id.split(":")[0]
                schema_parts = self.schema_id.split(":")
                
                r = requests.post(
                        f"{self.agent_url}/issue-credential/send",
                        json=IssueCredentialV1(
                                connection_id=connection_id,
                                comment='Performance Issuance',
                                cred_def_id=self.cred_def_id,
                                issuer_did=issuer_did,
                                schema_id=self.schema_id,
                                schema_issuer_did=schema_parts[0],
                                schema_name=schema_parts[2],
                                schema_version=schema_parts[3],
                                credential_proposal=CredentialProposalV1(
                                        attributes=self.cred_attributes
                                ).model_dump()
                        ).model_dump(),
                        headers=self.headers,
                )
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {
                        "connection_id": r["connection_id"], 
                        "cred_ex_id": r["credential_exchange_id"]
                }

        def revoke_credential(self, connection_id, credential_exchange_id):
                time.sleep(1)
                r = requests.post(
                        f"{self.agent_url}/revocation/revoke",
                        json=AnonCredsRevocation(
                                comment='Load Test',
                                connection_id=connection_id,
                                cred_ex_id=credential_exchange_id,
                                notify_version='v1_0'
                        ).model_dump(),
                        headers=self.headers,
                )
                if r.status_code != 200:
                        raise Exception(r.content)

        def send_message(self, connection_id, msg):
                r = requests.post(
                        f"{self.agent_url}/connections/{connection_id}/send-message",
                        json={"content": msg},
                        headers=self.headers,
                )
                r.json()
