import os
import typing as t

import dotenv
import sqlalchemy as sa
from sqlalchemy import orm

dotenv.load_dotenv()

SQL_ALCHEMY_URI = os.environ["APP_SQL_ALCHEMY_URI"]

engine = sa.create_engine(SQL_ALCHEMY_URI, connect_args={"check_same_thread": False})
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get() -> t.Generator[orm.Session, None, None]:
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        db_.close()


class Base(orm.DeclarativeBase): ...
