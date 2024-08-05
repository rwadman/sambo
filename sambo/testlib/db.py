import pathlib
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from sambo import database

from . import auth


def override_get_dep(engine: sa.Engine) -> t.Callable[[], t.Generator[orm.Session, None, None]]:
    def get_dep() -> t.Generator[orm.Session, None, None]:
        db_ = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)()
        try:
            yield db_
        finally:
            db_.close()

    return get_dep


def setup_test_db(folder: pathlib.Path) -> sa.Engine:
    engine = sa.create_engine(f"sqlite:///{folder}/testdata.db")
    database.Base.metadata.create_all(engine)
    db = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    auth.insert_test_users(db)

    return engine
