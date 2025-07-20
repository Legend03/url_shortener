from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .click import Click
from .user import User
from ..core.database import Base, int_pk, str_uniq, str_nullable_false

class Link(Base):
    id: Mapped[int_pk]
    original_url: Mapped[str_nullable_false]
    short_code: Mapped[str_uniq]
    clicks_count: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    clicks: Mapped[List['Click']] = relationship(back_populates='link', cascade='all, delete-orphan')
    user: Mapped['User'] = relationship(back_populates='links')