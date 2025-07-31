from locust import User
from locustClient import CustomClient


class CustomLocust(User):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = CustomClient(self.host)
