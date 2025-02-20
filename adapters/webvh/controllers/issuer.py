import uuid
import secrets
import requests
import json
from settings import Settings

class IssuerController:
    def __init__(self):
        self.admin_endpoint = Settings.ISSUER_ADMIN_API
        self.witness_key = Settings.WITNESS_KEY
        self.webvh_server = Settings.WEBVH_SERVER
        self.webvh_namespace = Settings.WEBVH_NS
        self.webvh_identifier = str(uuid.uuid4())
        
    def setup_anoncreds(self):
        self.configure_webvh()
        self.create_webvh()
        self.multi_use_invitation()
        self.schema_id = requests.post(
            f'{self.admin_endpoint}/anoncreds/schema',
            json={
                "schema": {
                    "attrNames": [attribute for attribute in Settings.CREDENTIAL.get('attributes')],
                    "issuerId": self.issuer_id,
                    "name": Settings.CREDENTIAL.get('name'),
                    "version": Settings.CREDENTIAL.get('version')
                }
            }
        ).json().get('schema_state').get('schema_id')
        self.cred_def_id = requests.post(
            f'{self.admin_endpoint}/anoncreds/credential-definition',
            json={
                # 'options': {
                #     'support_revocation': True,
                #     'revocation_registry_size': Settings.CREDENTIAL.get('size')
                # },
                "credential_definition": {
                    "issuerId": self.issuer_id,
                    "schemaId": self.schema_id,
                    "tag": Settings.CREDENTIAL.get('name')
                },
            }
        ).json().get('credential_definition_state').get('credential_definition_id')
        # self.rev_reg_id = requests.post(
        #     f'{self.admin_endpoint}/anoncreds/credential-definition',
        #     json={}
        # )
        self.multi_use_invitation()
        
    def multi_use_invitation(self):
        r = requests.post(
            f'{self.admin_endpoint}/out-of-band/create-invitation?multi_use=true',
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
            f'{self.admin_endpoint}/out-of-band/create-invitation',
            json={
                "alias": alias,
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
            f'{self.admin_endpoint}/connections?alias={alias}'
        )
        self.connection_id = r.json()['results'][0]['connection_id']
        
    def configure_webvh(self):
        requests.post(
            f'{self.admin_endpoint}/did/webvh/configuration',
            json={
                'server_url': self.webvh_server,
                'witness_auto': True,
                'witness': True,
                'witness_key': self.witness_key
            }
        )
        
    def create_webvh(self):
        r = requests.post(
            f'{self.admin_endpoint}/did/webvh/create',
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
        
    def add_key(self, kid):
        r = requests.post(
            f'{self.admin_endpoint}/wallet/keys',
            json={
                'kid': kid,
            }
        )
        print(r.json()['multikey'])