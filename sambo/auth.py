import datetime as dt
import os
import typing as t

import dotenv
import fastapi
import fastapi.security
import jwt
import passlib.context
import pydantic
from sqlalchemy import orm

from . import crud, database, models

dotenv.load_dotenv()


SECRET_KEY = os.environ["APP_SECRET_KEY"]
ALGORITHM = os.environ["APP_HASH_ALGORITHM"]

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserDict(t.TypedDict):
    username: str
    full_name: str
    email: str
    hashed_password: str
    disabled: bool


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    email: str | None = None


class User(pydantic.BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, db: orm.Session) -> models.User | None:
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def _create_access_token(data: dict, expires_delta: dt.timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = (
        dt.datetime.now(dt.UTC) + expires_delta if expires_delta else dt.datetime.now(dt.UTC) + dt.timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: t.Annotated[str, fastapi.Depends(oauth2_scheme)],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get)],
) -> models.User:
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError as err:
        raise credentials_exception from err
    if token_data.email is None:
        raise credentials_exception
    user = crud.get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: t.Annotated[User, fastapi.Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise fastapi.HTTPException(status_code=400, detail="Inactive user")
    return current_user


def setup_routes(app: fastapi.FastAPI) -> None:
    @app.post("/token")
    async def login_for_access_token(
        form_data: t.Annotated[fastapi.security.OAuth2PasswordRequestForm, fastapi.Depends()],
        db: t.Annotated[orm.Session, fastapi.Depends(database.get)],
    ) -> Token:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = _create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return Token(access_token=access_token, token_type="bearer")  # noqa: S106
