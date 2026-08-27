from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.core.constants import (
    DEFAULT_INVESTED_AMOUNT,
    MAX_NAME_LENGTH,
    MIN_DESCRIPTION_LENGTH,
    MIN_NAME_LENGTH,
)


class CharityProjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    description: str = Field(min_length=MIN_DESCRIPTION_LENGTH)
    full_amount: PositiveInt


class CharityProjectCreate(CharityProjectBase):
    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(CharityProjectBase):
    model_config = ConfigDict(extra='forbid')
    name: str | None = Field(
        None, min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH
    )
    description: str | None = Field(None, min_length=MIN_DESCRIPTION_LENGTH)
    full_amount: PositiveInt | None = None


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int = DEFAULT_INVESTED_AMOUNT
    fully_invested: bool = False
    create_date: datetime
    close_date: datetime | None = None
