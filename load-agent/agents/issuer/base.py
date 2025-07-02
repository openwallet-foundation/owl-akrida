from abc import abstractmethod

from settings import Settings

from ..base import BaseAgent


class BaseIssuer(BaseAgent):
    def __init__(self):
        print("BaseIssuer initialized")
        super().__init__()
        self.label = "Test Issuer"
        self.agent_url = Settings.ISSUER_URL
        self.headers = Settings.ISSUER_HEADERS | {"Content-Type": "application/json"}
        self.schema_id = Settings.SCHEMA_ID
        self.cred_def_id = Settings.CRED_DEF_ID
        self.cred_attributes = Settings.CRED_ATTR

    @abstractmethod
    def issue_credential(self, connection_id):
        # return { "connection_id": , "cred_ex_id":  ] }
        raise NotImplementedError

    @abstractmethod
    def revoke_credential(self, connection_id, credential_exchange_id):
        raise NotImplementedError

