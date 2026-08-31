from collections.abc import AsyncGenerator

from fastapi import Depends

from app.core.base_report_generator import BaseReportGenerator
from app.core.base_storage import BaseStorageClient
from app.core.yandex_client import get_yandex_client
from app.services.excel_report_generator import ExcelReportGenerator
from app.services.yandex_api import ReportService


async def get_storage_client() -> AsyncGenerator[BaseStorageClient, None]:
    async for client in get_yandex_client():
        yield client


def get_report_generator() -> BaseReportGenerator:
    """Поставщик генератора отчетов."""
    return ExcelReportGenerator()


async def get_report_service(
    generator: BaseReportGenerator = Depends(get_report_generator),
    storage_client: BaseStorageClient = Depends(get_storage_client),
) -> ReportService:
    """Поставщик сервиса отчетов."""
    return ReportService(generator, storage_client)
