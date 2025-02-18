import time
from locust import HttpUser, task, between
from client.settings import Settings
import hashlib
import uuid

class AgentLocustClient(HttpUser):
    wait_time = between(1, 5)
    host = Settings.ISSUER_API
    
    @task
    def create_user(self):
        client_id = str(uuid.uuid4())
        wallet_opts = {
            'wallet_key': hashlib.md5(client_id).hexdigest(),
            'wallet_name': client_id,
            'wallet_type': 'askar-anoncreds'
        }
        with self.client.post("/multitenancy/wallet", json=wallet_opts) as response:
            pass
        webvh_conf = {
            'server_url': Settings.WEBVH_SERVER,
            'witness_invitation': Settings.WITNESS_INVITATION
        }
        with self.client.post("/did/webvh/configuration", json=webvh_conf) as response:
            pass
        webvh_opts = {
            'options': {
                'namespace': Settings.WEBVH_NAMESPACE,
                'identifier': client_id,
                'parameters': {
                    'portable': False,
                    'prerotation': False
                }
            }
        }
        with self.client.post("/did/webvh/create", json=webvh_opts) as response:
            pass
        
    # def on_start(self):
    #     admin_endpoint = Settings.HOLDER_API
    #     webvh_server = Settings.WEBVH_SERVER
    #     self.agent = AgentController(admin_endpoint, webvh_server)
    #     self.agent.provision_client()