from enum import Enum


class AccessTypes(str, Enum):
    ACCESS = 'access'
    EXECUTE = 'execute'
    EXPORT = 'export'
    COMMENT = 'comment'
    AUDIT = 'audit'


class AccessStatus(str, Enum):
    ACTIVE = 'active'
    REVOKED = 'revoked'
    EXPIRED = 'expired'