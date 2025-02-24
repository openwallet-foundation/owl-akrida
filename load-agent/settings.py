import os
import json
from dotenv import load_dotenv

load_dotenv()

class Settings(object):
    
    # Load agent settings
    START_PORT = json.loads(os.getenv("START_PORT"))
    END_PORT = json.loads(os.getenv("END_PORT"))
    
    # Load test data
    SCHEMA_ID: str = os.getenv("SCHEMA")
    CRED_DEF_ID: str = os.getenv("CRED_DEF")
    CRED_ATTR: dict = json.loads(os.getenv("CRED_ATTR"))
    
    # Load test parameters
    SHUTDOWN_TIMEOUT_SECONDS: int = 10
    READ_TIMEOUT_SECONDS: int = 120
    ERRORS_BEFORE_RESTART: int = 10
    # How long to wait for verified = true state
    VERIFIED_TIMEOUT_SECONDS: int = int(os.getenv("VERIFIED_TIMEOUT_SECONDS", 20))
    # Message to send mediator, defaults to "ping"
    MESSAGE_TO_SEND = os.getenv("MESSAGE_TO_SEND", "ping")

    RAW_OOB_BOOL = os.getenv("OOB_INVITE")
    if RAW_OOB_BOOL == "False":
        # Handles case when string False passed in (AKA accidentally evals to True)
        OOB_INVITE = False
    else: 
        OOB_INVITE = bool(os.getenv("OOB_INVITE", False))

    # Verifier
    VERIFIER_URL: str = os.getenv("VERIFIER_URL")
    VERIFIER_TYPE: str = os.getenv("VERIFIER_TYPE", "acapy")
    # VERIFIER_API_KEY: str = os.getenv("VERIFIER_API_KEY", None)
    # VERIFIER_API_TOKEN: str = os.getenv("VERIFIER_API_TOKEN", None)
    VERIFIER_HEADERS: str = json.loads(os.getenv("VERIFIER_HEADERS"))

    # Issuer
    ISSUER_URL: str = os.getenv("ISSUER_URL")
    ISSUER_TYPE: str = os.getenv("ISSUER_TYPE", "acapy")
    # ISSUER_API_KEY: str = os.getenv("ISSUER_API_KEY", None)
    # ISSUER_API_TOKEN: str = os.getenv("ISSUER_API_TOKEN", None)
    ISSUER_HEADERS: str = json.loads(os.getenv("ISSUER_HEADERS"))