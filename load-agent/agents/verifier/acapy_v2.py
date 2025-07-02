import time
from json.decoder import JSONDecodeError

import requests
from models import AnonCredsPresReq, ProofRequest
from models import RequestPresentationV2 as RequestPresentation
from settings import Settings

from .base import BaseVerifier


class AcapyVerifier(BaseVerifier):
    def __init__(self):
        self.filter = Settings.FILTER_TYPE
        self.cred_attributes = Settings.CRED_ATTR

    def create_connectionless_request(self):
        r = requests.post(
            f"{self.agent_url}/present-proof-2.0/send-request",
            headers=self.headers,
            json=RequestPresentation(
                proof_request=AnonCredsPresReq(
                    anoncreds=ProofRequest(
                        name="PerfScore",
                        requested_attributes={
                            item["name"]: {"name": item["name"]}
                            for item in self.cred_attributes
                        },
                        requested_predicates={},
                        version="1.0",
                    )
                ),
            ).model_dump(),
        )
        if r.status_code != 200:
            raise Exception("Request was not successful: ", r.content)
        try:
            return r.json()
        except JSONDecodeError:
            raise Exception(
                "Encountered JSONDecodeError while parsing the request: ", r.text
            )

    def request_verification(self, connection_id):
        r = requests.post(
            f"{self.agent_url}/present-proof-2.0/send-request",
            headers=self.headers,
            json=RequestPresentation(
                connection_id=connection_id,
                proof_request=AnonCredsPresReq(
                    anoncreds=ProofRequest(
                        name="PerfScore",
                        requested_attributes={
                            item["name"]: {"name": item["name"]}
                            for item in self.cred_attributes
                        },
                        requested_predicates={},
                        version="1.0",
                    )
                ),
            ).model_dump(),
        )
        if r.status_code != 200:
            raise Exception("Request was not successful: ", r.content)

        try:
            return r.json()["presentation_exchange_id"]
        except JSONDecodeError:
            raise Exception(
                "Encountered JSONDecodeError while parsing the request: ", r.text
            )

    def verify_verification(self, pres_ex_id):
        # Want to do a for loop
        try:
            for iteration in range(self.verifiedTimeoutSeconds):
                r = requests.get(
                    f"{self.agent_url}/present-proof-2.0/records/{pres_ex_id}",
                    headers=self.headers,
                )
                if (
                    r.json()["state"] != "request_sent"
                    and r.json()["state"] != "presentation_received"
                ):
                    "request_sent" and r.json()["state"] != "presentation_received"
                    break
                time.sleep(1)

            if r.json()["verified"] != "true":
                raise AssertionError(
                    f"Presentation was not successfully verified. Presentation in state {r.json()['state']}"
                )

            return True

        except JSONDecodeError as e:
            raise Exception(
                "Encountered JSONDecodeError while getting the presentation record: ", e
            )
