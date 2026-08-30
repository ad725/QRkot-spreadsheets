from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_storage import BaseStorageClient
from app.core.db import get_async_session
from app.core.dependencies import get_storage_client
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/', response_model=str, dependencies=[Depends(current_superuser)]
)
async def create_report(
    session: AsyncSession = Depends(get_async_session),
    storage_client: BaseStorageClient = Depends(get_storage_client),
):
    """
    Создает Excel-отчёт о закрытых проектах и загружает его на Яндекс Диск.
    Возвращает публичную ссылку на файл.
    Доступно только суперпользователям.
    """
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет закрытых проектов для формирования отчёта.',
        )
    try:
        return await create_simple_report(projects, storage_client)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчёта: {str(e)}',
        )
