import secrets
import string
from typing import List

from fastapi import HTTPException, Depends, Form
from sqlalchemy import select, delete
from starlette.responses import RedirectResponse

from app.core.database import async_session_maker
from app.models.link import Link
from app.repositories.userRepository import UserRepository
from app.schemes import SUser
from app.schemes.linkSchemes import SLink


class LinkRepository:
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    @classmethod
    async def create_link(cls, original_link: str, user_id: int) -> RedirectResponse:
        short_code = cls.generate_short_code()

        new_link = Link(
            original_url=original_link,
            short_code=short_code,
            user_id=user_id,
        )

        async with async_session_maker() as session:
            session.add(new_link)
            await session.commit()
            await session.refresh(new_link)
            return RedirectResponse(url="/dashboard", status_code=303)

    @classmethod
    async def get_links_by_user_id(cls, user_id: int) -> List[SLink]:
        async with async_session_maker() as session:
            query = select(Link).where(Link.user_id == user_id)
            result = await session.execute(query)
            links_model = result.scalars().all()
            links = [SLink.model_validate(link) for link in links_model]

            return links

    @classmethod
    async def get_link_by_id(cls, link_id: int, user_id: int) -> SLink:
        async with async_session_maker() as session:
            query = select(Link).where(Link.id == link_id, Link.user_id == user_id)
            result = await session.execute(query)
            link = result.scalar_one_or_none()
            if not link:
                raise HTTPException(status_code=404, detail="Link not found")
            return SLink.model_validate(link)

    @classmethod
    async def delete_link(cls, link_id: int, current_user: SUser):
        async with async_session_maker() as session:
            await cls.get_link_by_id(link_id, current_user.id)

            query = delete(Link).where(Link.id == link_id)
            await session.execute(query)
            await session.commit()

            return RedirectResponse(url="/dashboard", status_code=303)

    @classmethod
    async def link_exists(cls, link_id, user_id: int):
        link = await cls.get_link_by_id(link_id, user_id)

        if link is None:
            raise HTTPException(status_code=404, detail="Link not found")