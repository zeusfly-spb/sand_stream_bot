from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    admin_ids: str = ""
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://sandstream:change_me@localhost:5432/sandstream"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def admin_id_set(self) -> set[int]:
        return {
            int(value.strip())
            for value in self.admin_ids.split(",")
            if value.strip().isdigit()
        }


settings = Settings()
