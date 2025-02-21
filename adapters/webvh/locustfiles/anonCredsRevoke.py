from locust import SequentialTaskSet, FastHttpUser, task, events, between
from settings import Settings
from controllers import HolderController, IssuerController
from utils import create_issue_credential_payload
import time

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    IssuerController().provision()

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        issuer = IssuerController()
        
        holder = HolderController()
        holder.create_subwallet()
        holder.accept_invitation(
            issuer.single_use_invitation(holder.wallet_id).get('invitation')
        )
        
        self.connection_id = issuer.get_connection(holder.wallet_id).get('connection_id')
        self.cred_def_id = issuer.find_cred_def().get('credential_definition_ids')[0]
        self.rev_reg_id = issuer.get_active_rev_reg(self.cred_def_id).get('result').get('revoc_reg_id')
        self.issuer_id = self.cred_def_id.split('/')[0]
        print(self.rev_reg_id)
        self.batch = 0
        
        # Wait for connection state to become active
        time.sleep(1)
        
        return
    
    def on_stop(self):
        return
    
    @task
    def issue_credential(self):
        pass
        credential_offer = create_issue_credential_payload(
            self.issuer_id,
            self.cred_def_id,
            self.connection_id,
            Settings.CREDENTIAL.get('preview'),
        )
        with self.client.post("/issue-credential-2.0/send", json=credential_offer) as response:
            if response.status_code == 200:
                self.batch += 1
                self.cred_ex_id = response.json().get('cred_ex_id')
            else:
                pass
            
        # Wait for credential exchange
        time.sleep(1)
    
    @task
    def revoke_credential(self):
        payload = {
            'cred_ex_id': self.cred_ex_id,
            'publish': False
        }
        with self.client.post("/anoncreds/revocation/revoke", json=payload) as response:
            if response.status_code == 200:
                pass
            else:
                pass
    
    @task
    def publish_revocation(self):
        if self.batch >= Settings.CREDENTIAL_BATCH_SIZE:
            payload = {}
            with self.client.post("/anoncreds/revocation/publish-revocations", json=payload) as response:
                if response.status_code == 200:
                    self.batch = 0
                else:
                    pass

class User(FastHttpUser):
    tasks = [UserBehaviour]
    wait_time = between(Settings.LOCUST_MIN_WAIT, Settings.LOCUST_MAX_WAIT)
    host = Settings.ISSUER_ADMIN_API