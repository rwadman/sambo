from sqlalchemy import orm

import sambo.auth.models
from sambo import database

from . import models, schemas


def create_expense(db: orm.Session, expense: schemas.ExpenseCreate, user: sambo.auth.models.User) -> models.Expense:
    return database.add(db, models.Expense(created_by=user, **expense.__dict__))
