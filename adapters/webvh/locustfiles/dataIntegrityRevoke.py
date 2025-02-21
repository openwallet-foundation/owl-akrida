import time
import logging
from locust import FastHttpUser, task, between, tag
from controllers import IssuerController
from settings import Settings


class AgentLocustClient(FastHttpUser):
    wait_time = between(1, 5)
    host = Settings.ISSUER_API

    @tag("eddsa-jcs-2022")
    @task(1)
    def eddsa_jcs_2022(self):
        logging.info("eddsa-jcs-2022")
        with self.client.post(
            "/vc/di/add-proof",
            catch_response=True,
            json={
                "document": self.credential,
                "options": {
                    "type": "DataIntegrityProof",
                    "cryptosuite": "eddsa-jcs-2022",
                    "proofPurpose": "assertionMethod",
                    "verificationMethod": self.verification_method,
                },
            },
        ) as response:
            if response.status_code != 201:
                response.failure("Got wrong response")
            response.json().get("securedDocument")
            response.success()

    def on_start(self):
        self.issuer = IssuerController()
        self.issuer_id = self.issuer.create_webvh()
        self.verification_method = f"{self.issuer_id}#key-01"
        # self.issuer.add_key(self.verification_method)
        self.credential = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential"],
            "issuer": self.issuer_id,
            "credentialSubject": {
                "name": "Jane Doe",
                "description": "A credential about Jane Doe.",
            },
        }
