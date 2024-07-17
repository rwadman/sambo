import os
import typing as t

import dotenv
import fastapi

from . import auth

dotenv.load_dotenv()
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ["APP_SECRET_KEY"]
ALGORITHM = os.environ["APP_HASH_ALGORITHM"]
SQL_ALCHEMY_URI = os.environ["APP_SQL_ALCHEMY_URI"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app = fastapi.FastAPI()

auth.setup_routes(app)


@app.get("/users/me/", response_model=auth.User)
async def read_users_me(
    current_user: t.Annotated[auth.User, fastapi.Depends(auth.get_current_active_user)],
) -> auth.User:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: t.Annotated[auth.User, fastapi.Depends(auth.get_current_active_user)],
) -> list[dict]:
    return [{"item_id": "Foo", "owner": current_user.username}]
