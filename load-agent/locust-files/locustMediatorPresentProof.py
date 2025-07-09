import os

from constants import standard_wait
from locust import SequentialTaskSet, User, task
from locustClient import CustomClient

WITH_MEDIATION = os.getenv("WITH_MEDIATION")

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))

    def on_stop(self):
        self.client.shutdown()

    @task
    def get_issuer_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    @task
    def accept_issuer_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        if connection is not None:
            self.connection = connection

    @task
    def receive_credential(self):
        self.client.ensure_is_running()
        self.client.receive_credential(self.invite['connection_id'])

    @task
    def get_verifier_invite(self):
        verifier_invite = self.client.issuer_getinvite()
        self.verifier_invite = verifier_invite

    @task
    def accept_verifier_invite(self):
        self.client.ensure_is_running()

        verifier_connection = self.client.accept_invite(self.verifier_invite['invitation_url'])
        if verifier_connection is not None:
            self.verifier_connection = verifier_connection

    @task
    def presentation_exchange(self):
        self.client.ensure_is_running()
        self.client.presentation_exchange(self.verifier_invite['connection_id'])


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait

