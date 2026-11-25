import pytest
import pytest_asyncio
from uuid import uuid4

from src.services.project_service import ProjectService
from src.UoW.project_UoW import ProjectUoW
from src.repositories.project_repository import ProjectRepository
from src.mappers.project_mapper import ProjectMapper
from src.schemas.project import ProjectCreate, ProjectStatus, ProjectUpdate, ProjectResponse
from src.schemas.tag import TagCreate
from src.exceptions.general_errors import NotFoundError


async def create_projects(
        project_service: ProjectService,
        count: int = 5,
):
    projects = []
    test_id = uuid4().hex

    for index in range(count):
        project_data = ProjectCreate(
            name=f'test_project_{test_id}_{index}',
            slug=f'test-project-{test_id}-{index}',
            description=f'Description {index}',
            status=ProjectStatus.COMPLETED,
        )
        project = await project_service.create_project(project_data)
        projects.append(project)

    return projects


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def project_service(session_factory, redis_cache) -> ProjectService:
    unit_of_work = ProjectUoW(session_factory)
    mapper = ProjectMapper()
    project_service = ProjectService(unit_of_work, mapper, redis_cache)

    return project_service


@pytest.mark.asyncio
async def test_get_project_by_id(
        async_session,
        redis_cache,
        project_service,
):
    project_repository = ProjectRepository(async_session)

    test_project_create_schema = ProjectCreate(
        name='test_project',
        slug='test-project',
        description='just a test project',
        status=ProjectStatus.COMPLETED
    )
    test_project = await project_service.create_project(test_project_create_schema)
    test_project_get = await project_service.get_project_by_id(test_project.id)
    assert test_project_get == test_project

    cached_value = await redis_cache.redis_client.get(
        ProjectService.project_key(test_project.id)
    )
    assert cached_value is not None

    project_model = await project_repository.get_project_by_id(test_project.id)
    assert project_model is not None

    await project_repository.delete_project(project_model)
    second_response = await project_service.get_project_by_id(test_project.id)
    assert second_response == test_project_get


@pytest.mark.asyncio
async def test_project_not_found(project_service):
    with pytest.raises(NotFoundError):
        await project_service.get_project_by_id(uuid4())


@pytest.mark.asyncio
async def test_pagination_cache_miss(project_service, redis_cache):
    projects = await create_projects(project_service)

    cache_version = await redis_cache.get(ProjectService.PROJECTS_LIST_VERSION_KEY)
    assert cache_version is not None

    cache_key = ProjectService.project_list_version(
        int(cache_version),
        limit=2,
        cursor=None,
    )
    assert await redis_cache.get(cache_key) is None

    pagination_response = await project_service.list_projects(
        limit=2,
        cursor=None,
    )

    assert len(pagination_response.items) == 2
    assert pagination_response.next_cursor is not None
    project_ids = {project.id for project in projects}
    assert all(
        item.id in project_ids
        for item in pagination_response.items
    )
    assert await redis_cache.get(cache_key) is not None


@pytest.mark.asyncio
async def test_pagination_cache_hit(
        async_session,
        project_service,
):
    project_repository = ProjectRepository(async_session)

    projects = await create_projects(project_service)

    projects_from_service = await project_service.list_projects(limit=2, cursor=None)

    for project_response in projects:
        project_model = await project_repository.get_project_by_id(
            project_response.id
        )
        assert project_model is not None
        await project_repository.delete_project(project_model)

    project_from_cache = await project_service.list_projects(limit=2, cursor=None)

    assert projects_from_service == project_from_cache


@pytest.mark.asyncio
async def test_different_cache_keys_for_pagination(project_service):
    await create_projects(project_service)

    first_response = await project_service.list_projects(
        limit=2,
        cursor=None,
    )
    second_response = await project_service.list_projects(
        limit=3,
        cursor=None,
    )

    assert first_response != second_response


@pytest.mark.asyncio
async def test_invalidate_cache_after_update(project_service: ProjectService, redis_cache):
    test_project_create_schema = ProjectCreate(
        name='test_project',
        slug='test-project',
        description='just a test project',
        status=ProjectStatus.COMPLETED
    )
    test_project = await project_service.create_project(test_project_create_schema)
    test_project_cached = await project_service.get_project_by_id(test_project.id)

    assert await redis_cache.get(
        ProjectService.project_key(test_project_cached.id)
    ) is not None 

    test_project_update_schema = ProjectUpdate(
        name='updated_project',
        description='Updated description',
        status=ProjectStatus.DRAFT,
    )
    updated_project = await project_service.update_project(
        test_project.id,
        test_project_update_schema,
    )

    cached_project = await redis_cache.get(
        ProjectService.project_key(test_project_cached.id)
    )

    assert cached_project is not None
    assert ProjectResponse.model_validate_json(cached_project) == updated_project


@pytest.mark.asyncio
async def test_invalidate_cache_after_delete(project_service: ProjectService, redis_cache):
    test_project_create_schema = ProjectCreate(
            name='test_project',
            slug='test-project',
            description='just a test project',
            status=ProjectStatus.COMPLETED
        )
    test_project = await project_service.create_project(test_project_create_schema)
    test_project_cached = await project_service.get_project_by_id(test_project.id)

    assert await redis_cache.get(
        ProjectService.project_key(test_project_cached.id)
    ) is not None 

    await project_service.delete_project(
        test_project.id,
    )

    assert await redis_cache.get(
        ProjectService.project_key(test_project_cached.id)
    ) is None


@pytest.mark.asyncio
async def test_project_tags(project_service, redis_cache):
    project_data = ProjectCreate(
        name='test project',
        slug='test-project',
        description='project with tags',
        status=ProjectStatus.DRAFT,
        tags=[
            TagCreate(
                name='Python',
                slug='python',
                description='python tag',
                color='#AAAAAA',
            ),
            TagCreate(
                name='Backend',
                slug='backend',
                description='backend tag',
                color='#000000',
            ),
        ],
    )

    project = await project_service.create_project(project_data)
    project_get = await project_service.get_project_by_id(project.id)

    assert len(project_get.tags) == 2
    assert [tag.slug for tag in project_get.tags] == ['python', 'backend']
    assert await redis_cache.get(ProjectService.project_key(project.id)) is not None

    update_data = ProjectUpdate(
        tags=[
            TagCreate(
                name='FastAPI',
                slug='fastapi',
                description='fastapi tag',
                color='#ABACAB',
            ),
        ],
    )

    updated_project = await project_service.update_project(
        project.id,
        update_data,
    )

    cached_project = await redis_cache.get(ProjectService.project_key(project.id))

    assert cached_project is not None
    assert ProjectResponse.model_validate_json(cached_project) == updated_project
