from email.policy import default

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from ..core.database import Base, int_pk, str_uniq, str_nullable_false

class Link(Base):
    id: Mapped[int_pk]
    original_url: Mapped[str_nullable_false]
    short_url: Mapped[str_nullable_false]
    clicks_count: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    clicks = relationship('Click', back_populates='link', cascade='all, delete, delete-orphan')
    user = relationship('User')