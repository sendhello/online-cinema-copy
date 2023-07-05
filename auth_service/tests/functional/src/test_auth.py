import asyncio

import pytest
from tests.functional.settings import test_settings  # noqa
from tests.functional.testdata.data import USER
from tests.functional.utils import generate_tokens, get_headers, redis_flush

loop = asyncio.get_event_loop()


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (
            USER,
            201,
            {
                'id': '345fa6c5-c138-4f5c-bce5-a35b0f26fced',
                'login': 'test',
                'first_name': 'Тест',
                'last_name': 'Тестов',
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_user(client, mock_redis, user, status_code, result):
    response = client.post('api/v1/auth/signup', json=user)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    'login_data, status_code, result_keys',
    [
        # Ок
        (
            {'login': USER['login'], 'password': USER['password']},
            200,
            ['access_token', 'refresh_token'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_login(client, mock_redis, login_data, status_code, result_keys):
    response = client.post("api/v1/auth/login", json=login_data)
    assert response.status_code == status_code
    data = response.json()
    assert list(data.keys()) == result_keys

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    'user, status_code, result_keys',
    [
        # Ок
        (USER, 200, ['access_token', 'refresh_token']),
    ],
)
@pytest.mark.asyncio
async def test_refresh(client, mock_redis, user, status_code, result_keys):
    tokens = await generate_tokens(user)
    refresh_token = tokens['refresh_token']
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("api/v1/auth/refresh", headers=headers)
    assert response.status_code == status_code
    data = response.json()
    assert list(data.keys()) == result_keys

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    'user, status_code, result',
    [
        # Ок
        (USER, 200, {}),
    ],
)
@pytest.mark.asyncio
async def test_logout(client, mock_redis, user, status_code, result):
    response = client.post("api/v1/auth/logout", headers=await get_headers(user))
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)
