from locust import between
import os

standard_wait = between(float(os.getenv('LOCUST_MIN_WAIT', 0.1)), float(os.getenv('LOCUST_MAX_WAIT', 1)))