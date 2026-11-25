import pytest
from uuid import uuid4


def create_test_user():
    return {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'access_granted': [],
    }


def create_test_access():
    return {
        'resource': 'reports',
        'scope': ['access', 'export'],
        'status': 'active',
    }


@pytest.mark.asyncio
async def test_post_users(client):
    response = await client.post(
        '/v1/users/',
        json=create_test_user(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data['id'] is not None
    assert data['username'] == 'test_user'
    assert data['access_granted'] == []


@pytest.mark.asyncio
async def test_post_user_with_access_grants(client):
    user_data = create_test_user()
    user_data['access_granted'] = [create_test_access()]

    response = await client.post('/v1/users/', json=user_data)

    assert response.status_code == 201
    assert response.json()['access_granted'][0]['resource'] == 'reports'


@pytest.mark.asyncio
async def test_get_users(client):
    create_response = await client.post(
        '/v1/users/',
        json=create_test_user(),
    )
    user_id = create_response.json()['id']

    response = await client.get(f'/v1/users/{user_id}')

    assert response.status_code == 200
    assert response.json()['id'] == user_id


@pytest.mark.asyncio
async def test_put_users(client):
    create_response = await client.post(
        '/v1/users/',
        json=create_test_user(),
    )
    user_id = create_response.json()['id']

    response = await client.put(
        f'/v1/users/{user_id}',
        json={
            'username': 'updated_user',
            'email': 'updated_user@example.com',
            'access_granted_to_add': [create_test_access()],
        },
    )

    assert response.status_code == 200
    assert response.json()['username'] == 'updated_user'
    assert response.json()['email'] == 'updated_user@example.com'


@pytest.mark.asyncio
async def test_delete_users(client):
    create_response = await client.post(
        '/v1/users/',
        json=create_test_user(),
    )
    user_id = create_response.json()['id']

    response = await client.delete(f'/v1/users/{user_id}')

    assert response.status_code == 204

    get_response = await client.get(f'/v1/users/{user_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get(f'/v1/users/{uuid4()}')

    assert response.status_code == 404
