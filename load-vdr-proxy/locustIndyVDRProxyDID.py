from locust import task, HttpUser
from constants import standard_wait
import os
from string import Template
from urllib.parse import quote

global template
global base_url
global did
global url
template = Template('/did/$did')
base_url = os.getenv('VDR_BASE_URL')
did = os.getenv('VDR_DID')
url = quote(template.substitute(did=did))

class IndyVDRProxyDIDLookup(HttpUser):
    wait_time = standard_wait
    host = base_url

    @task
    def lookup_did(self):
        with self.client.get(url, headers={"Connection": "close"}, verify=False, catch_response=True) as response:
            try:
                data = response.json()
                # there are a variety of did formats. using the base did in the .env file 
                # (only the id, no prefix) helps ensure there are no false negatives from
                # the check below
                d = data['didDocument']['id']
                if did in d:
                    response.success()
                else:
                    print("Incorrect response")
                    response.failure("Incorrect response")
            except Exception as e:
                print("Error thrown")
                print(e)
                response.failure("Error thrown")
