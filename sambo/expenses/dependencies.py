import typing as t

import fastapi
from sqlalchemy import orm

import sambo.auth
import sambo.database

from . import models


async def my_created_expenses(
    user: t.Annotated[sambo.auth.models.User, fastapi.Depends(sambo.auth.dependencies.get_current_active_user)],
) -> list[models.Expense]:
    return user.expenses_created


async def my_paid_expenses(
    user: t.Annotated[sambo.auth.models.User, fastapi.Depends(sambo.auth.dependencies.get_current_active_user)],
) -> list[models.Expense]:
    return user.expenses_paid


async def my_boards(
    user: t.Annotated[sambo.auth.models.User, fastapi.Depends(sambo.auth.dependencies.get_current_active_user)],
    db: t.Annotated[orm.Session, fastapi.Depends(sambo.database.get_dep)],
) -> list[models.Board]:
    return db.query(models.Board).join(models.Participant.board).where(models.Participant.user_id == user.id).all()
