
class BaseVerifier:
        def get_invite(self, out_of_band=False):
                # return  {'invitation_url': , 'connection_id': }
                raise NotImplementedError

        def is_up(self):
                # return True/False
                raise NotImplementedError

        def request_verification(self, connection_id):
                # return r['presentation_exchange_id']
                raise NotImplementedError

        def verify_verification(self, presentation_exchange_id):
                # return True on success
                # Throw Exception on failure
                raise NotImplementedError

        def send_message(self, connection_id, msg):
                raise NotImplementedError