from sqlalchemy import orm

from sambo import auth


def insert_test_users(db: orm.Session) -> None:
    auth.service.create_user(
        db=db,
        user=auth.schemas.UserCreate(
            email="user1@example.com",
            full_name="Anders Andersson",
            password="password1",  # noqa: S106
        ),
    )
    auth.service.create_user(
        db=db,
        user=auth.schemas.UserCreate(
            email="user2@example.com",
            full_name="Sven Svensson",
            password="password2",  # noqa: S106
        ),
    )
