import os
from dotenv import load_dotenv

load_dotenv()
class Settings(object):
    
    # WebVH settings
    WITNESS_KEY: str = os.getenv('WITNESS_KEY', 'z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i')
    WEBVH_DOMAIN: str = os.getenv('WEBVH_DOMAIN', 'id.test-suite.app')
    WEBVH_SERVER: str = f'https://{WEBVH_DOMAIN}'
    WEBVH_NS: str = os.getenv('WEBVH_NS', 'akrida')
    
    
    # Acapy agent settings
    ISSUER_ADMIN_API: str = os.getenv('ISSUER_ADMIN_API')
    ISSUER_ADMIN_API_KEY: str = os.getenv('ISSUER_ADMIN_API_KEY')
    HOLDER_ADMIN_API: str = os.getenv('HOLDER_ADMIN_API')
    HOLDER_ADMIN_API_KEY: str = os.getenv('HOLDER_ADMIN_API_KEY')
    
    # Locust settings
    LOCUST_MIN_WAIT: float = float(os.getenv('LOCUST_MIN_WAIT', 0.1))
    LOCUST_MAX_WAIT: float = float(os.getenv('LOCUST_MAX_WAIT', 1))
    
    # AnonCreds settings
    CREDENTIAL_BATCH_SIZE: int = int(os.getenv('CREDENTIAL_BATCH_SIZE', 5))
    CREDENTIAL: dict = {
        'name': 'TestSchema',
        'version': '1.0',
        'size': 50,
        'preview': {
            'givenName': 'Jane',
            'familyName': 'Doe',
            'dob': '20240101',
        },
        'request': {
            'attributes': ['givenName', 'familyName'],
            'predicate': ['dob', '>=', 20000101]
        }
    }
