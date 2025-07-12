from sqlalchemy.orm import Mapped
from ..core.database import Base, int_pk, str_uniq, str_nullable_false

class User(Base):
    id: Mapped[int_pk]
    email: Mapped[str_uniq]
    password_hash: Mapped[str_nullable_false]