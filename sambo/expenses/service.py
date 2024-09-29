from sqlalchemy import orm

import sambo.auth.models
from sambo import database

from . import models, schemas


def create_expense(db: orm.Session, expense: schemas.ExpenseCreate, user: sambo.auth.models.User) -> models.Expense:
    return database.add(db, models.Expense(created_by=user, **expense.__dict__))


def create_board(db: orm.Session, board: schemas.BoardCreate, user: sambo.auth.models.User) -> models.Board:
    boarddict = board.__dict__
    boarddict["participants"] = [models.Participant(created_by=user, **p.__dict__) for p in board.participants]
    return database.add(db, models.Board(created_by=user, **boarddict))
