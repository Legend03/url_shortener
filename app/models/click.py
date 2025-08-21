from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.core.database import Base, int_pk, str_nullable_false

class Click(Base):
    id: Mapped[int_pk]
    ip_address: Mapped[str_nullable_false]
    country_code: Mapped[str_nullable_false]
    device_type: Mapped[str_nullable_false]
    link_id: Mapped[int] = mapped_column(ForeignKey('links.id'), nullable=False)

    link: Mapped['Link'] = relationship(back_populates='clicks')