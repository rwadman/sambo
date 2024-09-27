import typing as t

import fastapi
from sqlalchemy import orm

from sambo import auth, database


def insert_test_users(db: orm.Session) -> None:
    auth.service.create_user(
        db=db,
        user=auth.schemas.UserCreate(
            email="user1@example.com",
            full_name="Anders Andersson",
            password="password1",
        ),
    )
    auth.service.create_user(
        db=db,
        user=auth.schemas.UserCreate(
            email="user2@example.com",
            full_name="Sven Svensson",
            password="password2",
        ),
    )


def login_as(app: fastapi.FastAPI, user_id: str) -> None:
    async def get_current_user(
        db: t.Annotated[orm.Session, fastapi.Depends(database.get_dep)],
    ) -> auth.models.User:
        result = db.query(auth.models.User).where(auth.models.User.email == user_id).first()
        assert result is not None
        return result

    app.dependency_overrides[auth.dependencies.get_current_user] = get_current_user
