import secrets
import string
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select, delete

from app.core.database import async_session_maker
from app.models.link import Link
from app.schemes.linkSchemes import SLinkCreate, SLink


class LinkRepository:
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    @classmethod
    async def create_link(cls, link_data: SLinkCreate, user_id: int = Depends()) -> dict:
        short_code = cls.generate_short_code()

        new_link = Link(
            original_url=link_data.original_url,
            short_code=short_code,
            user_id=user_id,
        )

        async with async_session_maker() as session:
            session.add(new_link)
            await session.commit()
            await session.refresh(new_link)
            return { 'message': 'Link successfully created!' }

    @classmethod
    async def get_links(cls, user_id: int) -> List[SLink]:
        async with async_session_maker() as session:
            query = select(Link).where(Link.user_id == user_id)
            result = await session.execute(query)
            links_model = result.scalars().all()
            links = [SLink.model_validate(link) for link in links_model]

            return links

    @classmethod
    async def get_link_by_id(cls, link_id: int, user_id: int = Depends()) -> SLink:
        async with async_session_maker() as session:
            query = select(Link).where(Link.id == link_id, Link.user_id == user_id)
            result = await session.execute(query)
            link = result.scalar_one_or_none()
            if not link:
                raise HTTPException(status_code=404, detail="Link not found")
            return SLink.model_validate(link)

    @classmethod
    async def delete_link(cls, link_id):
        async with async_session_maker() as session:
            await cls.get_link_by_id(link_id)

            query = delete(Link).where(Link.id == link_id)
            await session.execute(query)
            await session.commit()
            return { 'message': 'Link deleted Successfully' }

    @classmethod
    async def link_exists(cls, link_id):
        link = await cls.get_link_by_id(link_id)

        if link is None:
            raise HTTPException(status_code=404, detail="Link not found")