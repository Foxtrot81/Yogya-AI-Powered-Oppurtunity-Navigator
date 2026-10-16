"""
Pipeline configuration and path management for Yogya Data Pipeline.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Find project root (directory containing schemas/ and config/)
def find_project_root() -> Path:
    # Check current working directory first
    cwd = Path.cwd().resolve()
    if (cwd / "config" / "settings.json").exists():
        return cwd
    if (cwd / "yogya-data" / "config" / "settings.json").exists():
        return cwd / "yogya-data"
    
    # Check parent of current file
    file_dir = Path(__file__).resolve().parent.parent
    if (file_dir / "config" / "settings.json").exists():
        return file_dir
        
    return cwd

PROJECT_ROOT = find_project_root()

# Load .env file
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Config:
    def __init__(self, root: Optional[Path] = None):
        self.root = root or PROJECT_ROOT
        self.settings_path = self.root / "config" / "settings.json"
        self.registry_path = self.root / "config" / "source_registry.json"
        
        self.settings = self._load_json(self.settings_path)
        self.registry = self._load_json(self.registry_path)
        
        # Directories
        dirs = self.settings.get("directories", {})
        self.raw_dir = self.root / dirs.get("raw", "data/raw")
        self.drafts_dir = self.root / dirs.get("drafts", "data/drafts")
        self.review_queue_dir = self.root / dirs.get("review_queue", "data/review_queue")
        self.processed_dir = self.root / dirs.get("processed", "data/processed")
        self.reports_dir = self.root / dirs.get("reports", "data/reports")
        self.fixtures_dir = self.root / dirs.get("fixtures", "data/fixtures")
        
        # Schemas
        schema_paths = self.settings.get("schemas", {})
        self.opportunity_schema_path = self.root / schema_paths.get(
            "opportunity", "schemas/opportunity.schema.json"
        )
        self.extraction_schema_path = self.root / schema_paths.get(
            "extraction", "schemas/extraction.schema.json"
        )

        # Ensure all data directories exist
        for d in [
            self.raw_dir,
            self.drafts_dir,
            self.review_queue_dir,
            self.processed_dir,
            self.reports_dir,
            self.fixtures_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)
            
    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    # LLM Settings
    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", self.settings.get("llm", {}).get("default_provider", "none")).lower()

    @property
    def llm_model(self) -> str:
        return os.getenv("LLM_MODEL", self.settings.get("llm", {}).get("model_name", "gemini-2.5-flash"))

    @property
    def gemini_api_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY")

    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    @property
    def openai_base_url(self) -> str:
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # DB Settings
    @property
    def database_url(self) -> Optional[str]:
        return os.getenv("DATABASE_URL")

    # Schema Validation Settings
    @property
    def allowed_categories(self) -> List[str]:
        return self.settings.get("categories", [])

    @property
    def allowed_education_levels(self) -> List[str]:
        return self.settings.get("education_levels", [])

    @property
    def verification_config(self) -> Dict[str, Any]:
        return self.settings.get("verification", {})

    @property
    def deduplication_config(self) -> Dict[str, Any]:
        return self.settings.get("deduplication", {})


# Global singleton instance
config = Config()
