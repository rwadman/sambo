import contextlib
import typing as t

import pytest


@contextlib.contextmanager
def raises_if(error: type, should_raise: bool) -> t.Generator[None, None, None]:
    if should_raise:
        with pytest.raises(error):
            yield
    else:
        yield
