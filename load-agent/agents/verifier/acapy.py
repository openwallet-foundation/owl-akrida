import time
from json.decoder import JSONDecodeError

import requests
from models import ProofRequest, RequestPresentationV1
from settings import Settings

from .base import BaseVerifier


class AcapyVerifier(BaseVerifier):
    def __init__(self):
        super().__init__()
        self.proof_request = ProofRequest(
            name="PerfScore",
            requested_attributes={
                item["name"]: {"name": item["name"]} for item in Settings.CRED_ATTR
            },
            requested_predicates={},
            version="1.0",
        )

    def create_connectionless_request(self):
        # Calling verification agent

        # API call to /present-proof/create-request
        r = requests.post(
            f"{self.agent_url}/present-proof/create-request",
            json=RequestPresentationV1(
                comment="Performance Verification", proof_request=self.proof_request
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
                comment="Performance Verification",
                connection_id=connection_id,
                proof_request=self.proof_request,
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
