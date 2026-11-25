import pytest
from uuid import uuid4


def create_test_workspace():
    return {
        'name': 'test workspace',
        'slug': 'test-workspace',
        'description': 'workspace for api test',
        'status': 'active',
        'workspace_settings': {
            'timezone': 'UTC',
            'language': 'ru',
            'notifications_enabled': True,
        },
    }


@pytest.mark.asyncio
async def test_post_workspaces(client):
    response = await client.post(
        '/v1/workspaces/',
        json=create_test_workspace(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data['id'] is not None
    assert data['name'] == 'test workspace'
    assert data['workspace_settings']['timezone'] == 'UTC'


@pytest.mark.asyncio
async def test_get_workspaces(client):
    create_response = await client.post(
        '/v1/workspaces/',
        json=create_test_workspace(),
    )
    workspace_id = create_response.json()['id']

    response = await client.get(f'/v1/workspaces/{workspace_id}')

    assert response.status_code == 200
    assert response.json()['id'] == workspace_id
    assert response.json()['workspace_settings']['language'] == 'ru'


@pytest.mark.asyncio
async def test_put_workspaces(client):
    create_response = await client.post(
        '/v1/workspaces/',
        json=create_test_workspace(),
    )
    workspace_id = create_response.json()['id']

    response = await client.put(
        f'/v1/workspaces/{workspace_id}',
        json={
            'name': 'updated workspace',
            'workspace_settings': {
                'timezone': 'Asia/Novosibirsk',
                'language': 'en',
                'notifications_enabled': False,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['name'] == 'updated workspace'
    assert response.json()['workspace_settings']['timezone'] == 'Asia/Novosibirsk'
    assert response.json()['workspace_settings']['language'] == 'en'
    assert response.json()['workspace_settings']['notifications_enabled'] is False


@pytest.mark.asyncio
async def test_delete_workspaces(client):
    create_response = await client.post(
        '/v1/workspaces/',
        json=create_test_workspace(),
    )
    workspace_id = create_response.json()['id']

    response = await client.delete(f'/v1/workspaces/{workspace_id}')

    assert response.status_code == 204

    get_response = await client.get(f'/v1/workspaces/{workspace_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_workspace_not_found(client):
    response = await client.get(f'/v1/workspaces/{uuid4()}')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_workspaces_pagination(client):
    for index in range(3):
        workspace_data = create_test_workspace()
        workspace_data['name'] = f'test workspace {index}'
        workspace_data['slug'] = f'test-workspace-{index}'

        await client.post('/v1/workspaces/', json=workspace_data)

    response = await client.get('/v1/workspaces/?limit=2')

    assert response.status_code == 200
    assert len(response.json()['items']) == 2
    assert response.json()['next_cursor'] is not None


@pytest.mark.asyncio
async def test_post_workspace_with_invalid_timezone(client):
    workspace_data = create_test_workspace()
    workspace_data['workspace_settings']['timezone'] = 'Invalid/Timezone'

    response = await client.post(
        '/v1/workspaces/',
        json=workspace_data,
    )

    assert response.status_code == 422
