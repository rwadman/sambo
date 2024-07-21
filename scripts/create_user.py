#!/usr/bin/env python3.11
import getpass

import sambo.database
from sambo.auth import schemas, service


def main() -> None:
    print("Create new user.")
    email = input("Email: ")
    full_name = input("Full name: ")
    password = getpass.getpass()

    new_user = schemas.UserCreate(
        email=email,
        full_name=full_name,
        password=password,
        disabled=False,
    )
    with sambo.database.get() as db:
        created_user = service.create_user(
            db,
            new_user,
        )
        print("created user:", created_user.__dict__)


if __name__ == "__main__":
    main()
