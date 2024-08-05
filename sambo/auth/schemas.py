import typing as t

import pydantic

from . import config


class User(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    email: str
    full_name: str
    disabled: bool = False


class UserInDb(User):
    id: int


def check_pass_complexity(pw: str) -> str:
    if len(pw) < config.PASSWORD_MIN_LENGTH:
        msg = "Choose a better password (must have length > 6)"
        raise ValueError(msg)
    return pw


class UserCreate(User):
    password: t.Annotated[str, pydantic.AfterValidator(check_pass_complexity)]

    @pydantic.field_validator("email")
    @staticmethod
    def email_must_contain_at(v: str) -> str:
        if "@" not in v:
            msg = "must contain '@'"
            raise ValueError(msg)
        return v


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    email: str
