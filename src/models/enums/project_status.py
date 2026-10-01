from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'
