from abc import ABC

import requests
from settings import Settings


class BaseAgent(ABC):
    def __init__(self):
        print("BaseAgent initialized")
        self.agent_url = Settings.ISSUER_URL
        self.headers = Settings.ISSUER_HEADERS | {"Content-Type": "application/json"}

    def get_invite(self):                    
        r = requests.post(
            f"{self.agent_url}/out-of-band/create-invitation?auto_accept=true",
            json={"handshake_protocols": Settings.HANDSHAKE_PROTOCOLS},
            headers=self.headers,
        )
        invitation = r.json()
        
        r = requests.get(
            f"{self.agent_url}/connections",
            params={"invitation_msg_id": invitation["invi_msg_id"]},
            headers=self.headers,
        )
        connection = r.json()["results"][0]
        
        return {
            "invitation_url": invitation["invitation_url"],
            "connection_id": connection["connection_id"],
        }

    def is_up(self):
        try:
            r = requests.get(
                f"{self.agent_url}/status",
                headers=self.headers,
            )
            if r.status_code != 200:
                raise Exception(r.content)

            r.json()
        except Exception:
            return False

        return True

    def send_message(self, connection_id, msg):
        requests.post(
            f"{self.agent_url}/connections/{connection_id}/send-message",
            json={"content": msg},
            headers=self.headers,
        )
