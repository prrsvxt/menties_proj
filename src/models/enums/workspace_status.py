from enum import Enum


class WorkspaceStatus(str, Enum):
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    SUSPENDED = 'suspended'