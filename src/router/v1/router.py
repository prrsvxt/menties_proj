from fastapi import APIRouter

from src.router.v1.healthcheck import router as healthcheck_router
from src.router.v1.projects import router as projects_router
from src.router.v1.tags import router as tags_router
from src.router.v1.users import router as users_router
from src.router.v1.workspaces import router as workspaces_router


router_v1 = APIRouter(prefix='/v1')

router_v1.include_router(healthcheck_router)
router_v1.include_router(projects_router)
router_v1.include_router(tags_router)
router_v1.include_router(users_router)
router_v1.include_router(workspaces_router)
