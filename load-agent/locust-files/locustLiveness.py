from constants import standard_wait
from locust import SequentialTaskSet, task
from locustCustom import CustomLocust


class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        pass

    def on_stop(self):
        pass

    @task
    def get_liveness(self):
        self.client.issuer_getliveness()


class Liveness(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = standard_wait
