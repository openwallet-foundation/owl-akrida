from locust import TaskSet, task, User
from locustClient import CustomClient
from constants import standard_wait

import os

WITH_MEDIATION = os.getenv("WITH_MEDIATION")

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(TaskSet):
    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))
        
    def on_stop(self):
        self.client.shutdown()

    @task
    def ping_mediator(self):
        self.client.ensure_is_running()

        self.client.ping_mediator()

class MediatorPing(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
#    host = "example.com"
