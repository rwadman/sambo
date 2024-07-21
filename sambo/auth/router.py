import datetime as dt
import typing as t

import fastapi
import fastapi.security
from sqlalchemy import orm

from sambo import database

from . import config, dependencies, models, schemas, service


def setup_routes(app: fastapi.FastAPI) -> None:
    @app.post("/token")
    async def login_for_access_token(
        form_data: t.Annotated[fastapi.security.OAuth2PasswordRequestForm, fastapi.Depends()],
        db: t.Annotated[orm.Session, fastapi.Depends(database.get_dep)],
    ) -> schemas.Token:
        user = service.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = dt.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = service.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return schemas.Token(access_token=access_token, token_type="bearer")  # noqa: S106

    @app.get("/users/me/", response_model=schemas.UserInDb)
    async def read_users_me(
        current_user: t.Annotated[models.User, fastapi.Depends(dependencies.get_current_active_user)],
    ) -> schemas.User:
        return current_user
