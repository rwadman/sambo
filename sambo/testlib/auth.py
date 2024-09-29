import typing as t

import fastapi
from sqlalchemy import orm

from sambo import auth, database

USER1 = auth.schemas.UserCreate(
    email="user1@example.com",
    full_name="Anders Andersson",
    password="password1",
)
USER2 = auth.schemas.UserCreate(
    email="user2@example.com",
    full_name="Sven Svensson",
    password="password2",
)
USER3 = auth.schemas.UserCreate(
    email="user3@example.com",
    full_name="Sven Svensson2",
    password="password3",
)
TEST_USERS = [USER1, USER2, USER3]


def insert_test_users(db: orm.Session) -> None:
    for user in TEST_USERS:
        auth.service.create_user(
            db=db,
            user=user,
        )


def login_as(app: fastapi.FastAPI, user: str | auth.schemas.User) -> None:
    user_id = user.email if isinstance(user, auth.schemas.User) else user

    async def get_current_user(
        db: t.Annotated[orm.Session, fastapi.Depends(database.get_dep)],
    ) -> auth.models.User:
        result = db.query(auth.models.User).where(auth.models.User.email == user_id).first()
        assert result is not None
        return result

    app.dependency_overrides[auth.dependencies.get_current_user] = get_current_user


def db_user(db: orm.Session, user: auth.schemas.User) -> auth.models.User | None:
    return db.query(auth.models.User).where(auth.models.User.email == user.email).first()
