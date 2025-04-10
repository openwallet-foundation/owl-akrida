from locust import task, HttpUser
from constants import standard_wait
import os
from string import Template
from urllib.parse import quote

global template
global base_url
global cred_def
global url
template = Template('/credential-definition/$creddef')
base_url = os.getenv('VDR_BASE_URL')
cred_def = os.getenv('VDR_CRED_DEF')
url = quote(template.substitute(creddef=cred_def))

class IndyVDRProxyCredDefLookup(HttpUser):
    wait_time = standard_wait
    host = base_url

    @task
    def lookup_cred_def(self):
        with self.client.get(url, headers={"Connection": "close"}, verify=False, catch_response=True) as response:
            try:
                data = response.json()
                cdid = data['credentialDefinitionId']
                if cdid == cred_def:
                    response.success()
                else:
                    print("Incorrect response")
                    response.failure("Incorrect response")
            except Exception as e:
                print("Error thrown")
                print(e)
                response.failure("Error thrown")
