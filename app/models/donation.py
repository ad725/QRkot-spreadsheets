from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.mixins import CommonMixin


class Donation(CommonMixin, Base):
    """Модель пожертвований."""

    comment: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_reservation_user_id_user'),
        nullable=True,
    )
