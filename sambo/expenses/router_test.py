import http
import typing as t

import fastapi
import fastapi.testclient
import pytest
from sqlalchemy import orm

import sambo
import sambo.testlib

from . import models


def test_get_my_created_expenses(app: fastapi.FastAPI, db: orm.Session, client: fastapi.testclient.TestClient) -> None:
    user = sambo.testlib.USER1
    sambo.testlib.auth.login_as(app=app, user=user)
    db_user = sambo.testlib.auth.db_user(db, user)
    assert db_user is not None

    expected_expenses = db.query(models.Expense).where(models.Expense.created_by_id == db_user.id).all()

    result = client.get("/users/me/expenses/created")

    assert result.is_success
    data: list[dict[str, t.Any]] = result.json()
    assert len(data) == len(expected_expenses)
    data = sorted(data, key=lambda exp: exp["id"])
    expected_expenses = sorted(expected_expenses, key=lambda exp: exp.id)

    for actual, expected in zip(data, expected_expenses, strict=False):
        assert actual["id"] == expected.id
        assert actual["amount"] == pytest.approx(expected.amount)
        assert actual["text"] == expected.text
        assert actual["created_by_id"] == db_user.id
        assert actual["created_by"]["email"] == db_user.email
        assert actual["paid_by_id"] == expected.paid_by_id
        assert actual["paid_by"]["email"] == expected.paid_by.email


@pytest.mark.parametrize(
    "create_expense",
    [
        {},
        {"amount": 10.15},
        {"paid_by_id": 1},
        {"amount": 10.15, "paid_by_id": 1},
        {"amount": 10.15, "paid_by_id": 1, "text": "hello"},
    ],
)
def test_post_expense_fails_for_incomplete_input(
    app: fastapi.FastAPI,
    client: fastapi.testclient.TestClient,
    create_expense: dict[str, t.Any],
) -> None:
    user = sambo.testlib.USER1
    sambo.testlib.auth.login_as(app=app, user=user)
    result = client.post("/expense", json=create_expense)
    assert result.is_error
    assert result.is_client_error
    assert result.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "create_expense",
    [
        {"amount": 10.15, "paid_by_id": 2, "text": "hello", "booked_time": "2023-10-22 10:00"},
    ],
)
def test_post_expense_succeeds_for_valid_input(
    app: fastapi.FastAPI,
    client: fastapi.testclient.TestClient,
    create_expense: dict[str, t.Any],
) -> None:
    user = sambo.testlib.USER1
    sambo.testlib.auth.login_as(app=app, user=user)
    result = client.post("/expense", json=create_expense)

    assert result.is_success
    created = result.json()
    assert created["amount"] == create_expense["amount"]
    assert created["created_by"]["email"] == user.email
    assert created["text"] == create_expense["text"]
    assert created["paid_by_id"] == create_expense["paid_by_id"]


@pytest.mark.parametrize(
    "create_board",
    [
        {},
        {"description": "hello"},
        {
            "name": "board1",
            "description": "a board",
            "participants": [{"user_id": 1, "weight": 2}, {"user_id": 1, "weight": 1}],
        },
    ],
)
def test_post_board_fails_for_incomplete_or_invalid_input(
    app: fastapi.FastAPI,
    client: fastapi.testclient.TestClient,
    create_board: dict[str, t.Any],
) -> None:
    user = sambo.testlib.USER1
    sambo.testlib.auth.login_as(app=app, user=user)
    result = client.post("/board", json=create_board)
    assert result.is_error
    assert result.is_client_error
    assert result.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "create_board",
    [
        {"name": "board1", "description": "a board"},
        {
            "name": "board1",
            "description": "a board",
            "participants": [{"user_id": 1, "weight": 2}, {"user_id": 2, "weight": 1}],
        },
    ],
)
def test_post_board_succeeds_for_valid_input(
    app: fastapi.FastAPI,
    client: fastapi.testclient.TestClient,
    create_board: dict[str, t.Any],
) -> None:
    user = sambo.testlib.USER1
    sambo.testlib.auth.login_as(app=app, user=user)
    result = client.post("/board", json=create_board)

    assert result.is_success
    created = result.json()
    assert created["name"] == create_board["name"]
    assert created["description"] == create_board["description"]
    assert created["created_by"]["email"] == user.email
    assert len(created["participants"]) == len(create_board.get("participants", []))


@pytest.mark.parametrize(
    "user",
    sambo.testlib.TEST_USERS,
)
def test_get_boards_lists_all_participatory_boards(
    app: fastapi.FastAPI,
    db: orm.Session,
    client: fastapi.testclient.TestClient,
    user: sambo.auth.schemas.User,
) -> None:
    sambo.testlib.auth.login_as(app=app, user=user)
    db_user = sambo.testlib.auth.db_user(db, user)
    assert db_user is not None

    result = client.get("/board")
    assert result.is_success
    data = result.json()

    expected_boards = (
        db.query(models.Board).join(models.Participant.board).where(models.Participant.user_id == db_user.id).all()
    )

    assert len(data) == len(expected_boards)
