from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.models.user import User


class CRUDDonation(CRUDBase):
    async def get_all_donations_of_user(
        self, session: AsyncSession, user: User
    ) -> list[Donation]:
        """Получить все пожервования пользователя."""
        query = select(self.model).where(self.model.user_id == user.id)
        donations = await session.execute(query)
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
