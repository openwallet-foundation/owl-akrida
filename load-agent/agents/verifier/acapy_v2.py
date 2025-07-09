import time
from json.decoder import JSONDecodeError

import requests
from models import AnonCredsPresReq, IndyPresReq, ProofRequest
from models import RequestPresentationV2 as RequestPresentation
from settings import Settings

from .base import BaseVerifier


class AcapyVerifier(BaseVerifier):
    def __init__(self):
        super().__init__()
        self.cred_attributes = Settings.CRED_ATTR
        
    def get_presentation_request(self):
        proof_request = ProofRequest(
            name="PerfScore",
            requested_attributes={
                item["name"]: {"name": item["name"]} for item in self.cred_attributes
            },
            requested_predicates={},
            version="1.0",
        ).model_dump()

        if Settings.IS_ANONCREDS == "True":
            return AnonCredsPresReq(anoncreds=proof_request)
        else:
            return IndyPresReq(indy=proof_request)

    def create_connectionless_request(self):
        r = requests.post(
            f"{self.agent_url}/present-proof-2.0/send-request",
            headers=self.headers,
            json=RequestPresentation(
                presentation_request=self.get_presentation_request(),
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
                presentation_request=self.get_presentation_request(),
            ).model_dump(),
        )
        if r.status_code != 200:
            raise Exception("Request was not successful: ", r.content)

        try:
            return r.json()["pres_ex_id"]
        except JSONDecodeError:
            raise Exception(
                "Encountered JSONDecodeError while parsing the request: ", r.text
            )

    def verify_verification(self, pres_ex_id):
        # Want to do a for loop
        try:
            for _ in range(self.verifiedTimeoutSeconds):
                r = requests.get(
                    f"{self.agent_url}/present-proof-2.0/records/{pres_ex_id}",
                    headers=self.headers,
                )
                presentation_json = r.json()
                if (
                    presentation_json["state"] != "request_sent"
                    and presentation_json["state"] != "presentation_received"
                ):
                    "request_sent" and presentation_json["state"] != "presentation_received"
                    break
                time.sleep(1)

            r_verify = requests.post(
                f"{self.agent_url}/present-proof-2.0/records/{pres_ex_id}/verify-presentation",
                headers=self.headers,
            )

            if r_verify.json()["verified"] != "true":
                raise AssertionError(
                    f"Presentation was not successfully verified. Presentation in state {presentation_json['state']}"
                )

            return True

        except JSONDecodeError as e:
            raise Exception(
                "Encountered JSONDecodeError while getting the presentation record: ", e
            )
