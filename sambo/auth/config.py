import os

import dotenv
import fastapi.security

dotenv.load_dotenv()

SECRET_KEY = os.environ["APP_SECRET_KEY"]
ALGORITHM = os.environ["APP_HASH_ALGORITHM"]
PASSWORD_MIN_LENGTH = 8
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")
