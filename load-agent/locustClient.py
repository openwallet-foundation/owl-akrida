import inspect
import json
import os
import signal
import sys
import time

from gevent import lock as gevent_lock
from gevent import select, subprocess
from locust import events
from settings import Settings


class PortManager:
    def __init__(self):
        self.lock = gevent_lock.BoundedSemaphore()
        self.ports = list(range(Settings.START_PORT, Settings.END_PORT))

    def getPort(self):
        self.lock.acquire()
        try:
            port = self.ports.pop(0)
            return port
        finally:
            self.lock.release()

    def returnPort(self, port):
        self.lock.acquire()
        try:
            self.ports.append(port)
        finally:
            self.lock.release()


portmanager = PortManager()


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
            events.request.fire(
                request_type="TYPE",
                name=f"{file_name}_{task_name}",
                response_time=total,
                response_length=0,
                exception=e,
            )
        else:
            total = int((time.time() - start) * 1000)
            events.request.fire(
                request_type="TYPE",
                name=f"{file_name}_{task_name}",
                response_time=total,
                response_length=0,     # size in bytes
                exception=None
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
        
        self.issuerType = Settings.ISSUER_TYPE
        self.verifierType = Settings.VERIFIER_TYPE
        self.shutdownTimeoutSeconds = Settings.SHUTDOWN_TIMEOUT_SECONDS
        self.readTimeoutSeconds = Settings.READ_TIMEOUT_SECONDS
        self.errorsBeforeRestart = Settings.ERRORS_BEFORE_RESTART
        self.oobInvite = Settings.OOB_INVITE
        self.messageToSend = Settings.MESSAGE_TO_SEND

        # Load modules here depending on config
        self._load_issuer()
        self._load_verifier()

    def _load_issuer(self):
        """Load issuer agent based on configuration"""
        issuer_classes = {
            'acapy': lambda: self._import_and_create('agents.issuer.acapy', 'AcapyIssuer'),
            'acapy_v2': lambda: self._import_and_create('agents.issuer.acapy_v2', 'AcapyIssuer'),
        }
        
        loader = issuer_classes.get(self.issuerType.lower())
        if loader:
            self.issuer = loader()
        else:
            raise ValueError(f"Unsupported issuer type: {self.issuerType}")

    def _load_verifier(self):
        """Load verifier agent based on configuration"""
        verifier_classes = {
            'acapy': lambda: self._import_and_create('agents.verifier.acapy', 'AcapyVerifier'),
            'acapy_v2': lambda: self._import_and_create('agents.verifier.acapy_v2', 'AcapyVerifier'),
        }
        
        loader = verifier_classes.get(self.verifierType.lower())
        if loader:
            self.verifier = loader()
        else:
            raise ValueError(f"Unsupported verifier type: {self.verifierType}")

    def _import_and_create(self, module_path, class_name):
        """Dynamically import module and create instance"""
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls()
            
    _locust_environment = None

    @stopwatch
    def startup(self, withMediation=True, reinstantiate=False):
        if (not self.withMediation) and self.withMediation is None:
            self.withMediation = withMediation
        try:
            if self.port is not None:
                portmanager.returnPort(self.port)
                self.port = None
            self.port = portmanager.getPort()

            self.errors = 0
            self.agent = subprocess.Popen(
                ["node", "--max-old-space-size=128", "dist/agent.js"],
                bufsize=0,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=sys.stderr,
                shell=False,
            )

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

    def shutdown(self):
        # Read output until process closes

        try:
            if self.port:
                portmanager.returnPort(self.port)
                self.port = None

            # We write the command by hand here because if we call the cmd function
            # above we could end up in an infinite loop on shutdown
            self.agent.stdin.write(json.dumps({"cmd": "shutdown"}))
            self.agent.stdin.write("\n")
            self.agent.stdin.flush()

            self.agent.communicate(timeout=self.shutdownTimeoutSeconds)
        except Exception:
            pass
        finally:
            try:
                os.kill(self.agent.pid, signal.SIGTERM)
            except Exception:
                pass
            self.agent = None

    def ensure_is_running(self):
        # Is the agent started?
        if not self.agent:
            self.startup()

        # is the agent still running?
        elif self.agent.poll() is None:
            # check for closed Pipes
            if self.agent.stdout.closed or self.agent.stdin.closed:
                self.startup()
            else:
                return True
        else:
            self.startup()

    def is_running(self):
        # Is the agent started?
        if not self.agent:
            return False

        # is the agent still running?
        elif self.agent.poll() is None:
            # check for closed Pipes
            if self.agent.stdout.closed or self.agent.stdin.closed:
                return False
            else:
                return True
        else:
            return False

    def run_command(self, command):
        try:
            self.agent.stdin.write(json.dumps(command))
            self.agent.stdin.write("\n")
            self.agent.stdin.flush()
        except Exception as e:
            # if we get an exception here, we cannot run any new commands
            self.shutdown()
            raise e

    def readjsonline(self):
        try:
            while True:
                line = None
                raw_line_stdout = None

                if self.agent.stdout.closed:
                    raise Exception("Stdout is closed.")

                q = select.poll()
                q.register(self.agent.stdout, select.POLLIN)

                if q.poll(self.readTimeoutSeconds * 1000):
                    raw_line_stdout = self.agent.stdout.readline()

                    if not raw_line_stdout:
                        raise Exception("EOF reached or empty line received.")

                    try:
                        line = json.loads(raw_line_stdout)
                    except json.JSONDecodeError:
                        # Log non-JSON data and continue reading
                        print(f"{raw_line_stdout.strip()}", file=sys.stderr)
                        continue  # Try reading the next line
                else:
                    raise Exception("Read Timeout")

                if not line or not isinstance(line, dict):
                    print(line, file=sys.stderr)
                    continue  # Skip to next line if somehow still invalid

                if line.get("error") != 0:
                    raise Exception("Error encountered within load testing agent: ", line)

                return line

        except Exception as e:
            self.errors += 1
            if self.errors > self.errorsBeforeRestart:
                self.shutdown()  # Restart if in bad state
            raise e

    @stopwatch
    def ping_mediator(self):
        self.run_command({"cmd": "ping_mediator"})
        self.readjsonline()

    @stopwatch
    def issuer_getinvite(self):
        return self.issuer.get_invite()
        
    @stopwatch
    def issuer_getliveness(self):
        return self.issuer.is_up()

    @stopwatch
    def delete_oob(self, id):
        self.run_command({"cmd": "deleteOobRecordById", "id": id})
        self.readjsonline()

    @stopwatch
    def accept_invite(self, invite, useConnectionDid=False):
        try:
            if useConnectionDid:
                self.run_command({"cmd": "receiveInvitationConnectionDid", "invitationUrl": invite})
            else:
                self.run_command({"cmd": "receiveInvitation", "invitationUrl": invite})
        except Exception:
            self.run_command({"cmd": "receiveInvitation", "invitationUrl": invite})

        line = self.readjsonline()
    
        # Filter out unwanted lines
        if line.get("connection") is None:
            return None
    
        return line["connection"]

    @stopwatch
    def receive_credential(self, connection_id):
        self.run_command({"cmd": "receiveCredential"})

        r = self.issuer.issue_credential(connection_id)
        self.readjsonline()

        return r

    @stopwatch
    def verifier_getinvite(self):
        return self.verifier.get_invite()

    @stopwatch
    def presentation_exchange(self, connection_id):
        self.run_command({"cmd": "presentationExchange"})

        pres_ex_id = self.verifier.request_verification(connection_id)
        self.readjsonline()
        
        self.verifier.verify_verification(pres_ex_id)

    @stopwatch
    def verifier_connectionless_request(self):
        return self.verifier.create_connectionless_request()
    
    @stopwatch
    def revoke_credential(self, credential_exchange):
        self.issuer.revoke_credential(
            credential_exchange['connection_id'],
            credential_exchange['cred_ex_id']
        )

    @stopwatch
    def msg_client(self, connection_id):
        self.run_command({"cmd": "receiveMessage"})

        self.issuer.send_message(connection_id, self.messageToSend)

        line = self.readjsonline()

        return line
