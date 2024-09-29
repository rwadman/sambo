import datetime as dt

import pydantic

import sambo.auth


class Expense(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    amount: float
    text: str
    booked_time: dt.datetime
    paid_by_id: int


class ExpenseInDB(Expense):
    id: int
    paid_by: sambo.auth.schemas.UserInDb
    created_by: sambo.auth.schemas.UserInDb
    created_by_id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted_at: dt.datetime | None


class ExpenseCreate(Expense): ...


class Participant(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    user_id: int
    default_weight: float = 1.0


class ParticipantInDb(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)
    id: int
    user: sambo.auth.schemas.UserInDb
    default_weight: float = 1.0
    created_by_id: int
    created_by: sambo.auth.schemas.UserInDb
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted_at: dt.datetime | None


class ParticipantCreate(Participant): ...


class Board(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    description: str


class BoardInDB(Board):
    id: int
    participants: list[ParticipantInDb]
    created_by: sambo.auth.schemas.UserInDb
    created_by_id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted_at: dt.datetime | None


class BoardCreate(Board):
    participants: list[ParticipantCreate] = pydantic.Field(default_factory=list)
