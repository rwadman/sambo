import datetime as dt

import jwt
import passlib.context
from sqlalchemy import orm

from . import config, models, schemas

pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, db: orm.Session) -> models.User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: dt.timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = (
        dt.datetime.now(dt.UTC) + expires_delta if expires_delta else dt.datetime.now(dt.UTC) + dt.timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decode_token(token: str) -> schemas.TokenData | None:
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    email: str | None = payload.get("sub")
    if email is None:
        return None
    return schemas.TokenData(email=email)


def get_user(db: orm.Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: orm.Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: orm.Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: orm.Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
