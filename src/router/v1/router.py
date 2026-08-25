from fastapi import APIRouter

from src.router.v1.healthcheck import router as healthcheck_router
from src.router.v1.users import router as users_router


router_v1 = APIRouter(prefix='/v1')

router_v1.include_router(healthcheck_router)
router_v1.include_router(users_router)