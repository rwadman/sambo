import typing as t

import fastapi.security
import jwt
from sqlalchemy import orm

from sambo import database

from . import config, models, service


async def get_current_user(
    token: t.Annotated[str, fastapi.Depends(config.oauth2_scheme)],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_dep)],
) -> models.User:
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = service.decode_token(token)
    except jwt.InvalidTokenError as err:
        raise credentials_exception from err
    if token_data is None:
        raise credentials_exception
    user = service.get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: t.Annotated[models.User, fastapi.Depends(get_current_user)],
) -> models.User:
    if current_user.disabled:
        raise fastapi.HTTPException(status_code=400, detail="Inactive user")
    return current_user
