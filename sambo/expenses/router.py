import typing as t

import fastapi

from . import dependencies, models, schemas


def setup_routes(app: fastapi.FastAPI) -> None:
    @app.get("/users/me/expenses/created", response_model=list[schemas.Expense])
    async def created_expenses(
        my_created_expenses: t.Annotated[
            list[models.Expense],
            fastapi.Depends(dependencies.my_created_expenses),
        ],
    ) -> list[models.Expense]:
        return my_created_expenses
