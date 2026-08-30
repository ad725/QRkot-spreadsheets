import httpx
from fastapi import HTTPException, status

from app.core.base_storage import BaseStorageClient
from app.core.config import settings
from app.core.constants import (
    BASE_URL_YANDEX_DISK,
    FOLDER_NAME_YANDEX_DISK,
    PUBLISH_URL_YANDEX_DISK,
    RESOURCES_URL_YANDEX_DISK,
    UPLOAD_URL_YANDEX_DISK,
    YANDEX_DISK_TIMEOUT,
)


class YandexDiskClient(BaseStorageClient):
    """Универсальный клиент для API Яндекс Диска."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = BASE_URL_YANDEX_DISK
        self.timeout = YANDEX_DISK_TIMEOUT
        self.headers = {'Authorization': f'OAuth {token}'}
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _create_folder(self, folder: str):
        """Создаёт папку, если её нет."""
        try:
            await self._client.put(
                RESOURCES_URL_YANDEX_DISK,
                headers=self.headers,
                params={'path': f'disk:/{folder}'},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code != status.HTTP_409_CONFLICT:
                raise

    async def create_excel_file(
        self, title: str, folder: str = FOLDER_NAME_YANDEX_DISK
    ) -> tuple[str, str]:
        """
        Создаёт Excel-файл и возвращает ссылку для загрузки и путь к файлу.
        """
        await self._create_folder(folder)
        file_path = f'disk:/{folder}/{title}.xlsx'
        response = await self._client.get(
            UPLOAD_URL_YANDEX_DISK,
            headers=self.headers,
            params={'path': file_path, 'overwrite': 'true'},
        )
        response.raise_for_status()
        data = response.json()
        upload_url = data.get('href')
        if not upload_url:
            raise ValueError('Не удалось получить ссылку для загрузки.')
        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes):
        """Загружает файл по полученной ссылке."""
        response = await self._client.put(
            upload_url,
            content=content,
            headers={
                'Content-Type': 'application/vnd.openxmlformats-'
                'officedocument.spreadsheetml.sheet'
            },
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        """Делает файл публичным и возвращает ссылку."""
        response = await self._client.put(
            PUBLISH_URL_YANDEX_DISK,
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()
        response = await self._client.get(
            RESOURCES_URL_YANDEX_DISK,
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()
        data = response.json()
        public_url = data.get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Ссылка не была получена со стороны Яндекс Диска.',
            )
        return public_url


async def get_yandex_client():
    """Dependency для получения клиента Яндекс Диска."""
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Яндекс Диск не настроен. Пожалуйста, '
            'добавьте YANDEX_DISK_TOKEN в .env-файл',
        )
    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
