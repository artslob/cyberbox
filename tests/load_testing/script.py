import random
import string
from time import sleep

from locust import between, constant_pacing, task
from locust.contrib.fasthttp import FastHttpUser


class PingUser(FastHttpUser):
    wait_time = constant_pacing(0.5)

    @task
    def ping(self):
        self.client.get("/common/ping/")


class User(FastHttpUser):
    wait_time = constant_pacing(0.5)
    wait_before_login = between(0.3, 0.8)

    def __init__(self, environment):
        super().__init__(environment)
        self.headers = {}

    def on_start(self):
        username = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        password = f"{username}-pass"
        self.client.post(
            "/auth/register", data=dict(username=username, password1=password, password2=password)
        )
        sleep(self.wait_before_login())
        response = self.client.post("/auth/login", data=dict(username=username, password=password))
        access_token = response.json()["access_token"]
        self.headers.update({"Authorization": f"Bearer {access_token}"})

    @task
    def file_list(self):
        self.client.get("/file/", headers=self.headers)

    @task
    def link_list(self):
        self.client.get("/link/", headers=self.headers)

    @task
    def profile(self):
        self.client.get("/auth/profile", headers=self.headers)


class NotAuthenticatedUser(FastHttpUser):
    wait_time = constant_pacing(0.5)

    @task
    def profile(self):
        with self.client.get("/auth/profile", catch_response=True) as response:
            if response.status_code == 401:
                response.success()

    @task
    def file_list(self):
        with self.client.get("/file/", catch_response=True) as response:
            if response.status_code == 401:
                response.success()

    @task
    def link_list(self):
        with self.client.get("/link/", catch_response=True) as response:
            if response.status_code == 401:
                response.success()
