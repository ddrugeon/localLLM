from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    document_folder: Path = Field(default=Path(ROOT_DIR, Path("data/inputs")).absolute())