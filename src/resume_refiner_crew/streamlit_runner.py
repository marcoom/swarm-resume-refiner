"""
Streamlit Runner for Resume Refiner Crew

Provides a wrapper function to run the crew with custom parameters
and capture real-time logs for display in the Streamlit UI.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Callable

from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from resume_refiner_crew.utils import setup_clean_storage


class StreamlitLogHandler(logging.Handler):
    """Custom logging handler that streams logs to a callback function."""

    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)


def run_crew_with_params(
    resume_pdf_bytes: bytes,
    job_description: str,
    api_key: str,
    model: str,
    target_words: int,
    log_callback: Optional[Callable[[str], None]] = None
) -> dict:
    """
    Run the Resume Refiner Crew with custom parameters.

    Args:
        resume_pdf_bytes: PDF file content as bytes
        job_description: Job description text
        api_key: OpenAI API key
        model: OpenAI model name (e.g., 'gpt-5-mini')
        target_words: Target resume word count
        log_callback: Optional callback function to receive log messages

    Returns:
        dict with keys:
            - success (bool): Whether execution succeeded
            - error (str): Error message if failed
            - pdf_path (str): Path to generated PDF if successful
            - output_dir (str): Path to output directory
    """
    # Write files directly to knowledge directory (same as CLI)
    knowledge_dir = Path("knowledge")
    knowledge_dir.mkdir(exist_ok=True)

    resume_path = knowledge_dir / "CV.pdf"
    job_desc_path = knowledge_dir / "job_description.txt"

    try:
        # Write uploaded files to knowledge directory
        resume_path.write_bytes(resume_pdf_bytes)
        job_desc_path.write_text(job_description, encoding='utf-8')

        # Set environment variables for this run
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_MODEL'] = model
        os.environ['TARGET_RESUME_WORDS'] = str(target_words)

        # Configure logging
        logger = logging.getLogger()
        original_level = logger.level
        logger.setLevel(logging.INFO)

        # Add custom handler if callback provided
        custom_handler = None
        if log_callback:
            custom_handler = StreamlitLogHandler(log_callback)
            custom_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(custom_handler)

        # Prepare inputs for crew (using same paths as CLI defaults)
        inputs = {
            'TARGET_RESUME_WORDS': str(target_words),
            'RESUME_PDF_PATH': str(resume_path),
            'JOB_DESCRIPTION_PATH': str(job_desc_path)
        }

        # Helper function to safely call log callback
        def safe_log(message: str):
            if log_callback:
                try:
                    log_callback(message)
                except Exception:
                    # Silently ignore logging errors to prevent crashes
                    pass

        safe_log("Initializing Resume Refiner Crew...")

        # Clean storage and create crew
        setup_clean_storage()

        try:
            safe_log("Starting multi-agent pipeline...")

            # TextFileKnowledgeSource prepends knowledge/, PDFSearchTool does not
            crew = ResumeRefinerCrew(
                job_description_path="job_description.txt",
                resume_pdf_path="knowledge/CV.pdf"
            ).crew()
            crew.kickoff(inputs=inputs)

            safe_log("Generating PDF resume with Harvard formatting...")

            pdf_path = generate_resume_pdf_from_json()

            if pdf_path:
                safe_log(f"✓ PDF Resume generated: {pdf_path}")

                return {
                    'success': True,
                    'error': None,
                    'pdf_path': pdf_path,
                    'output_dir': 'output'
                }
            else:
                return {
                    'success': False,
                    'error': 'PDF generation failed',
                    'pdf_path': None,
                    'output_dir': 'output'
                }

        finally:
            # Remove custom handler
            if custom_handler:
                logger.removeHandler(custom_handler)

            # Restore original log level
            logger.setLevel(original_level)

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        # Use safe_log if it's defined, otherwise use log_callback with try-except
        try:
            if log_callback:
                log_callback(f"ERROR: {error_msg}")
        except Exception:
            pass

        return {
            'success': False,
            'error': error_msg,
            'pdf_path': None,
            'output_dir': 'output'
        }
