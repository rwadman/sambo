import datetime
import typing as t

import faker

fake = faker.Faker()


def time_between(start_dt: str, end_dt: str) -> datetime.datetime:
    time: datetime.datetime = fake.date_time_between(start_date=start_dt, end_date=end_dt, tzinfo=datetime.UTC)
    return time.replace(microsecond=0)


def time_in_the_past() -> datetime.datetime:
    return time_between(start_dt="-2y", end_dt="-1s")


T = t.TypeVar("T")


def maybe(generator: t.Callable[[], T], chance_of_getting_none: float = 0.5) -> t.Callable[[], T | None]:
    def generate() -> T | None:
        if fake.boolean(chance_of_getting_true=round(chance_of_getting_none * 100)):
            return None
        return generator()

    return generate
