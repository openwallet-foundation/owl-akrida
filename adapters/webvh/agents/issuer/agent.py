import uuid
import secrets
import requests

class AgentController:
    def __init__(self, webvh_server, admin_endpoint, admin_api_key=None):
        self.admin_endpoint = admin_endpoint
        self.admin_api_key = admin_api_key
        self.webvh_server = webvh_server
        self.webvh_namespace = 'akrida'
        self.admin_headers = {'X-API-KEY': self.admin_api_key}
        
    def provision_client(self, invitation):
        identifier = ''
        self.create_webvh(
            identifier,
            invitation
        )
        
    def set_connection(self, alias):
        r = requests.get(
            f'{self.admin_endpoint}/connections?alias={alias}',
            headers=self.admin_headers
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        
    def create_webvh(self, wallet_name, invitation):
        requests.post(
            f'{self.admin_endpoint}/did/webvh/configuration',
            headers=self.admin_headers,
            json={
                'server_url': self.webvh_server,
                'witness_auto': True,
                'witness': True
            }
        )
        r = requests.post(
            f'{self.admin_endpoint}/did/webvh/create',
            headers=self.admin_headers,
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