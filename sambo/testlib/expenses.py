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
    boards: t.Collection[expenses.models.Board],
) -> type[sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Expense]]:
    user_ids = [u.id for u in users]
    board_ids = [b.id for b in boards]

    class ExpenseFactory(sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Expense]):
        __random_seed__ = 3
        __set_primary_key__ = False
        booked_time = polyfactory.Use(faker.time_in_the_past)
        board_id = polyfactory.Use(
            sqlalchemy_factory.SQLAlchemyFactory.__random__.choice,
            board_ids,
        )
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


def participant_factory(
    users: t.Collection[auth.models.User],
) -> type[sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Participant]]:
    user_ids = [u.id for u in users]

    class ParticipantFactory(sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Participant]):
        __random_seed__ = 3
        __set_primary_key__ = False
        default_weight = polyfactory.Use(sqlalchemy_factory.SQLAlchemyFactory.__random__.uniform, 0.1, 10)
        created_by_id = polyfactory.Use(sqlalchemy_factory.SQLAlchemyFactory.__random__.choice, user_ids)
        created_at = polyfactory.Use(faker.time_in_the_past)
        updated_at = polyfactory.Use(faker.time_in_the_past)
        deleted_at = polyfactory.Use(faker.maybe(faker.time_in_the_past, chance_of_getting_none=0.1))

    return ParticipantFactory


def board_factory(
    users: t.Collection[auth.models.User],
) -> type[sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Board]]:
    user_ids = [u.id for u in users]

    class BoardFactory(sqlalchemy_factory.SQLAlchemyFactory[expenses.models.Board]):
        __random_seed__ = 3
        __set_primary_key__ = False
        created_by_id = polyfactory.Use(
            sqlalchemy_factory.SQLAlchemyFactory.__random__.choice,
            user_ids,
        )
        created_at = polyfactory.Use(faker.time_in_the_past)
        updated_at = polyfactory.Use(faker.time_in_the_past)
        deleted_at = polyfactory.Use(faker.maybe(faker.time_in_the_past, chance_of_getting_none=0.1))

    return BoardFactory


def insert_test_expenses(db: orm.Session, n_expenses: int = 30) -> list[expenses.models.Expense]:
    users = db.query(auth.models.User).all()

    boards = board_factory(users).batch(4)
    boards = database.add_all(db, boards)

    participant_factory_ = participant_factory(users)
    participants = [
        participant_factory_.build(board_id=board.id, user_id=u.id)
        for board, n_participants in zip(boards, [3, 2, 1, 0], strict=False)
        for u in users[:n_participants]
    ]
    database.add_all(db, participants)

    expenses = expense_factory(users, boards=boards).batch(n_expenses)
    return database.add_all(db, expenses)
