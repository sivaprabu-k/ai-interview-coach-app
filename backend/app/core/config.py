from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Interview Coach"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5433/ai_interview_coach"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
