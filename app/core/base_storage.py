from typing import Protocol


class BaseStorageClient(Protocol):
    async def create_excel_file(self, title: str) -> str:
        """Создаёт файл в хранилище и возвращает ссылку для загрузки."""

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        """Загружает содержимое файла по полученной ссылке."""

    async def publish_file(self) -> str:
        """Делает файл публичным и возвращает ссылку."""
