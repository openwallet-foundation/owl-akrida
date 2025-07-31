import os

from constants import standard_wait
from locust import TaskSet, task
from locustCustom import CustomLocust

WITH_MEDIATION = os.getenv("WITH_MEDIATION")


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
