import datetime as dt

import sqlalchemy as sa
from sqlalchemy import orm

from sambo import database


class User(database.Base):
    __tablename__ = "user"
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    email: orm.Mapped[str]
    hashed_password: orm.Mapped[str]
    full_name: orm.Mapped[str]
    disabled: orm.Mapped[bool] = orm.mapped_column(default=False)
    created_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now())
    updated_at: orm.Mapped[dt.datetime] = orm.mapped_column(server_default=sa.func.now(), onupdate=sa.func.now())
