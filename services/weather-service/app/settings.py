from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    weather_api_url: str
    geocoding_user_agent: str
    geocoding_api_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
