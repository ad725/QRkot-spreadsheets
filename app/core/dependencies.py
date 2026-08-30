from app.core.base_storage import BaseStorageClient
from app.core.yandex_client import get_yandex_client


async def get_storage_client() -> BaseStorageClient:
    async for client in get_yandex_client():
        yield client
