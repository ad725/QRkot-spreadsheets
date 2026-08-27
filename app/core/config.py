from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация настроек приложения."""

    app_title: str = 'Благотворительный фонд QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    app_author: str = 'ad725'
    author_pass: str = 'qwerty123'
    secret: str = 'secret'
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    yandex_disk_token: str | None = None
    report_format: str = '%Y/%m/%d %H:%M:%S'

    class Config:
        env_file = '.env'


settings = Settings()
