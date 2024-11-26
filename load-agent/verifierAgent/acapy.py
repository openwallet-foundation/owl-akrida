from .base import BaseVerifier
import json
import os
import requests
import time

from json.decoder import JSONDecodeError

VERIFIED_TIMEOUT_SECONDS = int(os.getenv("VERIFIED_TIMEOUT_SECONDS", 20))

class AcapyVerifier(BaseVerifier):

        def get_invite(self, out_of_band=False):
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                headers["Content-Type"] = "application/json"

                if out_of_band:
                        # Out of Band Connection 
                        # (ACA-Py v10.4 - only works with connections protocol, not DIDExchange) 
                        r = requests.post(
                                os.getenv("VERIFIER_URL") + "/out-of-band/create-invitation?auto_accept=true", 
                                json={
                                "metadata": {}, 
                                "handshake_protocols": ["https://didcomm.org/connections/1.0"]
                                },
                                headers=headers
                        )
                else:
                        # Regular Connection
                        r = requests.post(
                                os.getenv("VERIFIER_URL") + "/connections/create-invitation?auto_accept=true",
                                json={"metadata": {}, "my_label": "Test"},
                                headers=headers,
                        )

                        # Ensure the request worked
                        try:
                                try_var = r.json()["invitation_url"]
                        except Exception:
                                raise Exception("Failed to get invitation url. Request: ", r.json())
                        if r.status_code != 200:
                                raise Exception(r.content)

                r = r.json()

                # If OOB, need to grab connection_id
                if out_of_band:
                        invitation_msg_id = r['invi_msg_id']
                        g = requests.get(
                                os.getenv("VERIFIER_URL") + "/connections",
                                params={"invitation_msg_id": invitation_msg_id},
                                headers=headers,
                        )
                        # Returns only one
                        connection_id = g.json()['results'][0]['connection_id']
                        r['connection_id'] = connection_id 
                
                return {
                        'invitation_url': r['invitation_url'], 
                        'connection_id': r['connection_id']
                }

        def is_up(self):
                try:
                        headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                        headers["Content-Type"] = "application/json"
                        r = requests.get(
                                os.getenv("VERIFIER_URL") + "/status",
                                json={"metadata": {}, "my_label": "Test"},
                                headers=headers,
                        )
                        if r.status_code != 200:
                                raise Exception(r.content)

                        r = r.json()
                except:
                        return False

                return True

        def create_connectionless_request(self):
                # Calling verification agent
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                headers["Content-Type"] = "application/json"

                # API call to /present-proof/create-request
                r = requests.post(
                        os.getenv("VERIFIER_URL") + "/present-proof/create-request",
                        json={
                                "auto_remove": False,
                                "auto_verify": True,
                                "comment": "Performance Verification",
                                "proof_request": {
                                "name": "PerfScore",
                                "requested_attributes": {
                                        item["name"]: {"name": item["name"]}
                                        for item in json.loads(os.getenv("CRED_ATTR"))
                                },
                                "requested_predicates": {},
                                "version": "1.0",
                                },
                                "trace": True,
                        },
                        headers=headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r
                        )
                
                r = r.json()

                return r
        
        def request_verification(self, connection_id):
                # From verification side
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"

                verifier_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")

                # Might need to change nonce
                # TO DO: Generalize schema parts
                r = requests.post(
                        os.getenv("VERIFIER_URL") + "/present-proof/send-request",
                        json={
                                "auto_remove": False,
                                "auto_verify": True,
                                "comment": "Performance Verification",
                                "connection_id": connection_id,
                                "proof_request": {
                                "name": "PerfScore",
                                "requested_attributes": {
                                        item["name"]: {"name": item["name"]}
                                        for item in json.loads(os.getenv("CRED_ATTR"))
                                },
                                "requested_predicates": {},
                                "version": "1.0",
                                },
                                "trace": True,
                        },
                        headers=headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r
                        )
                
                r = r.json()

                return r['presentation_exchange_id']
        

        def request_verification_2_0(self, connection_id):
                # From verification side
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"

                verifier_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")
                # Might need to change nonce
                # TO DO: Generalize schema parts
                
                payload = {
                        "auto_remove": False,
                        "auto_verify": True,
                        "comment": "Performance Verification",
                        "connection_id": connection_id, 
                        "presentation_request": {
                                "indy": {
                                "name": "PerfScore",  
                                "requested_attributes": {
                                        item["name"]: {
                                        "name": item["name"],
                                        }
                                        for item in json.loads(os.getenv("CRED_ATTR"))
                                },
                                "requested_predicates": {},
                                "version": "1.0",
                                }
                        },
                        "trace": True,
                        }
                        
                r = requests.post(
                        os.getenv("VERIFIER_URL") + "/present-proof-2.0/send-request",
                        json=payload,
                        headers=headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r
                        )
                
                r = r.json()

                return r['pres_ex_id']


        def request_non_revo_verification(self, connection_id):
                # From verification side
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"

                verifier_did = os.getenv("CRED_DEF_NR").split(":")[0]
                schema_parts = os.getenv("SCHEMA_NR").split(":")

                # Might need to change nonce
                # TO DO: Generalize schema parts
                r = requests.post(
                        os.getenv("VERIFIER_URL") + "/present-proof/send-request",
                        json={
                                "auto_remove": False,
                                "auto_verify": True,
                                "comment": "Performance Verification",
                                "connection_id": connection_id,
                                "proof_request": {
                                "name": "PerfScore",
                                "requested_attributes": {
                                        item["name"]: {"name": item["name"]}
                                        for item in json.loads(os.getenv("CRED_ATTR"))
                                },
                                "requested_predicates": {},
                                "version": "1.0",
                                },
                                "trace": True,
                        },
                        headers=headers,
                )

                try:
                        if r.status_code != 200:
                                raise Exception("Request was not successful: ", r.content)
                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while parsing the request: ", r
                        )
                
                r = r.json()

                return r['presentation_exchange_id']

        def verify_verification(self, presentation_exchange_id):
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"
                # Want to do a for loop
                iteration = 0
                try:
                        while iteration < VERIFIED_TIMEOUT_SECONDS:
                                g = requests.get(
                                        os.getenv("VERIFIER_URL") + f"/present-proof/records/{presentation_exchange_id}",
                                        headers=headers,
                                )
                                if (
                                        g.json()["state"] != "request_sent"
                                        and g.json()["state"] != "presentation_received"
                                ):
                                        "request_sent" and g.json()["state"] != "presentation_received"
                                        break
                                iteration += 1
                                time.sleep(1)

                        if g.json()["verified"] != "true":
                                raise AssertionError(
                                        f"Presentation was not successfully verified. Presentation in state {g.json()['state']}"
                                )

                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while getting the presentation record: ", g
                        )

                return True
        

        def verify_verification_2_0(self, pres_ex_id):
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))  # headers same
                headers["Content-Type"] = "application/json"
                # Want to do a for loop
                iteration = 0
                try:
                        while iteration < VERIFIED_TIMEOUT_SECONDS:
                                g = requests.get(
                                        os.getenv("VERIFIER_URL") + f"/present-proof-2.0/records/{pres_ex_id}",
                                        headers=headers,
                                )
                                response_text = g.json()
                                if (
                                        g.json()["state"] != "request-sent"
                                        and g.json()["state"] != "presentation-received"
                                ):
                                        "request-sent" and g.json()["state"] != "presentation-received"
                                        break
                                iteration += 1
                                time.sleep(1)

                        if g.json()["verified"] != "true":
                                raise AssertionError(
                                        f"Presentation was not successfully verified. Presentation in state {g.json()['state']}"
                                )

                except JSONDecodeError as e:
                        raise Exception(
                                "Encountered JSONDecodeError while getting the presentation record: ", g
                        )

                return True

        def send_message(self, connection_id, msg):
                headers = json.loads(os.getenv("VERIFIER_HEADERS"))
                headers["Content-Type"] = "application/json"

                r = requests.post(
                        os.getenv("ISSUER_URL") + "/connections/" + connection_id + "/send-message",
                        json={"content": msg},
                        headers=headers,
                )
                r = r.json()