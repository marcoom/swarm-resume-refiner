"""Utility functions for resume refiner crew."""

import logging
import os
import re
import shutil
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from crewai.utilities.paths import db_storage_path

from .constants import CREWAI_TEMP_DIR, OUTPUT_DIR, FIXTURES_DIR, MAX_FILENAME_LENGTH

logger = logging.getLogger(__name__)


def setup_clean_storage() -> None:
    """Setup clean storage and output directories for crew execution.

    Performs three cleanup operations:
    1. Removes CrewAI's knowledge base storage directory (from db_storage_path())
       and creates a fresh one to prevent knowledge source contamination
    2. Clears all content from .crewai_temp folder if it exists
    3. Clears all content from output/ folder to remove previous execution files

    This ensures that each crew execution starts with clean storage,
    preventing old job descriptions, resume data, or output files from persisting.

    Raises:
        PermissionError: If insufficient permissions to clean directories.
        OSError: If directory operations fail.
    """
    try:
        storage_dir = Path(db_storage_path())
        if storage_dir.exists():
            shutil.rmtree(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir.name)
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to clean CrewAI storage: {e}")
        raise

    try:
        if CREWAI_TEMP_DIR.exists():
            shutil.rmtree(CREWAI_TEMP_DIR)
        CREWAI_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to clean temporary directory: {e}")
        raise

    try:
        if OUTPUT_DIR.exists():
            for item in OUTPUT_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to clean output directory: {e}")
        raise


def simulate_crew_execution() -> None:
    """Simulate crew execution for developer mode.

    This function simulates the crew execution by:
    1. Writing simulated log messages to .crewai_temp/crew_logs.txt with 1-second delays
    2. Copying fixture files from tests/fixtures/output/ to output/

    This allows for rapid development iteration without running expensive API calls
    or waiting for the full agent pipeline to complete.

    Raises:
        FileNotFoundError: If fixture directory doesn't exist.
    """
    _write_simulated_logs()
    _copy_fixture_outputs()


def _write_simulated_logs() -> None:
    """Write simulated log messages with delays."""
    CREWAI_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    log_messages = [
        '2025-10-27 13:55:46: task_name="parse_resume_task", task="Use the PDFSearchTool to access and extract content from the resume PDF at: knowledge/CV.pdf',
        '2025-10-27 13:57:02: task_name="parse_resume_task", task="Use the PDFSearchTool to access and extract content from the resume PDF at: knowledge/CV.pdf',
        '2025-10-27 13:57:02: task_name="analyze_job_task", task="Analyze the job description from the provided knowledge source and score the candidate\'s fit based on their resume. Output will be saved as structured JSON data.',
        '2025-10-27 13:58:33: task_name="analyze_job_task", task="Analyze the job description from the provided knowledge source and score the candidate\'s fit based on their resume. Output will be saved as structured JSON data.',
        '2025-10-27 13:58:33: task_name="optimize_resume_task", task="Review the provided resume against the job analysis and create structured optimization suggestions. Output will be saved as structured JSON data.',
        '2025-10-27 13:59:36: task_name="optimize_resume_task", task="Review the provided resume against the job analysis and create structured optimization suggestions. Output will be saved as structured JSON data.',
        '2025-10-27 13:59:36: task_name="generate_resume_task", task="Using the provided resume from context, apply the optimization suggestions from previous steps, to create a polished resume in markdown format. Do not add markdown code blocks like \'```\'.',
        '2025-10-27 14:01:09: task_name="generate_resume_task", task="Using the provided resume from context, apply the optimization suggestions from previous steps, to create a polished resume in markdown format. Do not add markdown code blocks like \'```\'.',
        '2025-10-27 14:01:09: task_name="verify_resume_task", task="Cross-reference the optimized resume against the original resume to ensure factual accuracy (source of truth is the original resume). Remove any hallucinated, embellished, or unverifiable content. If everything is correct, then return the optimized resume without changes. If you encounter a mismatch, fix it with the minimal changes possible.',
        '2025-10-27 14:02:07: task_name="verify_resume_task", task="Cross-reference the optimized resume against the original resume to ensure factual accuracy (source of truth is the original resume). Remove any hallucinated, embellished, or unverifiable content. If everything is correct, then return the optimized resume without changes. If you encounter a mismatch, fix it with the minimal changes possible.2025-10-27 14:02:07: task_name="harvard_format_task", task="Parse the verified markdown resume and structure it into Harvard format with precise data extraction.',
        '2025-10-27 14:05:56: task_name="harvard_format_task", task="Parse the verified markdown resume and structure it into Harvard format with precise data extraction.',
        '2025-10-27 14:05:56: task_name="generate_report_task", task="Create an executive summary report using data from previous steps. Format in markdown without code blocks \'```\'. The output must be ONLY the report in markdown format - no introductions, no conclusions, no commentary.',
        '2025-10-27 14:06:32: task_name="generate_report_task", task="Create an executive summary report using data from previous steps. Format in markdown without code blocks \'```\'. The output must be ONLY the report in markdown format - no introductions, no conclusions, no commentary.',
    ]

    log_file = CREWAI_TEMP_DIR / "crew_logs.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        for message in log_messages:
            f.write(message + '\n')
            f.flush()
            time.sleep(1)


def _copy_fixture_outputs() -> None:
    """Copy fixture output files to output directory."""
    fixture_output_dir = FIXTURES_DIR / "output"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not fixture_output_dir.exists():
        raise FileNotFoundError(
            f"Fixture output directory not found: {fixture_output_dir}\n"
            "Please ensure tests/fixtures/output/ exists with sample output files."
        )

    for file_path in fixture_output_dir.iterdir():
        if file_path.is_file():
            shutil.copy2(file_path, OUTPUT_DIR / file_path.name)


def sanitize_for_filename(text: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """Sanitize string for use in filename.

    Args:
        text: The text to sanitize.
        max_length: Maximum length for the sanitized filename.

    Returns:
        Sanitized string safe for use in filenames.

    Examples:
        >>> sanitize_for_filename("Hello World!")
        'Hello_World'
        >>> sanitize_for_filename("test  /  file.txt")
        'test_file_txt'
    """
    sanitized = re.sub(r'[^\w\s-]', '', text)
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized


@contextmanager
def temporary_env(**kwargs: Any) -> Iterator[None]:
    """Context manager for temporary environment variables.

    Sets environment variables for the duration of the context and restores
    original values afterward.

    Args:
        **kwargs: Environment variable name-value pairs to set temporarily.

    Yields:
        None

    Examples:
        >>> with temporary_env(OPENAI_MODEL="gpt-4", TARGET_WORDS="600"):
        ...     # Environment variables are set
        ...     pass
        # Original values are restored
    """
    old_env: Dict[str, Optional[str]] = {}
    for key, value in kwargs.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = str(value)

    try:
        yield
    finally:
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def validate_path_exists(path: Path, file_type: str = "file") -> None:
    """Validate that a path exists.

    Args:
        path: The path to validate.
        file_type: Type description for error messages (e.g., "resume", "config").

    Raises:
        FileNotFoundError: If the path doesn't exist.
        ValueError: If path is not a file when expected.
    """
    if not path.exists():
        raise FileNotFoundError(f"{file_type.capitalize()} not found: {path}")

    if file_type != "directory" and path.is_dir():
        raise ValueError(f"Expected file but got directory: {path}")
