"""Utility functions for resume refiner crew."""

import os
import shutil
from pathlib import Path
from crewai.utilities.paths import db_storage_path


def setup_clean_storage() -> None:
    """Setup clean storage directory for crew knowledge base.

    Removes existing .crewai_temp directory in the project root and creates
    a fresh one to prevent knowledge source contamination across runs.

    This ensures that each crew execution starts with a clean Chroma DB,
    preventing old job descriptions or resume data from persisting.
    """
    storage_dir = Path(db_storage_path())

    # Clean up existing storage
    if storage_dir.exists():
        shutil.rmtree(storage_dir)

    # Create fresh storage directory
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variable for crewAI to use this directory
    os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir.name)
