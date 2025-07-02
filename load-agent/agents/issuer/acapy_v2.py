import time

import requests
from models import (
    AnonCredsFilter,
    AnonCredsRevocation,
    CredentialPreview,
    Filter,
)
from models import (
    IssueCredentialV2 as IssueCredential,
)
from settings import Settings

from .base import BaseIssuer


class AcapyIssuer(BaseIssuer):
    def __init__(self):
        super().__init__()
        self.filter = Settings.FILTER_TYPE

    def issue_credential(self, connection_id):
        r = requests.post(
            f"{self.agent_url}/issue-credential-2.0/send",
            headers=self.headers,
            json=IssueCredential(
                connection_id=connection_id,
                credential_preview=CredentialPreview(attributes=self.cred_attributes),
                filter=AnonCredsFilter(anoncreds=Filter(cred_def_id=self.cred_def_id)),
            ).model_dump(),
        )
        if r.status_code != 200:
            raise Exception(r.content)

        cred_ex = r.json()

        return {
            "connection_id": cred_ex["connection_id"],
            "cred_ex_id": cred_ex["credential_exchange_id"],
        }

    def revoke_credential(self, connection_id, cred_ex_id):
        time.sleep(1)
        r = requests.post(
            f"{self.agent_url}/revocation/revoke",
            headers=self.headers,
            json=AnonCredsRevocation(
                connection_id=connection_id,
                cred_ex_id=cred_ex_id,
                notify_version="v1_0",
            ).model_dump(),
        )
        if r.status_code != 200:
            raise Exception(r.content)
