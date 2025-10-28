#!/usr/bin/env python
"""Main entry point for Resume Refiner Crew CLI."""

import argparse
import logging
import os
import sys
import warnings
from typing import Dict

from resume_refiner_crew.constants import (
    DEFAULT_TARGET_WORDS,
    DEFAULT_RESUME_PATH,
    DEFAULT_JOB_DESC_PATH,
)
from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from resume_refiner_crew.utils import setup_clean_storage, simulate_crew_execution

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Resume Refiner Crew - Optimize resumes with AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--resume",
        default=os.getenv("RESUME_PDF_PATH", str(DEFAULT_RESUME_PATH)),
        help="Path to resume PDF"
    )
    parser.add_argument(
        "--job-description",
        dest="job_description",
        default=os.getenv("JOB_DESCRIPTION_PATH", str(DEFAULT_JOB_DESC_PATH)),
        help="Path to job description text file"
    )
    parser.add_argument(
        "--target-words",
        dest="target_words",
        type=int,
        default=int(os.getenv("TARGET_RESUME_WORDS", str(DEFAULT_TARGET_WORDS))),
        help="Target word count for resume"
    )
    parser.add_argument(
        "--developer-mode",
        dest="developer_mode",
        action="store_true",
        default=os.getenv("DEVELOPER_MODE", "false").lower() == "true",
        help="Use fixture data instead of running API calls"
    )
    return parser.parse_args()


def validate_environment() -> None:
    """Validate required environment variables.

    Raises:
        SystemExit: If required environment variables are missing.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required")
        sys.exit(1)


def run_developer_mode() -> None:
    """Run in developer mode with fixture data."""
    logger.info("Developer Mode: Simulating crew execution with fixture data...")
    setup_clean_storage()
    simulate_crew_execution()
    logger.info("Simulation complete. Output files are ready.")


def run_production_mode(inputs: Dict[str, str]) -> None:
    """Run in production mode with actual API calls.

    Args:
        inputs: Dictionary containing crew execution inputs.
    """
    setup_clean_storage()
    logger.info("Starting Resume Refiner Crew...")
    crew = ResumeRefinerCrew(
        job_description_path=inputs['JOB_DESCRIPTION_PATH'],
        resume_pdf_path=inputs['RESUME_PDF_PATH']
    ).crew()
    crew.reset_memories(command_type='knowledge')
    crew.reset_memories(command_type='all')
    crew.reset_memories(command_type='agent_knowledge')
    crew.kickoff(inputs=inputs)


def generate_pdf() -> None:
    """Generate final PDF resume."""
    logger.info("Generating PDF resume with Harvard formatting...")
    pdf_path = generate_resume_pdf_from_json()

    if pdf_path:
        logger.info(f"PDF Resume generated: {pdf_path}")
    else:
        logger.warning("PDF generation failed")


def run() -> None:
    """Run the resume refiner crew."""
    validate_environment()
    args = parse_args()

    inputs = {
        'TARGET_RESUME_WORDS': str(args.target_words),
        'RESUME_PDF_PATH': args.resume,
        'JOB_DESCRIPTION_PATH': args.job_description
    }

    try:
        if args.developer_mode:
            run_developer_mode()
        else:
            run_production_mode(inputs)

        generate_pdf()

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()