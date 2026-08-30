from abc import ABC, abstractmethod

from app.models.charity_project import CharityProject


class BaseReportGenerator(ABC):
    @abstractmethod
    async def generate_report(
        self, projects: list[CharityProject]
    ) -> tuple[bytes, str]:
        """Генерирует отчет и возвращает (содержимое_файла, имя_файла)."""
