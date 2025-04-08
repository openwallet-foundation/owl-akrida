from .base import BaseVerifier
import json
import os
import requests
import time
from models import RequestPresentationV1, ProofRequest
from settings import Settings

from json.decoder import JSONDecodeError

class AcapyVerifier(BaseVerifier):
        def __init__(self):
                self.label = "Test Verifier"
                self.agent_url = Settings.VERIFIER_URL
                self.headers = Settings.VERIFIER_HEADERS | {
                        'Content-Type': 'application/json'
                }
        
                self.cred_attributes = Settings.CRED_ATTR
                self.verifiedTimeoutSeconds = Settings.VERIFIED_TIMEOUT_SECONDS

        def get_invite(self, out_of_band=False):
                if out_of_band:
                        # Out of Band Connection 
                        # (ACA-Py v10.4 - only works with connections protocol, not DIDExchange) 
                        r = requests.post(
                                f"{self.agent_url}/out-of-band/create-invitation?auto_accept=true", 
                                json={
                                "handshake_protocols": ["https://didcomm.org/connections/1.0"]
                                },
                                headers=self.headers
                        )
                else:
                        # Regular Connection
                        r = requests.post(
                                f"{self.agent_url}/connections/create-invitation?auto_accept=true",
                                json={"my_label": self.label},
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
                
                return {
                        'invitation_url': r['invitation_url'], 
                        'connection_id': r['connection_id']
                }

        def is_up(self):
                try:
                        r = requests.get(
                                f"{self.agent_url}/status",
                                headers=self.headers,
                        )
                        if r.status_code != 200:
                                raise Exception(r.content)

                        r = r.json()
                except:
                        return False

                return True

        def create_connectionless_request(self):
                # Calling verification agent

                # API call to /present-proof/create-request
                r = requests.post(
                        f"{self.agent_url}/present-proof/create-request",
                        json=RequestPresentationV1(
                                comment='Performance Verification',
                                proof_request=ProofRequest().model_dump(
                                        name='PerfScore',
                                        requested_attributes={
                                                item["name"]: {"name": item["name"]}
                                                for item in self.cred_attributes
                                        },
                                        requested_predicates={},
                                        version='1.0'
                                )
                        ).model_dump(),
                        headers=self.headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r.text
                        )
                
                return r.json()
        
        def request_verification(self, connection_id):
                # From verification side
                # Might need to change nonce
                # TO DO: Generalize schema parts
                r = requests.post(
                        f"{self.agent_url}/present-proof/send-request",
                        json=RequestPresentationV1(
                                comment='Performance Verification',
                                connection_id=connection_id,
                                proof_request=ProofRequest().model_dump(
                                        name='PerfScore',
                                        requested_attributes={
                                                item["name"]: {"name": item["name"]}
                                                for item in self.cred_attributes
                                        },
                                        requested_predicates={},
                                        version='1.0'
                                )
                        ).model_dump(),
                        headers=self.headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r.text
                        )
                
                r = r.json()

                return r['presentation_exchange_id']

        def verify_verification(self, presentation_exchange_id):
                # Want to do a for loop
                iteration = 0
                try:
                        while iteration < self.verifiedTimeoutSeconds:
                                g = requests.get(
                                        f"{self.agent_url}/present-proof/records/{presentation_exchange_id}",
                                        headers=self.headers,
                                )
                                if (
                                        g.json()["state"] != "request_sent"
                                        and g.json()["state"] != "presentation_received"
                                ):
                                        "request_sent" and g.json()["state"] != "presentation_received"
                                        break
                                iteration += 1
                                time.sleep(1)

                        if g.json()["verified"] != "true":
                                raise AssertionError(
                                        f"Presentation was not successfully verified. Presentation in state {g.json()['state']}"
                                )

                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while getting the presentation record: ", g
                        )

                return True

        def send_message(self, connection_id, msg):
                r = requests.post(
                        f"{self.agent_url}/connections/{connection_id}/send-message",
                        json={"content": msg},
                        headers=self.headers,
                )
                r.json()
