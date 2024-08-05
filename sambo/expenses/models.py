import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm

import sambo.auth
import sambo.database


class Expense(sambo.database.Base):
    __tablename__ = "expense"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    text: orm.Mapped[str]
    amount: orm.Mapped[float]
    booked_time: orm.Mapped[dt.datetime]
    paid_by_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    paid_by: orm.Mapped[sambo.auth.models.User] = orm.relationship(
        back_populates="expenses_paid",
        foreign_keys="Expense.paid_by_id",
    )
    created_by_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    created_by: orm.Mapped[sambo.auth.models.User] = orm.relationship(
        back_populates="expenses_created",
        foreign_keys="Expense.created_by_id",
    )
    board_id: orm.Mapped[int | None] = orm.mapped_column(sa.ForeignKey("board.id"), default=None)
    board: orm.Mapped["Board | None"] = orm.relationship(
        back_populates="expenses",
        foreign_keys="Expense.board_id",
    )
    participations: orm.Mapped[list["ExpenseParticipation"]] = orm.relationship(
        back_populates="expense",
        foreign_keys="ExpenseParticipation.expense_id",
    )
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
    deleted_at: orm.Mapped[dt.datetime | None] = orm.mapped_column(default=None)


class Board(sambo.database.Base):
    __tablename__ = "board"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    name: orm.Mapped[str]
    description: orm.Mapped[str]
    created_by_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    created_by: orm.Mapped[sambo.auth.models.User] = orm.relationship(
        back_populates="created_boards",
        foreign_keys="Board.created_by_id",
    )
    expenses: orm.Mapped[list[Expense]] = orm.relationship(back_populates="board", foreign_keys="Expense.board_id")
    participants: orm.Mapped[list["Participant"]] = orm.relationship(
        back_populates="board",
        foreign_keys="Participant.board_id",
    )
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
    deleted_at: orm.Mapped[dt.datetime | None] = orm.mapped_column(default=None)


class Participant(sambo.database.Base):
    __tablename__ = "participant"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    user: orm.Mapped[sambo.auth.models.User] = orm.relationship(
        back_populates="participations",
        foreign_keys="Participant.user_id",
    )
    board_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("board.id"))
    board: orm.Mapped[Board] = orm.relationship(back_populates="participants", foreign_keys="Participant.board_id")
    participations: orm.Mapped[list["ExpenseParticipation"]] = orm.relationship(
        back_populates="participant",
        foreign_keys="ExpenseParticipation.participant_id",
    )

    default_weight: orm.Mapped[float] = orm.mapped_column(default=1.0)
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
    deleted_at: orm.Mapped[dt.datetime | None] = orm.mapped_column(default=None)


class ExpenseParticipation(sambo.database.Base):
    __tablename__ = "expense_participation"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    participant_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("participant.id"))
    participant: orm.Mapped[Participant] = orm.relationship(
        back_populates="participations",
        foreign_keys="ExpenseParticipation.participant_id",
    )
    expense_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("expense.id"))
    expense: orm.Mapped[Expense] = orm.relationship(
        back_populates="participations",
        foreign_keys="ExpenseParticipation.expense_id",
    )
    weight: orm.Mapped[float]
    amount: orm.Mapped[float]
