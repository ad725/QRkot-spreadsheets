from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация настроек приложения."""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_title: str = 'Благотворительный фонд QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    app_author: str = 'ad725'
    author_pass: str = 'qwerty123'
    secret: str = 'secret'
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    yandex_disk_token: str | None = None
    report_format: str = '%Y-%m-%d_%H-%M-%S'


settings = Settings()
