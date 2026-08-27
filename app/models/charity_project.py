from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MAX_NAME_LENGTH
from app.core.db import Base
from app.models.mixins import CommonMixin


class CharityProject(CommonMixin, Base):
    """Модель целевых проектов."""

    name: Mapped[str] = mapped_column(
        String(MAX_NAME_LENGTH), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(nullable=True)
