from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_INVESTED_AMOUNT
from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject
from app.schemas.charity_project import CharityProjectUpdate


async def check_name_duplicate(
    name: str, session: AsyncSession, project_id: int | None = None
) -> None:
    """Проверить уникальность имени проекта."""
    if await charity_project_crud.get_project_by_name(
        name, session, project_id
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            'Проект с таким названием уже существует!',
        )


async def check_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    """Проверить существование проекта по ID."""
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден'
        )
    return project


def check_project_before_edit(
    project: CharityProject, project_data: CharityProjectUpdate
) -> None:
    """Проверить возможность редактирования проекта."""
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )
    if project_data.full_amount and (
        project_data.full_amount < project.invested_amount
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Требуемая сумма не может быть меньше внесенной!',
        )


def check_project_before_delete(project: CharityProject) -> None:
    if project.invested_amount > DEFAULT_INVESTED_AMOUNT:
        """Проверить возможность удаления проекта."""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
