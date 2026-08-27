from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt

from app.core.constants import DEFAULT_INVESTED_AMOUNT


class DonationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    full_amount: PositiveInt
    comment: str | None = None


class DonationCreate(DonationBase):
    model_config = ConfigDict(extra='forbid')


class DonationUserDB(DonationBase):
    id: int
    create_date: datetime


class DonationFullInfoDB(DonationBase):
    id: int
    create_date: datetime
    invested_amount: int = DEFAULT_INVESTED_AMOUNT
    fully_invested: bool = False
    close_date: datetime | None = None
    user_id: int
