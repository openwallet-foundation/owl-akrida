from locust import SequentialTaskSet, FastHttpUser, task, events, between
from settings import Settings
from controllers import HolderController, IssuerController
import uuid

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    issuer = IssuerController()
    issuer.configure_webvh()

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        holder = HolderController()
        wallet_info = holder.create_subwallet()

        issuer = IssuerController()
        invitation = issuer.single_use_invitation(wallet_info.get('wallet_id'))
        
        holder.configure_webvh(invitation.get('invitation_url'))
        self.headers = holder.set_headers(wallet_info.get('token'))
    
    def on_stop(self):
        pass
    
    @task
    def register_did(self):
        identifier = str(uuid.uuid4())
        create_options = {
            'options': {
                'namespace': Settings.WEBVH_NS,
                'identifier': identifier,
                'parameters': {
                    'portable': False,
                    'prerotation': False
                }
            }
        }
        print(create_options)
        # with self.client.post(
        #     "/did/webvh/create", 
        #     headers=self.headers, 
        #     json=create_options
        #     ) as response:
        #     pass

class User(FastHttpUser):
    tasks = [UserBehaviour]
    wait_time = between(Settings.LOCUST_MIN_WAIT, Settings.LOCUST_MAX_WAIT)
    host = Settings.HOLDER_ADMIN_API