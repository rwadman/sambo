import typing as t

import polyfactory
import polyfactory.factories
import polyfactory.factories.sqlalchemy_factory
from polyfactory.factories import pydantic_factory, sqlalchemy_factory
from sqlalchemy import orm

from sambo import auth, database, expenses

from . import faker


class ExpenseCreateFactory(pydantic_factory.ModelFactory[expenses.schemas.ExpenseCreate]):
    booked_time = polyfactory.Use(faker.time_in_the_past)


def expense_factory(
    users: t.Collection[auth.models.User],
) -> type[sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Expense]]:
    user_ids = [u.id for u in users]

    class ExpenseFactory(sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Expense]):
        __random_seed__ = 3
        __set_primary_key__ = False
        booked_time = polyfactory.Use(faker.time_in_the_past)
        board_id = polyfactory.Use(lambda: None)
        created_by_id = polyfactory.Use(
            sqlalchemy_factory.SQLAlchemyFactory.__random__.choice,
            user_ids,
        )
        paid_by_id = polyfactory.Use(
            sqlalchemy_factory.SQLAlchemyFactory.__random__.choice,
            user_ids,
        )
        created_at = polyfactory.Use(faker.time_in_the_past)
        updated_at = polyfactory.Use(faker.time_in_the_past)
        deleted_at = polyfactory.Use(faker.maybe(faker.time_in_the_past, chance_of_getting_none=0.1))

    return ExpenseFactory


def insert_test_expenses(db: orm.Session, n_expenses: int = 30) -> list[expenses.models.Expense]:
    users = db.query(auth.models.User).all()
    factory = expense_factory(users)
    expenses = factory.batch(n_expenses)
    return database.add_all(db, expenses)
