import os
import typing as t

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
ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "prod").lower()
SHOW_DOCS_ENVIRONMENT = ("local", "staging")

app_config: dict[str, t.Any] = {"title": "Sambo the app"}
if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_config["openapi_url"] = None


app = fastapi.FastAPI(**app_config)  # type: ignore[arg-type]

auth.setup_routes(app)
expenses.setup_routes(app)
