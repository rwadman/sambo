import pathlib
import typing as t

import fastapi
import fastapi.testclient
import pytest
import sqlalchemy as sa
from sqlalchemy import orm

from . import database, main, testlib


@pytest.fixture
def db_engine(tmp_path: pathlib.Path) -> sa.Engine:
    return testlib.db.setup_test_db(tmp_path)


@pytest.fixture
def db(db_engine: sa.Engine) -> t.Generator[orm.Session, None, None]:
    db_ = orm.sessionmaker(autocommit=False, autoflush=False, bind=db_engine)()
    try:
        yield db_
    finally:
        db_.close()


@pytest.fixture
def app(db_engine: sa.Engine) -> t.Generator[fastapi.FastAPI, None, None]:
    main.app.dependency_overrides[database.get_dep] = testlib.db.override_get_dep(db_engine)
    try:
        yield main.app
    finally:
        main.app.dependency_overrides = {}


@pytest.fixture
def client(app: fastapi.FastAPI) -> fastapi.testclient.TestClient:
    return fastapi.testclient.TestClient(app)
