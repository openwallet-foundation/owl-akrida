from locust import events
import time
import inspect



def stopwatch(func):
    def wrapper(*args, **kwargs):
        # get task's function name
        previous_frame = inspect.currentframe().f_back
        file_name, _, task_name, _, _ = inspect.getframeinfo(previous_frame)

        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(
                request_type="TYPE",
                name=file_name + "_" + task_name,
                response_time=total,
                exception=e,
                response_length=0,
            )
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(
                request_type="TYPE",
                name=file_name + "_" + task_name,
                response_time=total,
                response_length=0,
            )
        return result

    return wrapper

class CustomClient:
    def __init__(self, host):
        self.host = host
        self.agent = None
        self.errors = 0
        self.port = None
        self.withMediation = None


        # # Load modules here depending on config
        # if ISSUER_TYPE == 'acapy':
        #     from issuerAgent.acapy import AcapyIssuer
        #     self.issuer = AcapyIssuer()
            
        # if VERIFIER_TYPE == 'acapy':
        #     from verifierAgent.acapy import AcapyVerifier
        #     self.verifier = AcapyVerifier()
            
    _locust_environment = None

    @stopwatch
    def startup(self, withMediation=True, reinstantiate=False):
        if (not self.withMediation) and self.withMediation is None:
            self.withMediation = withMediation
        try:
            self.port = ''

            self.errors = 0
            self.agent = ''

            self.run_command(
                {
                    "cmd": "start",
                    "withMediation": self.withMediation,
                    "port": self.port,
                    "agentConfig": self.agentConfig if reinstantiate else None,
                }
            )

            # Create the wallet for the first time
            self.agentConfig = self.readjsonline()["result"]
            # self.agentConfig = self.agent.stdout.readline()

            # we tried to start the agent and failed
            if self.agent is None or self.agent.poll() is not None:
                raise Exception("unable to start")
            
        except Exception as e:
            self.shutdown()
            raise e