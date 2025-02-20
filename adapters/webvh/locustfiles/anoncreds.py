import time
from random import randint, getrandbits
from locust import SequentialTaskSet, FastHttpUser, task, events, between
from controllers import HolderController, IssuerController
from utils import create_issue_credential_payload, create_request_presentation_payload
from settings import Settings

@events.test_start.add_listener
def on_locust_start(environment, **kwargs):
    issuer = IssuerController()
    issuer.setup_anoncreds()

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        self.holder = HolderController()
        self.holder.create_subwallet()
        
        self.issuer = IssuerController()
        self.issuer.single_use_invitation(self.holder.wallet_id)
        
        self.holder.accept_invitation(invitation=self.issuer.invitation)
    
    def on_stop(self):
        pass
    
    @task
    def issue_credential(self):
        self.cred_batch = []
        body = create_issue_credential_payload(
            self.issuer.issuer_id,
            self.issuer.cred_def_id,
            self.issuer.connection_id,
            Settings.CREDENTIAL.get('preview'),
        )
        with self.client.post("/issue-credential-2.0/send", json=body) as response:
            print(response.text)
            self.cred_ex_id = ''
    
    # @task
    # def issue_credential_batch(self):
    #     self.cred_batch = []
    #     body = create_issue_credential_payload(
    #         self.issuer.issuer_id,
    #         self.issuer.cred_def_id,
    #         self.issuer.connection_id,
    #         Settings.CREDENTIAL.get('preview'),
    #     )
    #     for element in Settings.CREDENTIAL_BATCH_SIZE:
    #         with self.client.post("/issue-credential-2.0/send", json=body) as response:
    #             print(response.text)
    #             self.cred_batch.append()
    
    @task
    def verify_presentation(self):
        body = create_request_presentation_payload(
            self.issuer.cred_def_id,
            self.issuer.connection_id,
            Settings.CREDENTIAL.get('request').get('attributes'),
            Settings.CREDENTIAL.get('request').get('predicate'),
            int(time.time()),
        )
        with self.client.post("/present-proof-2.0/send-request", json=body) as response:
            self.pres_ex_id = ''
            print(response.text)
    
    @task
    def revoke_credential(self):
        body = {
            'cred_ex_id': self.cred_ex_id,
            'publish': True,
        }
        with self.client.post("/anoncreds/revocation/revoke", json=body) as response:
            print(response.text)
    
    # @task
    # def revoke_credential_batch(self):
    #     for cred_ex_id in self.cred_batch:
    #         if bool(getrandbits(1)):
    #             body = {
    #                 'cred_ex_id': cred_ex_id,
    #                 'publish': False,
    #             }
    #             with self.client.post("/anoncreds/revocation/revoke", json=body) as response:
    #                 print(response.text)
    #     with self.client.post("/anoncreds/revocation/publish-revocations", json=body) as response:
    #         print(response.text)

class AnonCredsIssuance(FastHttpUser):
    tasks = [UserBehaviour]
    wait_time = between(Settings.LOCUST_MIN_WAIT, Settings.LOCUST_MAX_WAIT)
    host = Settings.ISSUER_API
        