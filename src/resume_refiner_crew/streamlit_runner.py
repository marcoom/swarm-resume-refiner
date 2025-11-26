"""Streamlit Runner for Resume Refiner Crew.

Provides a wrapper function to run the crew with custom parameters.
Logs are written to .crewai_temp/crew_logs.txt by CrewAI's output_log_file feature.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, TypedDict

from resume_refiner_crew.constants import KNOWLEDGE_DIR, CREWAI_TEMP_DIR, FIXTURES_DIR
from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from resume_refiner_crew.utils import setup_clean_storage, simulate_crew_execution, temporary_env
from resume_refiner_crew.validation import (
    validate_api_key,
    validate_model_name,
    validate_non_empty_string,
    validate_resume_bytes,
    validate_target_words,
)


class CrewResult(TypedDict):
    """Result of crew execution."""

    success: bool
    error: Optional[str]
    pdf_path: Optional[str]
    output_dir: str


def _validate_inputs(
    resume_pdf_bytes: bytes,
    job_description: str,
    api_key: str,
    model: str,
    target_words: int
) -> None:
    """Validate input parameters.

    Args:
        resume_pdf_bytes: PDF file content as bytes.
        job_description: Job description text.
        api_key: OpenAI API key.
        model: OpenAI model name.
        target_words: Target resume word count.

    Raises:
        InvalidInputError: If any input is invalid.
    """
    validate_resume_bytes(resume_pdf_bytes)
    validate_non_empty_string(job_description, "Job description")
    validate_api_key(api_key)
    validate_model_name(model)
    validate_target_words(target_words)


def _is_developer_mode() -> bool:
    """Check if developer mode is enabled."""
    return os.getenv("DEVELOPER_MODE", "false").lower() == "true"


def _run_developer_mode() -> None:
    """Execute crew in developer mode using fixtures."""
    fixture_knowledge_dir = FIXTURES_DIR / "knowledge"
    if fixture_knowledge_dir.exists():
        KNOWLEDGE_DIR.mkdir(exist_ok=True)
        for file_path in fixture_knowledge_dir.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, KNOWLEDGE_DIR / file_path.name)

    setup_clean_storage()
    simulate_crew_execution()


def _run_production_mode(
    resume_pdf_bytes: bytes,
    job_description: str,
    target_words: int,
    enable_report: bool,
    enable_fact_check: bool
) -> None:
    """Execute crew in production mode with actual data.

    Args:
        resume_pdf_bytes: PDF file content as bytes.
        job_description: Job description text.
        target_words: Target resume word count.
        enable_report: Whether to generate a report.
        enable_fact_check: Whether to run fact checker.
    """
    KNOWLEDGE_DIR.mkdir(exist_ok=True)
    resume_path = KNOWLEDGE_DIR / "CV.pdf"
    job_desc_path = KNOWLEDGE_DIR / "job_description.txt"

    resume_path.write_bytes(resume_pdf_bytes)
    job_desc_path.write_text(job_description, encoding='utf-8')

    inputs = {
        'TARGET_RESUME_WORDS': str(target_words),
        'RESUME_PDF_PATH': str(resume_path),
        'JOB_DESCRIPTION_PATH': str(job_desc_path)
    }

    setup_clean_storage()
    CREWAI_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Note: TextFileKnowledgeSource prepends "knowledge/" to job_description_path
    # but PDFSearchTool does not prepend to resume_pdf_path
    crew = ResumeRefinerCrew(
        job_description_path="job_description.txt",
        resume_pdf_path="knowledge/CV.pdf",
        enable_report=enable_report,
        enable_fact_check=enable_fact_check
    ).crew()
    crew.kickoff(inputs=inputs)


def run_crew_with_params(
    resume_pdf_bytes: bytes,
    job_description: str,
    api_key: str,
    model: str,
    target_words: int,
    enable_report: bool = True,
    enable_fact_check: bool = True
) -> CrewResult:
    """Run the Resume Refiner Crew with custom parameters.

    Logs are automatically written to .crewai_temp/crew_logs.txt by CrewAI.

    Args:
        resume_pdf_bytes: PDF file content as bytes.
        job_description: Job description text.
        api_key: OpenAI API key.
        model: OpenAI model name (e.g., 'gpt-5-mini').
        target_words: Target resume word count.
        enable_report: Whether to generate a report.
        enable_fact_check: Whether to run fact checker.

    Returns:
        CrewResult dictionary with execution results.
    """
    try:
        _validate_inputs(resume_pdf_bytes, job_description, api_key, model, target_words)

        with temporary_env(
            OPENAI_API_KEY=api_key,
            OPENAI_MODEL=model,
            TARGET_RESUME_WORDS=str(target_words)
        ):
            if _is_developer_mode():
                _run_developer_mode()
            else:
                _run_production_mode(
                    resume_pdf_bytes,
                    job_description,
                    target_words,
                    enable_report,
                    enable_fact_check
                )

            pdf_path = generate_resume_pdf_from_json()

            if pdf_path:
                return CrewResult(
                    success=True,
                    error=None,
                    pdf_path=pdf_path,
                    output_dir='output'
                )
            else:
                return CrewResult(
                    success=False,
                    error='PDF generation failed',
                    pdf_path=None,
                    output_dir='output'
                )

    except Exception as e:
        return CrewResult(
            success=False,
            error=f"An error occurred: {str(e)}",
            pdf_path=None,
            output_dir='output'
        )
