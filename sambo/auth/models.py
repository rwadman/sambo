import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm

import sambo.database


class User(sambo.database.Base):
    __tablename__ = "user"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    email: orm.Mapped[str]
    hashed_password: orm.Mapped[bytes]
    full_name: orm.Mapped[str]
    disabled: orm.Mapped[bool] = orm.mapped_column(default=False)
    expenses_paid: orm.Mapped[list["sambo.expenses.models.Expense"]] = orm.relationship(
        back_populates="paid_by",
        foreign_keys="sambo.expenses.models.Expense.paid_by_id",
    )
    expenses_created: orm.Mapped[list["sambo.expenses.models.Expense"]] = orm.relationship(
        back_populates="created_by",
        foreign_keys="sambo.expenses.models.Expense.created_by_id",
    )
    participations: orm.Mapped[list["sambo.expenses.models.Participant"]] = orm.relationship(
        back_populates="user",
        foreign_keys="sambo.expenses.models.Participant.user_id",
    )
    created_boards: orm.Mapped[list["sambo.expenses.models.Board"]] = orm.relationship(
        back_populates="created_by",
        foreign_keys="sambo.expenses.models.Board.created_by_id",
    )
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
