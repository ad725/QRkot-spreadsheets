from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationFullInfoDB,
    DonationUserDB,
)
from app.services.investment import process_investments

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    dependencies=[Depends(current_superuser)],
)
async def get_donations(session: AsyncSession = Depends(get_async_session)):
    """Показать список всех пожертвований.

    Только для суперюзеров.
    """
    return await donation_crud.get_multi(session)


@router.post(
    '/', response_model=DonationUserDB, response_model_exclude_none=True
)
async def create_donation(
    donation_data: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Сделать пожертвование.

    Только для зарегистрированных пользователей.
    """
    new_donation = await donation_crud.create(donation_data, session, user)
    uninvested_projects = await charity_project_crud.get_uninvested(session)
    updated_projects = process_investments(new_donation, uninvested_projects)
    if updated_projects:
        session.add_all(updated_projects)
    await session.commit()
    return new_donation


@router.get('/my', response_model=list[DonationUserDB])
async def get_all_donations_of_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Показать список пожертвований пользователя, выполняющего запрос.

    Только для зарегистрированных пользователей.
    """
    return await donation_crud.get_all_donations_of_user(session, user)
