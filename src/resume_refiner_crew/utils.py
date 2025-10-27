"""Utility functions for resume refiner crew."""

import os
import shutil
from pathlib import Path
from crewai.utilities.paths import db_storage_path


def setup_clean_storage() -> None:
    """Setup clean storage and output directories for crew execution.

    Performs three cleanup operations:
    1. Removes CrewAI's knowledge base storage directory (from db_storage_path())
       and creates a fresh one to prevent knowledge source contamination
    2. Clears all content from .crewai_temp folder if it exists
    3. Clears all content from output/ folder to remove previous execution files

    This ensures that each crew execution starts with clean storage,
    preventing old job descriptions, resume data, or output files from persisting.
    """
    # Clean up CrewAI's knowledge base storage
    storage_dir = Path(db_storage_path())
    if storage_dir.exists():
        shutil.rmtree(storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir.name)

    # Clean up .crewai_temp folder
    crewai_temp_dir = Path(".crewai_temp")
    if crewai_temp_dir.exists():
        shutil.rmtree(crewai_temp_dir)
    crewai_temp_dir.mkdir(parents=True, exist_ok=True)

    # Clean up output folder
    output_dir = Path("output")
    if output_dir.exists():
        # Remove all files and subdirectories
        for item in output_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
