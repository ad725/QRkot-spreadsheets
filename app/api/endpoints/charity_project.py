from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.validators import (
    check_name_duplicate,
    check_project_before_delete,
    check_project_before_edit,
    check_project_exists,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import process_investments

router = APIRouter()


@router.get('/', response_model=list[CharityProjectDB])
async def get_projects(session: AsyncSession = Depends(get_async_session)):
    """Показать список всех целевых проектов."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_project(
    project_data: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать целевой проект.

    Только для суперюзеров.
    """
    await check_name_duplicate(project_data.name, session)
    new_project = await charity_project_crud.create(project_data, session)
    uninvested_donations = await donation_crud.get_uninvested(session)
    updated_donations = process_investments(new_project, uninvested_donations)
    if updated_donations:
        session.add_all(updated_donations)
    await session.commit()
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    project_data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Редактировать целевой проект.

    Только для суперюзеров.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    project = await check_project_exists(project_id, session)
    check_project_before_edit(project, project_data)
    if project_data.name:
        await check_name_duplicate(project_data.name, session, project_id)
    if project.invested_amount == project_data.full_amount:
        project.fully_invested = True
        project.close_date = datetime.now()
    return await charity_project_crud.update(project, project_data, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
    project_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Удалить целевой проект.

    Только для суперюзеров. Нельзя удалить проект,
    в который уже были инвестированы средства.
    """
    project = await check_project_exists(project_id, session)
    check_project_before_delete(project)
    return await charity_project_crud.remove(project, session)
