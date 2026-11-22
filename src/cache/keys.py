from uuid import UUID

CACHE_VERSION = 'v1'

PROJECTS_LIST_VERSION_KEY = "projects:list:version"
WORKSPACES_LIST_VERSION_KEY = "workspaces:list:version"


def project_key(project_id: UUID) -> str:
    return f'{CACHE_VERSION}:project:{project_id}'


def workspace_key(workspace_id: UUID) -> str:
    return f'{CACHE_VERSION}:workspace:{workspace_id}'


def user_key(user_id: UUID) -> str:
    return f'{CACHE_VERSION}:user:{user_id}'


def project_list_version(
        version: int,
        limit: int,
        cursor: str | None,
) -> str:
    return f'{CACHE_VERSION}:projects:list:v{version}:limit{limit}:{cursor if cursor else 'first'}'

def workspace_list_version(
        version: int,
        limit: int,
        cursor: str | None,
) -> str:
    return f'{CACHE_VERSION}:workspaces:list:v{version}:limit{limit}:{cursor if cursor else 'first'}'
