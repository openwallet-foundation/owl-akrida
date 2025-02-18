import time
from locust import HttpUser, task, between
from .controller import AgentController
from client.settings import Settings

class AgentLocustClient(HttpUser):
    wait_time = between(1, 5)
    host = Settings.ISSUER_API
    
    @task
    def create_user(self):
        pass
    
    @task
    def issue_credential(self):
        issuer_id = ''
        cred_def_id = ''
        connection_id = ''
        attributes = {}
        headers = {}
        body = {
            'auto_remove': True,
            'connection_id': connection_id,
            'credential_preview': {
                '@type': 'issue-credential/2.0/credential-preview',
                'attributes': [{
                    "name": attribute,
                    "value": attributes[attribute]
                } for attribute in attributes]
            },
            'filter': {
                'anoncreds': {
                    'issuer_id': issuer_id,
                    'cred_def_id': cred_def_id
                }
            }
        }
        with self.client.post("/issue-credential-2.0/send", json=body, headers=headers) as response:
            pass
        
    def on_start(self):
        admin_endpoint = Settings.HOLDER_API
        webvh_server = Settings.WEBVH_SERVER
        self.agent = AgentController(admin_endpoint, webvh_server)
        self.agent.provision_client()