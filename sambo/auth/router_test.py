import fastapi
import fastapi.testclient
import pytest

import sambo.testlib.auth


@pytest.mark.parametrize(
    ("username", "password", "is_valid"),
    [
        ("not a user", "password1", False),
        ("user1@example.com", "password1", True),
        ("user2@example.com", "password1", False),
    ],
)
def test_login(client: fastapi.testclient.TestClient, username: str, password: str, is_valid: bool) -> None:
    response = client.post("/token", data={"username": username, "password": password})
    if is_valid:
        assert response.is_success
        json = response.json()
        assert "access_token" in json
        assert "token_type" in json
        assert json["token_type"] == "bearer"
    else:
        assert response.is_error
        assert response.status_code == fastapi.status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "username",
    [
        sambo.testlib.USER1.email,
        None,
    ],
)
def test_get_me(username: str | None, app: fastapi.FastAPI, client: fastapi.testclient.TestClient) -> None:
    if username:
        sambo.testlib.auth.login_as(app=app, user=username)

    result = client.get("/users/me")
    if username:
        assert result.is_success
        json = result.json()
        assert json["email"] == username
    else:
        assert result.is_error
