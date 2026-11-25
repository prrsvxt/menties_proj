import pytest
import pytest_asyncio
from uuid import uuid4

from src.services.workspace_service import WorkspaceService
from src.UoW.workspace_UoW import WorkspaceUoW
from src.repositories.workspace_repository import WorkspaceRepository
from src.mappers.workspace_mapper import WorkspaceMapper
from src.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from src.schemas.workspace_settings import (
    WorkspaceSettingsCreate,
    WorkspaceSettingsUpdate,
)
from src.models.enums.workspace_status import WorkspaceStatus
from src.exceptions.general_errors import NotFoundError


async def create_workspaces(
        workspace_service: WorkspaceService,
        count: int = 5,
):
    workspaces = []
    test_id = uuid4().hex

    for index in range(count):
        workspace_data = WorkspaceCreate(
            name=f'test_workspace_{test_id}_{index}',
            slug=f'test-workspace-{test_id}-{index}',
            description=f'Description {index}',
            status=WorkspaceStatus.ACTIVE,
            workspace_settings=WorkspaceSettingsCreate(
                timezone='UTC',
                language='ru',
                notifications_enabled=True,
            ),
        )
        workspace = await workspace_service.create_workspace(workspace_data)
        workspaces.append(workspace)

    return workspaces


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def workspace_service(session_factory, redis_cache):
    unit_of_work = WorkspaceUoW(session_factory)
    mapper = WorkspaceMapper()
    workspace_service = WorkspaceService(unit_of_work, mapper, redis_cache)

    return workspace_service


@pytest.mark.asyncio
async def test_workspace_by_id(workspace_service, async_session, redis_cache):
    workspace_repository = WorkspaceRepository(async_session)

    workspace_data = WorkspaceCreate(
        name='test workspace',
        slug='test-workspace',
        description='workspace for test',
        status=WorkspaceStatus.ACTIVE,
        workspace_settings=WorkspaceSettingsCreate(
            timezone='UTC',
            language='ru',
            notifications_enabled=True,
        ),
    )

    workspace = await workspace_service.create_workspace(workspace_data)

    await workspace_service.get_workspace_by_id(workspace.id)
    
    assert (await redis_cache.get(
        WorkspaceService.workspace_key(workspace.id)
    )) is not None

    workspace_model = await workspace_repository.get_workspace_by_id(workspace.id)
    assert workspace_model is not None

    await workspace_repository.delete_workspace(workspace_model)
    assert (await redis_cache.get(
        WorkspaceService.workspace_key(workspace.id)
    )) is not None  


@pytest.mark.asyncio
async def test_workspace_not_found(workspace_service):

    with pytest.raises(NotFoundError):
        await workspace_service.get_workspace_by_id(uuid4())


@pytest.mark.asyncio
async def test_workspace_settings(workspace_service, redis_cache):
    workspace_data = WorkspaceCreate(
        name='workspace settings',
        slug='workspace-settings',
        description='workspace settings test',
        workspace_settings=WorkspaceSettingsCreate(
            timezone='UTC',
            language='ru',
            notifications_enabled=True,
        ),
    )

    workspace = await workspace_service.create_workspace(workspace_data)

    assert workspace.workspace_settings.timezone == 'UTC'
    assert workspace.workspace_settings.language == 'ru'
    assert workspace.workspace_settings.notifications_enabled is True

    workspace_update = WorkspaceUpdate(
        workspace_settings=WorkspaceSettingsUpdate(
            timezone='Asia/Novosibirsk',
            language='en',
            notifications_enabled=False,
        ),
    )

    updated_workspace = await workspace_service.update_workspace(
        workspace.id,
        workspace_update,
    )

    assert updated_workspace.workspace_settings.timezone == 'Asia/Novosibirsk'
    assert updated_workspace.workspace_settings.language == 'en'
    assert updated_workspace.workspace_settings.notifications_enabled is False

    cached_workspace = await redis_cache.get(
        WorkspaceService.workspace_key(workspace.id)
    )

    assert cached_workspace is not None
    assert WorkspaceResponse.model_validate_json(cached_workspace) == updated_workspace


@pytest.mark.asyncio
async def test_pagination_cache_miss(workspace_service, redis_cache):
    workspaces = await create_workspaces(workspace_service)

    cache_version = await redis_cache.get(
        WorkspaceService.WORKSPACES_LIST_VERSION_KEY
    )
    assert cache_version is not None

    pagination_response = await workspace_service.list_workspaces(limit=2, cursor=None)
    assert len(pagination_response.items) == 2
    assert pagination_response.next_cursor is not None

    workspace_ids = [workspace.id for workspace in workspaces]
    assert all(
        item.id in workspace_ids
        for item in pagination_response.items
    )


@pytest.mark.asyncio
async def test_pagination_cache_hit(workspace_service, async_session, redis_cache):
    workspace_repository = WorkspaceRepository(async_session)
    workspaces = await create_workspaces(workspace_service)

    cache_version = await redis_cache.get(
        WorkspaceService.WORKSPACES_LIST_VERSION_KEY
    )
    assert cache_version is not None

    first_page = await workspace_service.list_workspaces(limit=2, cursor=None)
    assert await redis_cache.get(
        WorkspaceService.workspace_list_version(
            cache_version,
            limit=2,
            cursor=None,
        )
    ) is not None

    for workspace in workspaces:
        workspace_model = await workspace_repository.get_workspace_by_id(
            workspace.id
        )
        assert workspace_model is not None
        await workspace_repository.delete_workspace(workspace_model)

    assert first_page == (await workspace_service.list_workspaces(limit=2, cursor=None))
    assert await redis_cache.get(
        WorkspaceService.workspace_list_version(
            cache_version,
            limit=2,
            cursor=None,
        )
    ) is not None


@pytest.mark.asyncio
async def test_different_cache_keys_for_pagination(workspace_service, redis_cache):
    await create_workspaces(workspace_service)

    await workspace_service.list_workspaces(limit=2, cursor=None)
    await workspace_service.list_workspaces(limit=3, cursor=None)

    cache_version = await redis_cache.get(
        WorkspaceService.WORKSPACES_LIST_VERSION_KEY
    )
    assert cache_version is not None

    assert (
        (await redis_cache.get(
            WorkspaceService.workspace_list_version(
                cache_version,
                limit=2,
                cursor=None,
            )
        )) 
        != 
        (await redis_cache.get(
            WorkspaceService.workspace_list_version(
                cache_version,
                limit=3,
                cursor=None,
            )
        ))
    )


@pytest.mark.asyncio
async def test_cache_invalidation_after_delete(workspace_service, redis_cache):

    workspace_data = WorkspaceCreate(
        name='workspace settings',
        slug='workspace-settings',
        description='workspace settings test',
        workspace_settings=WorkspaceSettingsCreate(
            timezone='UTC',
            language='ru',
            notifications_enabled=True,
        ),
    )

    workspace = await workspace_service.create_workspace(workspace_data)

    workspace_cache = await workspace_service.get_workspace_by_id(workspace.id)
    await workspace_service.delete_workspace(workspace.id)

    assert await redis_cache.get(
        WorkspaceService.workspace_key(workspace.id)
    ) is None
