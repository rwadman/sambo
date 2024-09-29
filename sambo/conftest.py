import pathlib
import shutil
import typing as t

import fastapi
import fastapi.testclient
import pytest
import sqlalchemy as sa
from sqlalchemy import orm

from . import database, main, testlib


@pytest.fixture(scope="session")
def test_db_dont_mutate(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    test_db_dir = tmp_path_factory.mktemp("testdb")
    return testlib.db.setup_test_db(test_db_dir)


@pytest.fixture
def db_engine(tmp_path: pathlib.Path, test_db_dont_mutate: pathlib.Path) -> sa.Engine:
    path = shutil.copyfile(test_db_dont_mutate, tmp_path / "testdata.db")
    return sa.create_engine(f"sqlite:///{path}")


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
