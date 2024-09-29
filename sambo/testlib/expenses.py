import random
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


def insert_test_expenses(db: orm.Session, n_expenses: int = 100) -> list[expenses.models.Expense]:
    users = db.query(auth.models.User).all()

    boards = board_factory(users).batch(4)
    boards = database.add_all(db, boards)

    participant_factory_ = participant_factory(users)
    participants = {
        board.id: [participant_factory_.build(board_id=board.id, user_id=u.id) for u in users[:n_participants]]
        for board, n_participants in zip(boards, [3, 2, 1, 0], strict=False)
    }

    database.add_all(db, [p for ps in participants.values() for p in ps])

    expenses = expense_factory(users, boards=boards).batch(n_expenses)
    expenses = database.add_all(db, expenses)
    insert_participations_for_expenses(db, expenses, users, participants, rng=random.Random(3))  # noqa: S311
    return expenses


def insert_participations_for_expenses(
    db: orm.Session,
    expenses: list[expenses.models.Expense],
    users: list[auth.models.User],
    participants: dict[int, list[expenses.models.Participant]],
    rng: random.Random,
) -> None:
    participations = [
        p for expense in expenses for p in make_participations_for_expense(expense, users, participants, rng)
    ]
    database.add_all(db, participations)


def make_participations_for_expense(
    expense: expenses.models.Expense,
    users: list[auth.models.User],
    participants: dict[int, list[expenses.models.Participant]],
    rng: random.Random,
) -> list[expenses.models.ExpenseParticipation]:
    if expense.board_id is None or expense.board_id not in participants or not participants[expense.board_id]:
        return []
    user_ids = [u.id for u in users]
    expense_participants = participants[expense.board_id]
    weights = [rng.uniform(0.1, 10) for _ in expense_participants]
    total_weight = sum(weights)
    amounts = [expense.amount * w / total_weight for w in weights]

    return [
        expenses.models.ExpenseParticipation(
            participant_id=participant.id,
            weight=weight,
            amount=amount,
            expense_id=expense.id,
            updated_by_id=rng.choice(user_ids),
            created_at=faker.time_in_the_past(),
            updated_at=faker.time_in_the_past(),
            deleted_at=None,
        )
        for participant, weight, amount in zip(expense_participants, weights, amounts, strict=False)
    ]
