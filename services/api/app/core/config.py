from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Greenhouse Farm API"
    environment: str = "development"
    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 480
    database_url: str = "postgresql+psycopg://agri:agri@localhost:5432/agri"
    farm_timezone: str = "Africa/Casablanca"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    seed_demo: bool = True
    summary_only_mode: bool = False
    force_analysis_failure: bool = False
    ops_token: str = "dev-ops-token"
    otel_exporter_otlp_endpoint: str = ""
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
