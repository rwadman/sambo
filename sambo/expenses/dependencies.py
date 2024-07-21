import typing as t

import fastapi

import sambo.auth

from . import models


async def my_created_expenses(
    user: t.Annotated[sambo.auth.models.User, fastapi.Depends(sambo.auth.dependencies.get_current_active_user)],
) -> list[models.Expense]:
    return user.expenses_created


async def my_paid_expenses(
    user: t.Annotated[sambo.auth.models.User, fastapi.Depends(sambo.auth.dependencies.get_current_active_user)],
) -> list[models.Expense]:
    return user.expenses_paid
