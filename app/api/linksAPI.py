from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.link import Link
from app.repositories.linkRepository import LinkRepository
from app.repositories.userRepository import UserRepository
from app.schemes.linkSchemes import SLinkCreate, SLink
from app.schemes.userSchemes import SUser

router = APIRouter(prefix="/links", tags=["Work with Links"])

@router.get("", summary="Get links for current user")
async def get_links(current_user: SUser = Depends(UserRepository.get_current_user)) -> List[SLink]:
    return await LinkRepository.get_links(user_id=current_user.id)

@router.get('/{link_id}', summary="Get link by id for current user")
async def get_link_by_id(link_id: int,
                         current_user: SUser = Depends(UserRepository.get_current_user)) -> SLink:
    return await LinkRepository.get_link_by_id(link_id, user_id=current_user.id)

@router.post("/create", summary="Create link")
async def create_link(link_data: SLinkCreate = Depends(),
                      current_user: SUser = Depends(UserRepository.get_current_user)) -> dict:
    return await LinkRepository.create_link(link_data, user_id=current_user.id)

@router.post("/delete", summary="Delete link")
async def delete_link(link_id: int,
                      current_user: SUser = Depends(UserRepository.get_current_user)) -> dict:
    return await LinkRepository.delete_link(link_id, user_id=current_user.id)

@router.get('/r/{short_code}', summary='Redirect by short link')
async def redirect_short_link(short_code: str,
                              current_user: SUser = Depends(UserRepository.get_current_user)) -> str:
    async with async_session_maker() as session:
        query = select(Link).where(Link.short_code == short_code, Link.user_id == current_user.id)
        result = await session.execute(query)
        link = result.scalar_one_or_none()

        if not link:
            raise HTTPException(status_code=404, detail='Link not found')

        link.clicks_count += 1
        await session.commit()

        if not link.original_url.startswith(('http://', 'https://')):
            link.original_url = f'https://{link.original_url}'

        try:
            urlparse(link.original_url)
            return link.original_url
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid URL format")