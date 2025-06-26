from .base import BaseVerifier
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
        
                self.verifiedTimeoutSeconds = Settings.VERIFIED_TIMEOUT_SECONDS
                self.proof_request = ProofRequest(
                        name='PerfScore',
                        requested_attributes={
                                item["name"]: {"name": item["name"]}
                                for item in Settings.CRED_ATTR
                        },
                        requested_predicates={},
                        version='1.0'
                )

        def get_invite(self):
                r = requests.post(
                        f"{self.agent_url}/out-of-band/create-invitation?auto_accept=true", 
                        json={
                        "handshake_protocols": Settings.HANDSHAKE_PROTOCOLS
                        },
                        headers=self.headers
                )
                invitation = r.json()

                r = requests.get(
                        f"{self.agent_url}/connections",
                        params={"invitation_msg_id": invitation['invi_msg_id']},
                        headers=self.headers,
                )
                connection = r.json()['results'][0]
                
                return {
                        'invitation_url': invitation['invitation_url'], 
                        'connection_id': connection['connection_id']
                }

        def is_up(self):
                try:
                        r = requests.get(
                                f"{self.agent_url}/status",
                                headers=self.headers,
                        )
                        if r.status_code != 200:
                                raise Exception(r.content)

                        r.json()
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
                                proof_request=self.proof_request
                        ).model_dump(),
                        headers=self.headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                        presentation_request = r.json()
                except JSONDecodeError:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r.text
                        )
                
                return presentation_request
        
        def request_verification(self, connection_id):
                # From verification side
                # Might need to change nonce
                # TO DO: Generalize schema parts
                r = requests.post(
                        f"{self.agent_url}/present-proof/send-request",
                        json=RequestPresentationV1(
                                comment='Performance Verification',
                                connection_id=connection_id,
                                proof_request=self.proof_request
                        ).model_dump(),
                        headers=self.headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                        presentation_request = r.json()
                except JSONDecodeError:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r.text
                        )

                return presentation_request

        def verify_verification(self, presentation_exchange_id):
                # Want to do a for loop
                iteration = 0
                try:
                        while iteration < self.verifiedTimeoutSeconds:
                                r = requests.get(
                                        f"{self.agent_url}/present-proof/records/{presentation_exchange_id}",
                                        headers=self.headers,
                                )
                                presentation_record = r.json()
                                presentation_state = presentation_record["state"]
                                if (
                                        presentation_state != "request_sent"
                                        and presentation_state != "presentation_received"
                                ):
                                        "request_sent" and presentation_state != "presentation_received"
                                        break
                                iteration += 1
                                time.sleep(1)

                        if presentation_record["verified"] != "true":
                                raise AssertionError(
                                        f"Presentation was not successfully verified. Presentation in state {presentation_state}"
                                )

                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while getting the presentation record: ", e
                        )

                return True

        def send_message(self, connection_id, msg):
                r = requests.post(
                        f"{self.agent_url}/connections/{connection_id}/send-message",
                        json={"content": msg},
                        headers=self.headers,
                )
                r.json()
