
class BaseIssuer:

        def get_invite(self):
                # return  {'invitation_url': , 'connection_id': }
                raise NotImplementedError

        def is_up(self):
                # return True/False
                raise NotImplementedError

        def issue_credential(self, connection_id):
                # return { "connection_id": , "cred_ex_id":  ] }
                raise NotImplementedError

        def revoke_credential(self, connection_id, credential_exchange_id):
                raise NotImplementedError

        def send_message(self, connection_id, msg):
                raise NotImplementedError