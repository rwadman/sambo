import datetime as dt

import pydantic

import sambo.auth


class Expense(pydantic.BaseModel):
    amount: float
    text: str
    booked_time: dt.datetime
    paid_by_id: int

    class Config:
        from_attributes = True


class ExpenseInDB(Expense):
    id: int
    paid_by: sambo.auth.schemas.User
    created_by: sambo.auth.schemas.User
    created_by_id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted_at: dt.datetime | None


class ExpenseCreate(Expense): ...
