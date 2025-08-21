from fastapi import APIRouter
from .linksAPI import router as linksRouter
from .userAPI import router as usersRouter

router = APIRouter()

router.include_router(linksRouter)
router.include_router(usersRouter)

__all__ = [
    'router',
]
