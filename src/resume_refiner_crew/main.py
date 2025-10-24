#!/usr/bin/env python
import os
import shutil
import warnings
import logging

from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.pdf_generator import generate_resume_pdf

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
        storage_dir = "./.crewai_temp"
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)
        os.makedirs(storage_dir)
        os.environ["CREWAI_STORAGE_DIR"] = storage_dir

        logger.info("Starting Resume Refiner Crew...")
        crew = ResumeRefinerCrew().crew()
        crew.kickoff(inputs=inputs)

        logger.info("\n" + "="*60)
        logger.info("Crew execution completed successfully!")
        logger.info("="*60 + "\n")

        # Generate PDF from the verified resume
        logger.info("Generating PDF resume with Harvard template...")
        pdf_path = generate_resume_pdf()

        if pdf_path:
            logger.info("\n" + "="*60)
            logger.info(f"✓ PDF Resume generated: {pdf_path}")
            logger.info("="*60 + "\n")
        else:
            logger.warning("\n" + "="*60)
            logger.warning("PDF generation failed or skipped.")
            logger.warning("Note: Ensure pypandoc and pdflatex are installed.")
            logger.warning("="*60 + "\n")

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()