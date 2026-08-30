from typing import Protocol


class BaseStorageClient(Protocol):
    async def upload_and_publish(self, content: bytes, filename: str) -> str:
        """Загружает файл и возвращает публичную ссылку."""
