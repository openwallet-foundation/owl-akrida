from .base import BaseIssuer
import requests
import time
from models import IssueCredentialV1, CredentialProposalV1, AnonCredsRevocation
from settings import Settings


class AcapyIssuer(BaseIssuer):
    def __init__(self):
        self.label = "Test Issuer"
        self.agent_url = Settings.ISSUER_URL
        self.headers = Settings.ISSUER_HEADERS | {"Content-Type": "application/json"}
        self.schema_id = Settings.SCHEMA_ID
        self.cred_def_id = Settings.CRED_DEF_ID
        self.cred_attributes = Settings.CRED_ATTR

    def get_invite(self):
        r = requests.post(
                f"{self.agent_url}/out-of-band/create-invitation?auto_accept=true",
                json={"handshake_protocols": Settings.HANDSHAKE_PROTOCOLS},
                headers=self.headers,
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
        except Exception:
            return False

        return True

    def issue_credential(self, connection_id):
        schema_parts = self.schema_id.split(":")

        payload = IssueCredentialV1(
            connection_id=connection_id,
            comment="Performance Issuance",
            cred_def_id=self.cred_def_id,
            issuer_did=self.cred_def_id.split(":")[0],
            schema_id=self.schema_id,
            schema_issuer_did=schema_parts[0],
            schema_name=schema_parts[2],
            schema_version=schema_parts[3],
            credential_proposal=CredentialProposalV1(attributes=self.cred_attributes),
        ).model_dump()
        
        r = requests.post(
            f"{self.agent_url}/issue-credential/send",
            json=payload,
            headers=self.headers,
        )
        if r.status_code != 200:
            raise Exception(r.content)

        cred_offer = r.json()

        return {
            "connection_id": cred_offer["connection_id"],
            "cred_ex_id": cred_offer["credential_exchange_id"],
        }

    def revoke_credential(self, connection_id, credential_exchange_id):
        time.sleep(1)
        payload = AnonCredsRevocation(
            comment="Load Test",
            connection_id=connection_id,
            cred_ex_id=credential_exchange_id,
            notify_version="v1_0",
        ).model_dump()
        r = requests.post(
            f"{self.agent_url}/revocation/revoke",
            json=payload,
            headers=self.headers,
        )
        if r.status_code != 200:
            raise Exception(r.content)

    def send_message(self, connection_id, msg):
        requests.post(
            f"{self.agent_url}/connections/{connection_id}/send-message",
            json={"content": msg},
            headers=self.headers,
        )
