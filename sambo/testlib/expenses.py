import datetime as dt

from sqlalchemy import orm

from sambo import auth, expenses


def insert_test_expenses(db: orm.Session) -> None:
    users = db.query(auth.models.User).all()
    expenses.service.create_expense(
        db=db,
        expense=expenses.schemas.ExpenseCreate(
            amount=100.3,
            text="kaffet",
            booked_time=dt.datetime.now(tz=dt.UTC),
            paid_by_id=users[0].id,
        ),
        user=users[0],
    )
