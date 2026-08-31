class StorageError(Exception):
    """Базовое исключение для хранилища."""


class StorageAPIError(StorageError):
    """Ошибка ответа API с сохранением статус-кода."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code
