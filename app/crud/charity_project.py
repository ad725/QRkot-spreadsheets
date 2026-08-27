from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_by_name(
        self, name: str, session: AsyncSession, project_id: int | None = None
    ) -> CharityProject | None:
        """Поиск проекта по имени для валидации уникальности."""
        query = select(self.model).where(self.model.name == name)
        if project_id:
            query = query.where(self.model.id != project_id)
        return (await session.scalars(query)).first()


charity_project_crud = CRUDCharityProject(CharityProject)
