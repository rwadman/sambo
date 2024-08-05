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
