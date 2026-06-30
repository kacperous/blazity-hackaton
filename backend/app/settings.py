from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    anthropic_api_key: str = ""
    fal_key: str = ""
    replicate_api_token: str = ""
    creatomate_api_key: str = ""
    creatomate_template_id: str = ""
    video_output_dir: str = "./generated_videos"
    fb_page_id: str = ""
    fb_page_access_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
