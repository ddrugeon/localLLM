from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv('.env')

ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    document_folder: Path = Field(
        default=Path(ROOT_DIR, Path("data/inputs")).absolute()
    )

    discogs_user_token: SecretStr