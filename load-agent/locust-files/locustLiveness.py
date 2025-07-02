from constants import standard_wait
from locust import SequentialTaskSet, User, task
from locustClient import CustomClient


class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        pass

    def on_stop(self):
        pass

    @task
    def get_liveness(self):
        invite = self.client.issuer_getliveness()

class Liveness(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
