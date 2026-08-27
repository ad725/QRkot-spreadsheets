from fastapi import APIRouter

from app.api.endpoints import charity_project, donation, user_router

main_router = APIRouter()

main_router.include_router(
    charity_project.router, prefix='/charity_project', tags=['Проекты']
)
main_router.include_router(
    donation.router, prefix='/donation', tags=['Пожертвования']
)
main_router.include_router(user_router)
