"""Utility functions for resume refiner crew."""

import os
import shutil
import time
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


def simulate_crew_execution() -> None:
    """Simulate crew execution for developer mode.

    This function simulates the crew execution by:
    1. Writing simulated log messages to .crewai_temp/crew_logs.txt with 1-second delays
    2. Copying fixture files from tests/fixtures/output/ to output/

    This allows for rapid development iteration without running expensive API calls
    or waiting for the full agent pipeline to complete.
    """
    # Ensure .crewai_temp directory exists
    crewai_temp_dir = Path(".crewai_temp")
    crewai_temp_dir.mkdir(parents=True, exist_ok=True)

    # Define simulated log messages (from user specification)
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

    # Write log messages with 1-second delay between each
    log_file = crewai_temp_dir / "crew_logs.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        for message in log_messages:
            f.write(message + '\n')
            f.flush()  # Ensure message is written immediately
            time.sleep(1)  # 1-second delay between messages

    # Copy fixture files from tests/fixtures/output to output/
    fixture_output_dir = Path("tests/fixtures/output")
    output_dir = Path("output")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files from fixture output to output
    if fixture_output_dir.exists():
        for file_path in fixture_output_dir.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, output_dir / file_path.name)
    else:
        raise FileNotFoundError(
            f"Fixture output directory not found: {fixture_output_dir}\n"
            "Please ensure tests/fixtures/output/ exists with sample output files."
        )
