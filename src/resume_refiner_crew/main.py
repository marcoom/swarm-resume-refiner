#!/usr/bin/env python
import os
import warnings
import logging

from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from resume_refiner_crew.utils import setup_clean_storage

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew and generate PDF resume.
    """
    inputs = {
        'TARGET_RESUME_WORDS': os.getenv("TARGET_RESUME_WORDS", "500")
    }

    try:
        setup_clean_storage()

        logger.info("Starting Resume Refiner Crew...")
        crew = ResumeRefinerCrew().crew()
        crew.kickoff(inputs=inputs)

        logger.info("Generating PDF resume with Harvard formatting from structured data...")
        pdf_path = generate_resume_pdf_from_json()

        if pdf_path:
            logger.info(f"✓ PDF Resume generated: {pdf_path}")
        else:
            logger.warning("PDF generation failed.")

    except Exception as e:
        raise Exception(f"An error occurred: {e}")

if __name__ == "__main__":
    run()