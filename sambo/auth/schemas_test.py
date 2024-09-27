import pytest

import sambo.testlib.pytest

from . import schemas


@pytest.mark.parametrize(
    ("email", "password", "should_raise"),
    [
        ("invalid-email", "aVeryG00dPassword.", True),
        ("a-valid@email.com", "aVeryG00dPassword.", False),
        ("a-valid@email.com", "pwd", True),
    ],
)
def test_user_create(email: str, password: str, should_raise: bool) -> None:
    with sambo.testlib.pytest.raises_if(ValueError, should_raise=should_raise):
        schemas.UserCreate(email=email, full_name="a name", disabled=False, password=password)
