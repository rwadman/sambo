import os

import dotenv
import fastapi

from . import auth, expenses

dotenv.load_dotenv()
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ["APP_SECRET_KEY"]
ALGORITHM = os.environ["APP_HASH_ALGORITHM"]
SQL_ALCHEMY_URI = os.environ["APP_SQL_ALCHEMY_URI"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = fastapi.FastAPI()

auth.setup_routes(app)
expenses.setup_routes(app)
