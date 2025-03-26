from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os
from dotenv import load_dotenv

load_dotenv()

USE_GOOGLE_AUTH = os.getenv("USE_GOOGLE_AUTH", "False").lower() == "true"

oauth = OAuth()

if USE_GOOGLE_AUTH:
    config = Config(environ=os.environ)
    
    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
