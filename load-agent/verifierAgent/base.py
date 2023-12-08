
class BaseVerifier:
        def get_invite(self):
                # return  {'invitation_url': , 'connection_id': }
                raise NotImplementedError

        def is_up(self):
                # return True/False
                raise NotImplementedError
