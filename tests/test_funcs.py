from fastapi.testclient import TestClient
import datetime
from app.funcs import generate_url, generate_key
from string import ascii_letters

import asyncio


def test_generate_url():
    async def inner():
        url = generate_url()
        assert len(url) == 20
        assert all([d not in url for d in "0123456789-+*/!£$%^&*()_+-="])

    asyncio.get_event_loop().run_until_complete(inner())


def test_generate_key():
    async def inner():
        pin_code = generate_key()
        assert len(pin_code) == 4
        assert all([c not in pin_code for c in ascii_letters])

    asyncio.get_event_loop().run_until_complete(inner())


