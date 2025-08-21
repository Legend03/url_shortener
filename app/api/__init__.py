from fastapi import APIRouter
from .linksAPI import router as linksRouter
from .userAPI import router as usersRouter

router = APIRouter()

router.include_router(linksRouter, prefix='/links', tags=['links'])
router.include_router(usersRouter, prefix='/users', tags=['users'])

__all__ = [
    'router',
]
