from constants import standard_wait
from locust import task
from locustConnection import ConnectionUserBehaviour
from locustCustom import CustomLocust


class UserBehaviour(ConnectionUserBehaviour):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @task
    def msg_client(self):
        # I think this should be @id....
        for invite in self.invites:
            self.client.msg_client(invite["connection_id"])


class MediatorMsg(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
