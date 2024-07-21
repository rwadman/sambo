import datetime as dt

import pydantic

import sambo.auth


class Expense(pydantic.BaseModel):
    id: int
    amount: float
    booked_time: dt.datetime
    paid_by: sambo.auth.schemas.User
    created_by_id: int
    created_by: sambo.auth.schemas.User
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted_at: dt.datetime | None

    class Config:
        from_attributes = True
