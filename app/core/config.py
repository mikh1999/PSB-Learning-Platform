from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "psb_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # App
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8080
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PSB Learning Platform"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_LESSON_EXTENSIONS: str = ".pdf,.docx,.pptx,.mp4,.zip,.txt,.md"
    ALLOWED_SUBMISSION_EXTENSIONS: str = ".pdf,.docx,.zip,.py,.ipynb,.txt,.md"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()