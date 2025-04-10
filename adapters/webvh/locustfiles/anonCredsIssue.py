from locust import SequentialTaskSet, FastHttpUser, task, events, between
from settings import Settings
from controllers import HolderController, IssuerController
from utils import create_issue_credential_payload
import time


@events.init.add_listener
def on_test_start(environment, **kwargs):
    IssuerController().provision()


class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        issuer = IssuerController()
        issuer.provision()

        holder = HolderController()
        holder.create_subwallet()
        holder.accept_invitation(
            issuer.single_use_invitation(holder.wallet_id).get("invitation")
        )

        self.connection_id = issuer.get_connection(holder.wallet_id).get(
            "connection_id"
        )
        self.cred_def_id = issuer.find_cred_def().get("credential_definition_ids")[0]
        self.rev_reg_id = (
            issuer.get_active_rev_reg(self.cred_def_id)
            .get("result")
            .get("revoc_reg_id")
        )
        self.issuer_id = self.cred_def_id.split("/")[0]
        print(self.cred_def_id)
        print(self.rev_reg_id)
        return

    def on_stop(self):
        return

    @task
    def issue_credential(self):
        credential_offer = create_issue_credential_payload(
            self.issuer_id,
            self.cred_def_id,
            self.connection_id,
            Settings.CREDENTIAL.get("preview"),
        )
        with self.client.post(
            "/issue-credential-2.0/send", catch_response=True, json=credential_offer
        ) as response:
            
            if response.status_code == 200:
                self.cred_ex_id = response.json().get("cred_ex_id")
                if not self.cred_ex_id:
                    response.failure("No credential exchange")
            else:
                response.failure("Bad status code")

            for attempt in range(Settings.ISSUANCE_DELAY_LIMIT):
                time.sleep(1)
                issuance = IssuerController().check_issuance(self.cred_ex_id)
                state = issuance.get("cred_ex_record").get("state")
                print(f'Issuance: {state}')
                if state == "done":
                    response.success()
                    break
            if state != 'done':
                response.failure("Incomplete exchange")


class User(FastHttpUser):
    tasks = [UserBehaviour]
    wait_time = between(Settings.LOCUST_MIN_WAIT, Settings.LOCUST_MAX_WAIT)
    host = Settings.ISSUER_ADMIN_API
