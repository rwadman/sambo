import contextlib
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
def get_dep() -> t.Generator[orm.Session, None, None]:
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        db_.close()


get = contextlib.contextmanager(get_dep)


class Base(orm.DeclarativeBase): ...


ModelT = t.TypeVar("ModelT", bound=Base)
ModelsT = t.TypeVar("ModelsT", bound=t.Collection[Base])


def add(db: orm.Session, item: ModelT) -> ModelT:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def add_all(db: orm.Session, items: ModelsT) -> ModelsT:
    db.add_all(items)
    db.commit()
    for item in items:
        db.refresh(item)
    return items
