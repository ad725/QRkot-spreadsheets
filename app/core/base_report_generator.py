from typing import Protocol

from app.models.charity_project import CharityProject


class BaseReportGenerator(Protocol):
    async def generate_report(
        self, projects: list[CharityProject]
    ) -> tuple[bytes, str]:
        """Генерирует отчет и возвращает (содержимое_файла, имя_файла)."""
