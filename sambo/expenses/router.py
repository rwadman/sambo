import typing as t

import fastapi
from sqlalchemy import orm

import sambo.auth

from . import dependencies, models, schemas, service


def setup_routes(app: fastapi.FastAPI) -> None:
    @app.get("/users/me/expenses/created", response_model=list[schemas.ExpenseInDB])
    async def created_expenses(
        my_created_expenses: t.Annotated[
            list[models.Expense],
            fastapi.Depends(dependencies.my_created_expenses),
        ],
    ) -> list[models.Expense]:
        return my_created_expenses

    @app.post("/expense", response_model=schemas.ExpenseInDB)
    async def create_expense(
        expense: schemas.ExpenseCreate,
        me: t.Annotated[
            sambo.auth.models.User,
            fastapi.Depends(sambo.auth.dependencies.get_current_active_user),
        ],
        db: t.Annotated[orm.Session, fastapi.Depends(sambo.database.get_dep)],
    ) -> models.Expense:
        if sambo.auth.service.get_user(db, id_=expense.paid_by_id, require_active=True) is None:
            raise fastapi.exceptions.RequestValidationError(
                [
                    {
                        "type": "entity_not_found",
                        "loc": ["body", "paid_by_id"],
                        "msg": "Could not find active user with requested id",
                        "input": expense.paid_by_id,
                    },
                ],
            )

        return service.create_expense(db, expense, me)

    @app.post("/board", response_model=schemas.BoardInDB)
    async def create_board(
        board: schemas.BoardCreate,
        me: t.Annotated[
            sambo.auth.models.User,
            fastapi.Depends(sambo.auth.dependencies.get_current_active_user),
        ],
        db: t.Annotated[orm.Session, fastapi.Depends(sambo.database.get_dep)],
    ) -> models.Board:
        has_duplicate_participants = len({p.user_id for p in board.participants}) != len(board.participants)
        if has_duplicate_participants:
            raise fastapi.exceptions.RequestValidationError(
                [
                    {
                        "type": "duplicate_entity",
                        "loc": ["body", "participants"],
                        "msg": "Duplicate participant: you can only enter a user into a board once",
                        "input": board.participants,
                    },
                ],
            )

        nonexisting_participants = [
            p.user_id
            for p in board.participants
            if sambo.auth.service.get_user(db, id_=p.user_id, require_active=True) is None
        ]

        if nonexisting_participants:
            raise fastapi.exceptions.RequestValidationError(
                [
                    {
                        "type": "entity_not_found",
                        "loc": ["body", "participants"],
                        "msg": "Could not find active users with requested ids",
                        "input": nonexisting_participants,
                    },
                ],
            )

        return service.create_board(db, board, me)

    @app.get("/board", response_model=list[schemas.BoardInDB])
    async def boards(
        my_boards: t.Annotated[
            list[models.Board],
            fastapi.Depends(dependencies.my_boards),
        ],
    ) -> list[models.Board]:
        return my_boards
