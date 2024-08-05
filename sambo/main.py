import os
import typing as t

import dotenv
import fastapi

from . import auth, expenses

dotenv.load_dotenv()
ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "prod").lower()
SHOW_DOCS_ENVIRONMENT = ("dev", "local", "staging")

app_config: dict[str, t.Any] = {"title": "Sambo the app"}
if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_config["openapi_url"] = None


app = fastapi.FastAPI(**app_config)  # type: ignore[arg-type]

auth.setup_routes(app)
expenses.setup_routes(app)
