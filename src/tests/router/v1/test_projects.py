import pytest
from uuid import uuid4


def create_test_project():
    return {
            'name': 'test_project',
            'slug': 'test-project',
            'description': 'project_for_test',
            'status': 'draft',
            'tags': []
        }

@pytest.mark.asyncio
async def test_post_projects(client):
    response = await client.post(
        '/v1/projects/',
        json=create_test_project(),
    )
    assert response.status_code == 201

    data = response.json()
    assert data['name'] == 'test_project'
    assert data['id'] is not None


@pytest.mark.asyncio
async def test_get_projects(client):
    create_response = await client.post(
        '/v1/projects/',
        json=create_test_project()
    )
    project_id = create_response.json()['id']

    response = await client.get(f'/v1/projects/{project_id}')
    assert response.status_code == 200
    assert response.json()['id'] == project_id


@pytest.mark.asyncio
async def test_put_projects(client):
    create_response = await client.post(
        '/v1/projects/',
        json=create_test_project(),
    )
    project_id = create_response.json()['id']

    response = await client.put(
        f'/v1/projects/{project_id}',
        json={
            'name': 'updated_project',
            'description': 'updated project',
            'status': 'active',
        },
    )

    assert response.status_code == 200
    assert response.json()['name'] == 'updated_project'
    assert response.json()['status'] == 'active'


@pytest.mark.asyncio
async def test_delete_projects(client):
    create_response = await client.post(
        '/v1/projects/',
        json=create_test_project(),
    )
    project_id = create_response.json()['id']

    response = await client.delete(f'/v1/projects/{project_id}')

    assert response.status_code == 204

    get_response = await client.get(f'/v1/projects/{project_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    response = await client.get(f'/v1/projects/{uuid4()}')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_projects_pagination(client):
    for index in range(3):
        project_data = create_test_project()
        project_data['name'] = f'test_project_{index}'
        project_data['slug'] = f'test-project-{index}'
        await client.post('/v1/projects/', json=project_data)

    response = await client.get('/v1/projects/?limit=2')

    assert response.status_code == 200
    assert len(response.json()['items']) == 2
    assert response.json()['next_cursor'] is not None


@pytest.mark.asyncio
async def test_post_project_with_tags(client):
    project_data = create_test_project()
    project_data['tags'] = [
        {
            'name': 'Python',
            'slug': 'python',
            'description': 'python tag',
            'color': '#AAAAAA',
        },
    ]

    response = await client.post('/v1/projects/', json=project_data)

    assert response.status_code == 201
    assert len(response.json()['tags']) == 1
    assert response.json()['tags'][0]['slug'] == 'python'
