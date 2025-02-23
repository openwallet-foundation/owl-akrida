from locust import SequentialTaskSet, task, User, between
from locustClient import CustomClient
from constants import standard_wait

import os

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
    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    @task
    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        self.connection = connection

    @task
    def receive_credential(self):
        self.client.ensure_is_running()

        credential = self.client.receive_credential(self.invite['connection_id'])

class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
#    host = "example.com"
