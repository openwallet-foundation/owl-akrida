import uuid
import secrets
import requests
import json
from settings import Settings

class IssuerController:
    def __init__(self):
        self.label = 'OWL Akrida Issuer'
        self.admin_api = Settings.ISSUER_ADMIN_API
        self.headers = {'X-API-KEY': Settings.ISSUER_ADMIN_API_KEY}
        self.witness_key = Settings.WITNESS_KEY
        self.webvh_server = Settings.WEBVH_SERVER
        self.webvh_namespace = Settings.WEBVH_NS
        self.webvh_identifier = str(uuid.uuid4())
        
    def provision(self):
        self.configure_webvh()
        if not self.find_cred_def().get('credential_definition_ids')[0]:
            self.create_webvh()
            self.setup_anoncreds()
        
    def setup_anoncreds(self):
        self.schema_id = self.create_schema().get('schema_state').get('schema_id')
        self.cred_def_id = self.create_cred_def(self.schema_id).get('credential_definition_state').get('credential_definition_id')
        self.rev_reg_id = self.get_active_rev_reg(self.cred_def_id).get('result').get('revoc_reg_id')
        
    def create_schema(self):
        r = requests.post(
            f'{self.admin_api}/anoncreds/schema',
            # headers=self.headers,
            json={
                "schema": {
                    "attrNames": [attribute for attribute in Settings.CREDENTIAL.get('preview')],
                    "issuerId": self.issuer_id,
                    "name": Settings.CREDENTIAL.get('name'),
                    "version": Settings.CREDENTIAL.get('version')
                }
            }
        )
        return r.json()
        
    def create_cred_def(self, schema_id):
        r = requests.post(
            f'{self.admin_api}/anoncreds/credential-definition',
            # headers=self.headers,
            json={
                'options': {
                    'support_revocation': True,
                    'revocation_registry_size': Settings.CREDENTIAL.get('size')
                },
                "credential_definition": {
                    "issuerId": self.issuer_id,
                    "schemaId": schema_id,
                    "tag": Settings.CREDENTIAL.get('name')
                },
            }
        )
        return r.json()
    
    def get_active_rev_reg(self, cred_def_id):
        encoded_cred_def_id = cred_def_id.replace('/', r'%2f')
        r = requests.get(
            f'{self.admin_api}/anoncreds/revocation/active-registry/{encoded_cred_def_id}',
            # headers=self.headers,
        )
        return r.json()
        
    def multi_use_invitation(self):
        r = requests.post(
            f'{self.admin_api}/out-of-band/create-invitation?multi_use=true',
            # headers=self.headers,
            json={
                "handshake_protocols": [
                    "https://didcomm.org/didexchange/1.0"
                ]
            }
        )
        self.invitation = r.json().get('invitation')
        self.invitation_url = r.json().get('invitation_url')
        
    def single_use_invitation(self, alias):
        r = requests.post(
            f'{self.admin_api}/out-of-band/create-invitation',
            # headers=self.headers,
            json={
                "alias": alias,
                "my_label": self.label,
                "handshake_protocols": [
                    "https://didcomm.org/didexchange/1.0"
                ]
            }
        )
        self.invitation = r.json().get('invitation')
        self.invitation_url = r.json().get('invitation_url')
        self.set_connection(alias)
        return r.json()
        
    def set_connection(self, alias):
        r = requests.get(
            f'{self.admin_api}/connections?alias={alias}',
            # headers=self.headers,
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        return r.json()
        
    def configure_webvh(self):
        r = requests.post(
            f'{self.admin_api}/did/webvh/configuration',
            # headers=self.headers,
            json={
                'server_url': self.webvh_server,
                'witness_auto': True,
                'witness': True,
                'witness_key': self.witness_key
            }
        )
        return r.json()
        
    def create_webvh(self):
        r = requests.post(
            f'{self.admin_api}/did/webvh/create',
            # headers=self.headers,
            json={
                'options': {
                    'namespace': self.webvh_namespace,
                    'identifier': self.webvh_identifier,
                    'parameters': {
                        'portable': False,
                        'prerotation': False
                    }
                }
            }
        )
        self.issuer_id = r.json().get('id')
        return r.json()
        
    def add_key(self, kid):
        r = requests.post(
            f'{self.admin_api}/wallet/keys',
            # headers=self.headers,
            json={
                'kid': kid,
            }
        )
        print(r.json()['multikey'])
        
    def get_connection(self, alias):
        r = requests.get(
            f'{self.admin_api}/connections?alias={alias}',
            # headers=self.headers,
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        return r.json()['results'][0]
    
    def find_cred_def(
        self, 
        schema_name=Settings.CREDENTIAL.get('name'), 
        schema_version=Settings.CREDENTIAL.get('version')
        ):
        r = requests.get(
            f'{self.admin_api}/anoncreds/credential-definitions??schema_name={schema_name}&schema_version={schema_version}',
            # headers=self.headers,
        )
        return r.json()