from locust import task, HttpUser
from constants import standard_wait
import os
from string import Template
from urllib.parse import quote

global template
global base_url
global rev_reg_def
global url
template = Template('/revocation-registry-definition/$revregdef')
base_url = os.getenv('VDR_BASE_URL')
rev_reg_def = os.getenv('VDR_REV_REG_DEF')
url = quote(template.substitute(revregdef=rev_reg_def))

class IndyVDRProxyRevRegDefLookup(HttpUser):
    wait_time = standard_wait
    host = base_url

    @task
    def lookup_rev_reg_def(self):
        with self.client.get(url, headers={"Connection": "close"}, verify=False, catch_response=True) as response:
            try:
                data = response.json()
                rrd = data['revocationRegistryDefinitionId']
                if rrd == rev_reg_def:
                    response.success()
                else:
                    print("Incorrect response")
                    response.failure("Incorrect response")
            except Exception as e:
                print("Error thrown")
                print(e)
                response.failure("Error thrown")
