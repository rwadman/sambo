import os

import dotenv
import sqlalchemy as sa
from sqlalchemy import orm

dotenv.load_dotenv()

SQL_ALCHEMY_URI = os.environ["APP_SQL_ALCHEMY_URI"]

engine = sa.create_engine(SQL_ALCHEMY_URI, connect_args={"check_same_thread": False})
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(orm.DeclarativeBase): ...
