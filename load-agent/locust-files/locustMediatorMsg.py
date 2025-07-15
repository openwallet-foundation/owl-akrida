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
        while not self.client.is_running():
            self.client.startup(withMediation=bool(WITH_MEDIATION))

        self.get_invite()

        self.accept_invite()

    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        if connection is not None:
            self.connection = connection

    def on_stop(self):
        self.client.shutdown()

    @task
    def msg_client(self):
        # I think this should be @id....
        self.client.msg_client(self.invite['connection_id'])

class MediatorMsg(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
