from locust import task, HttpUser
from constants import standard_wait
import os
from string import Template
from urllib.parse import quote

global template
global base_url
global schema
global url
template = Template('/schema/$schemaid')
base_url = os.getenv('VDR_BASE_URL')
schema = os.getenv('VDR_SCHEMA')
url = quote(template.substitute(schemaid=schema))

class IndyVDRProxySchemaLookup(HttpUser):
    wait_time = standard_wait
    host = base_url

    @task
    def lookup_schema(self):
        with self.client.get(url, headers={"Connection": "close"}, verify=False, catch_response=True) as response:
            try:
                data = response.json()
                sid = data['schemaId']
                if sid == schema and int(response.status_code) in range(200, 300):
                    response.success()
                else:
                    print("Incorrect response")
                    response.failure("Incorrect response")
            except Exception as e:
                print("Error thrown")
                print(e)
                response.failure("Error thrown")
