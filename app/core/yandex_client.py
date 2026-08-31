import httpx
from fastapi import HTTPException, status

from app.core.base_storage import BaseStorageClient
from app.core.config import settings
from app.core.constants import (
    CONTENT_TYPE_EXCEL,
    FOLDER_NAME_YANDEX_DISK,
    PUBLISH_URL_YANDEX_DISK,
    RESOURCES_URL_YANDEX_DISK,
    UPLOAD_URL_YANDEX_DISK,
    YANDEX_DISK_TIMEOUT,
)
from app.core.exceptions import StorageAPIError, StorageError


class YandexDiskClient(BaseStorageClient):
    """Универсальный клиент для API Яндекс Диска."""

    def __init__(self, token: str):
        self.headers = {'Authorization': f'OAuth {token}'}
        self.timeout = YANDEX_DISK_TIMEOUT
        self.folder = FOLDER_NAME_YANDEX_DISK
        self.file_path = ''
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _send_request(
        self, method: str, url: str, headers: dict | None = None, **kwargs
    ) -> httpx.Response:
        """Внутренний метод для отправки запросов."""
        req_headers = {**self.headers, **(headers or {})}
        try:
            response = await self._client.request(
                method, url, headers=req_headers, **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise StorageAPIError(
                e.response.text, e.response.status_code
            ) from e
        except httpx.RequestError as e:
            raise StorageError(
                f'Ошибка сети при запросе к Яндекс Диску: {e}'
            ) from e

    async def _create_folder(self):
        """Создаёт папку, если её нет."""
        try:
            await self._send_request(
                'PUT',
                RESOURCES_URL_YANDEX_DISK,
                params={'path': f'disk:/{self.folder}'},
            )
        except StorageAPIError as e:
            if e.status_code != status.HTTP_409_CONFLICT:
                raise

    async def create_excel_file(self, title: str) -> str:
        """Создаёт файл и возвращает ссылку для загрузки."""
        await self._create_folder()
        self.file_path = f'disk:/{self.folder}/{title}'
        response = await self._send_request(
            'GET',
            UPLOAD_URL_YANDEX_DISK,
            params={'path': self.file_path, 'overwrite': 'true'},
        )
        if not (upload_url := response.json().get('href')):
            raise StorageError(
                'Не удалось получить ссылку для загрузки из ответа API.'
            )
        return upload_url

    async def upload_file(self, upload_url: str, content: bytes):
        """Загружает контент файла по полученной ссылке."""
        await self._send_request(
            'PUT',
            upload_url,
            content=content,
            headers={'Content-Type': CONTENT_TYPE_EXCEL},
        )

    async def publish_file(self) -> str:
        """Делает файл публичным и возвращает ссылку."""
        await self._send_request(
            'PUT', PUBLISH_URL_YANDEX_DISK, params={'path': self.file_path}
        )
        response = await self._send_request(
            'GET', RESOURCES_URL_YANDEX_DISK, params={'path': self.file_path}
        )
        if not (public_url := response.json().get('public_url')):
            raise StorageError(
                'Ссылка не была получена со стороны Яндекс Диска.'
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
    try:
        async with YandexDiskClient(settings.yandex_disk_token) as client:
            yield client
    except StorageError as e:
        if isinstance(e, StorageAPIError) and (
            e.status_code == status.HTTP_401_UNAUTHORIZED
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Предоставлен невалидный токен Яндекс Диска.',
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Ошибка Яндекс Диска: {e}',
        )
