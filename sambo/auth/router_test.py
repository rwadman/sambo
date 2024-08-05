import fastapi.testclient
import pytest


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
    else:
        assert response.is_error
        assert response.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
