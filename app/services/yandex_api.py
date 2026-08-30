from typing import List

from app.core.base_report_generator import BaseReportGenerator
from app.core.base_storage import BaseStorageClient
from app.models.charity_project import CharityProject


class ReportService:
    """Сервис для создания и загрузки отчетов."""

    def __init__(
        self, generator: BaseReportGenerator, storage_client: BaseStorageClient
    ):
        self.generator = generator
        self.storage_client = storage_client

    async def create_and_upload_report(
        self, projects: List[CharityProject]
    ) -> str:
        """Создает отчет и загружает его в хранилище."""
        file_content, file_name = await self.generator.generate_report(
            projects
        )

        upload_url, file_path = await self.storage_client.create_excel_file(
            file_name
        )
        await self.storage_client.upload_file(upload_url, file_content)
        return await self.storage_client.publish_file(file_path)
