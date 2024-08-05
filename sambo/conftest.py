import pathlib

import fastapi
import fastapi.testclient
import pytest
import sqlalchemy as sa

from . import database, main, testlib


@pytest.fixture
def db(tmp_path: pathlib.Path) -> sa.Engine:
    return testlib.db.setup_test_db(tmp_path)


@pytest.fixture
def app(db: sa.Engine) -> fastapi.FastAPI:
    app_ = main.app
    app_.dependency_overrides[database.get_dep] = testlib.db.override_get_dep(db)

    return app_


@pytest.fixture
def client(app: fastapi.FastAPI) -> fastapi.testclient.TestClient:
    return fastapi.testclient.TestClient(app)
