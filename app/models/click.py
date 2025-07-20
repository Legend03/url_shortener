from fastapi.openapi.models import Link
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from ..core.database import Base, int_pk, str_uniq, str_nullable_false

class Click(Base):
    id: Mapped[int_pk]
    ip_address: Mapped[str_nullable_false]
    country_code: Mapped[str_nullable_false]
    device_type: Mapped[str_nullable_false]
    link_id: Mapped[int] = mapped_column(ForeignKey('links.id'), nullable=False)

    link: Mapped['Link'] = relationship(back_populates='clicks')