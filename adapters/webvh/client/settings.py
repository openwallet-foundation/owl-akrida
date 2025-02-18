from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    WEBVH_DOMAIN = os.getenv('WEBVH_DOMAIN', 'id.test-suite.app')
    WEBVH_SERVER = f'https://{WEBVH_DOMAIN}'
    WEBVH_NAMESPACE = os.getenv('WEBVH_NAMESPACE', 'akrida')
    ISSUER_API = os.getenv('ISSUER_API')
    HOLDER_API = os.getenv('HOLDER_API')
    WITNESS_INVITATION = os.getenv('WITNESS_INVITATION')


settings = Settings()
