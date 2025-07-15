from abc import abstractmethod

from settings import Settings

from ..base import BaseAgent


class BaseVerifier(BaseAgent):
    def __init__(self):
        super().__init__()
        self.label = "Test Verifier"
        self.agent_url = Settings.VERIFIER_URL
        self.headers = Settings.VERIFIER_HEADERS | {"Content-Type": "application/json"}
        self.verifiedTimeoutSeconds = Settings.VERIFIED_TIMEOUT_SECONDS

    @abstractmethod
    def request_verification(self, connection_id):
        # return r['presentation_exchange_id']
        raise NotImplementedError

    @abstractmethod
    def verify_verification(self, presentation_exchange_id):
        # return True on success
        # Throw Exception on failure
        raise NotImplementedError
