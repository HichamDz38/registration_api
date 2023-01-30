from fastapi.testclient import TestClient
import datetime
from app.main import app
import asyncio

client = TestClient(app)


def test_user_validation_wrong_url():
    async def inner():
        response = client.get("/users/validation/key135",
                              auth=("john", "secret"))
        assert response.status_code == 404

    asyncio.get_event_loop().run_until_complete(inner())


def test_add_user():
    async def inner():
        response = client.post("/users/",
                               json={
                                   "email": "sample@gmail.com",
                                   "password": "12345sfe",
                                   "first_name": "john",
                                   "last_name": "snow",
                                   "birth_date": "2023-01-26"
                               })
        assert response.status_code == 200

    asyncio.get_event_loop().run_until_complete(inner())


def test_get_user():
    async def inner():
        response = client.get("/users/sample@gmail.com")
        assert response.status_code == 200
        res = response.json()
        assert res["email"] == "sample@gmail.com"
        assert res["password"] == "12345sfe"
        assert res["first_name"] == "john"
        assert res["last_name"] == "snow"
        assert res["birth_date"] == "2023-01-26"

    asyncio.get_event_loop().run_until_complete(inner())


def test_delete_user():
    async def inner():
        response = client.delete("/users/sample@gmail.com")
        assert response.status_code == 200

    asyncio.get_event_loop().run_until_complete(inner())


def test_get_invalid_user():
    async def inner():
        response = client.get("/users/hello@yes.com")
        assert response.status_code == 404

    asyncio.get_event_loop().run_until_complete(inner())
