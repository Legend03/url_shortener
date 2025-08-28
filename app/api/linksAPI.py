from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from starlette.responses import RedirectResponse

from app.core.database import async_session_maker
from app.models.link import Link
from app.repositories.linkRepository import LinkRepository
from app.repositories.userRepository import UserRepository
from app.schemes.linkSchemes import SLinkCreate, SLink
from app.schemes.userSchemes import SUser

router = APIRouter(prefix="/dashboard", tags=["Work with Links in Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", summary="Get links for current user")
async def get_links(request: Request, current_user: SUser = Depends(UserRepository.require_auth)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Not Authorized')

    links = await LinkRepository.get_links_by_user_id(current_user.id)
    total_links = len(links)
    total_clicks = sum(link.clicks_count for link in links)

    return templates.TemplateResponse("dashboard.html", {
        'request': request,
        'user': current_user,
        'links': links,
        'total_links': total_links,
        'total_clicks': total_clicks,
    })

@router.get('/{link_id}', summary="Get link by id for current user")
async def get_link_by_id(link_id: int,
                         current_user: SUser = Depends(UserRepository.require_auth)) -> SLink:
    return await LinkRepository.get_link_by_id(link_id, user_id=current_user.id)

@router.post("/create-link", summary="Create link")
async def create_link(original_url: str = Form(...),
                      current_user: SUser = Depends(UserRepository.require_auth)):
    return await LinkRepository.create_link(original_url, user_id=current_user.id)

@router.post("/delete-link", summary="Delete link")
async def delete_link(link_id: int = Form(...),
                              current_user: SUser = Depends(UserRepository.require_auth)):
    return await LinkRepository.delete_link(link_id, current_user)

@router.get('/r/{short_code}', summary='Redirect by short link')
async def redirect_short_link(short_code: str,
                              current_user: SUser = Depends(UserRepository.require_auth)):
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
            return RedirectResponse(url=link.original_url, status_code=302)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid URL format")