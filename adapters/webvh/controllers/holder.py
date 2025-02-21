import uuid
import secrets
import hashlib
import requests
from settings import Settings

class HolderController:
    def __init__(self):
        self.admin_endpoint = Settings.HOLDER_ADMIN_API
        self.webvh_server = Settings.WEBVH_SERVER
        self.webvh_namespace = Settings.WEBVH_NS
        
    def provision_client(self, invitation):
        self.client_id = str(uuid.uuid4())
        
        wallet_info = self.create_subwallet(self.client_id)
        self.wallet_id = wallet_info['wallet_id']
        
        token = wallet_info['token']
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        
        self.create_webvh(
            self.client_id,
            invitation
        )
        self.set_connection(f'{self.webvh_server}@witness')
        
    def set_headers(self, token):
        self.headers = {'Authorization': f'Bearer {token}'}
        return self.headers
        
    def set_connection(self, alias):
        r = requests.get(
            f'{self.admin_endpoint}/connections?alias={alias}',
            headers=self.headers
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        
    def accept_invitation(self, invitation):
        alias = invitation.get('label')
        r = requests.post(
            f'{self.admin_endpoint}/out-of-band/receive-invitation?alias={alias}',
            headers=self.headers,
            json=invitation
        )
        self.connection_id = r.json().get('connection_id')
        return r.json()
        
    def create_subwallet(self):
        wallet_name = str(uuid.uuid4())
        r = requests.post(
            f'{self.admin_endpoint}/multitenancy/wallet',
            json={
                'wallet_key': hashlib.md5(wallet_name.encode()).hexdigest(),
                'wallet_name': wallet_name,
                'wallet_type': 'askar-anoncreds'
            }
        )
        self.wallet_info = r.json()
        self.wallet_id = self.wallet_info.get('wallet_id')
        self.token = self.wallet_info.get('token')
        self.set_headers(self.wallet_info.get('token'))
        return self.wallet_info
        
    def configure_webvh(self, invitation_url):
        r = requests.post(
            f'{self.admin_endpoint}/did/webvh/configuration',
            headers=self.headers,
            json={
                'server_url': self.webvh_server,
                'witness_invitation': invitation_url
            }
        )
        return r.json()
        
    def create_webvh(self, wallet_name, invitation_url):
        self.configure_webvh(invitation_url)
        r = requests.post(
            f'{self.admin_endpoint}/did/webvh/create',
            headers=self.headers,
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