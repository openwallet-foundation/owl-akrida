import os

from constants import standard_wait
from locust import SequentialTaskSet, User, task
from locustClient import CustomClient

WITH_MEDIATION = os.getenv("WITH_MEDIATION")

class CustomLocust(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = CustomClient(self.host)


class UserBehaviour(SequentialTaskSet):
    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        if connection is not None:
            self.connection = connection

    def receive_credential(self):
        self.client.ensure_is_running()
        self.client.receive_credential(self.invite["connection_id"])

    def get_verifier_invite(self):
        verifier_invite = self.client.verifier_getinvite()
        self.verifier_invite = verifier_invite

    def accept_verifier_invite(self):
        self.client.ensure_is_running()
        
        verifier_connection = self.client.accept_invite(self.verifier_invite['invitation_url'])
        if verifier_connection is not None:
            self.verifier_connection = verifier_connection

    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))
        self.get_invite()
        self.accept_invite()
        self.receive_credential()
        self.get_verifier_invite()
        self.accept_verifier_invite()

    def on_stop(self):
        self.client.shutdown()

    @task
    def presentation_exchange(self):
        presentation_not_complete = True
        restart = False
        while presentation_not_complete:
            if not self.client.is_running() or restart:
                self.client.shutdown()
                self.on_start()

            restart = False

            try:
                presentation = self.client.presentation_exchange(
                    self.verifier_invite["connection_id"]
                )
                presentation_not_complete = False
            except AssertionError as e:
                if "JSONDecodeError" in presentation["result"]:
                    restart = True
                    pass
                else:
                    raise AssertionError("Error is : ", e)


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
