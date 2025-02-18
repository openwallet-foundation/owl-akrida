
class Agent:
        def get_invite(self, out_of_band=False):
                raise NotImplementedError

        def is_up(self):
                raise NotImplementedError

        def issue_credential(self, connection_id):
                raise NotImplementedError

        def request_presentation(self, connection_id):
                raise NotImplementedError

        def send_message(self, connection_id, msg):
                raise NotImplementedError