import uuid
import secrets
import hashlib
import requests

class AgentController:
    def __init__(self, webvh_server, admin_endpoint, admin_api_key=None):
        self.admin_endpoint = admin_endpoint
        self.admin_api_key = admin_api_key
        self.webvh_server = webvh_server
        self.webvh_namespace = 'akrida'
        self.admin_headers = {'X-API-KEY': self.admin_api_key}
        
    def provision_client(self, invitation):
        self.client_id = str(uuid.uuid4())
        
        wallet_info = self.create_subwallet(self.client_id)
        self.wallet_id = wallet_info['wallet_id']
        
        token = wallet_info['token']
        self.client_headers = {
            'Authorization': f'Bearer {token}'
        }
        
        self.create_webvh(
            self.client_id,
            invitation
        )
        self.set_connection(f'{self.webvh_server}@witness')
        
    def set_connection(self, alias):
        r = requests.get(
            f'{self.admin_endpoint}/connections?alias={alias}',
            headers=self.client_headers
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        
    def create_subwallet(self, client_id):
        r = requests.post(
            f'{self.admin_endpoint}/multitenancy/wallet',
            headers=self.admin_headers,
            json={
                'wallet_key': hashlib.md5(client_id).hexdigest(),
                'wallet_name': client_id,
                'wallet_type': 'askar-anoncreds'
            }
        )
        return r.json()
        
    def create_webvh(self, wallet_name, invitation):
        requests.post(
            f'{self.admin_endpoint}/did/webvh/configuration',
            headers=self.client_headers,
            json={
                'server_url': self.webvh_server,
                'witness_invitation': invitation
            }
        )
        r = requests.post(
            f'{self.admin_endpoint}/did/webvh/create',
            headers=self.client_headers,
            json={
                'options': {
                    'namespace': self.webvh_namespace,
                    'identifier': wallet_name,
                    'parameters': {
                        'portable': False,
                        'prerotation': False
                    }
                }
            }
        )
        return r.json()