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

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ):
        """Получить закрытые проекты, отсортированные по скорости сбора."""
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.close_date.isnot(None))
            .order_by(CharityProject.close_date - CharityProject.create_date)
        )
        return result.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
