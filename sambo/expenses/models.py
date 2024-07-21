import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm

import sambo.auth
import sambo.database


class Expense(sambo.database.Base):
    __tablename__ = "expense"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    amount: orm.Mapped[float]
    booked_time: orm.Mapped[dt.datetime]
    paid_by_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    paid_by: orm.Mapped[sambo.auth.models.User] = orm.relationship(back_populates="expenses_paid")
    created_by_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("user.id"))
    created_by: orm.Mapped[sambo.auth.models.User] = orm.relationship(back_populates="expenses_created")
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
    deleted_at: orm.Mapped[dt.datetime | None] = orm.mapped_column(default=None)
