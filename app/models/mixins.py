from datetime import datetime

from sqlalchemy.orm import Mapped, declared_attr, mapped_column


def get_current_time() -> datetime:
    """Возвращает текущее время."""
    return datetime.now()


class CommonMixin:
    """Базовый миксин моделей."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
    full_amount: Mapped[int] = mapped_column(nullable=False)
    invested_amount: Mapped[int] = mapped_column(default=0, nullable=False)
    fully_invested: Mapped[bool] = mapped_column(default=False, nullable=False)
    create_date: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    close_date: Mapped[datetime | None] = mapped_column(nullable=True)
