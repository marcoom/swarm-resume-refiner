"""
Streamlit Runner for Resume Refiner Crew

Provides a wrapper function to run the crew with custom parameters.
Logs are written to .crewai_temp/crew_logs.txt by CrewAI's output_log_file feature.
"""

import os
from pathlib import Path

from resume_refiner_crew.crew import ResumeRefinerCrew
from resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from resume_refiner_crew.utils import setup_clean_storage


def run_crew_with_params(
    resume_pdf_bytes: bytes,
    job_description: str,
    api_key: str,
    model: str,
    target_words: int
) -> dict:
    """
    Run the Resume Refiner Crew with custom parameters.

    Logs are automatically written to .crewai_temp/crew_logs.txt by CrewAI.

    Args:
        resume_pdf_bytes: PDF file content as bytes
        job_description: Job description text
        api_key: OpenAI API key
        model: OpenAI model name (e.g., 'gpt-5-mini')
        target_words: Target resume word count

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

        # Prepare inputs for crew (using same paths as CLI defaults)
        inputs = {
            'TARGET_RESUME_WORDS': str(target_words),
            'RESUME_PDF_PATH': str(resume_path),
            'JOB_DESCRIPTION_PATH': str(job_desc_path)
        }

        # Clean storage and create crew
        setup_clean_storage()

        # Ensure .crewai_temp directory exists for log file
        crewai_temp = Path(".crewai_temp")
        crewai_temp.mkdir(parents=True, exist_ok=True)

        # TextFileKnowledgeSource prepends knowledge/, PDFSearchTool does not
        crew = ResumeRefinerCrew(
            job_description_path="job_description.txt",
            resume_pdf_path="knowledge/CV.pdf"
        ).crew()
        crew.kickoff(inputs=inputs)

        # Generate PDF resume with Harvard formatting
        pdf_path = generate_resume_pdf_from_json()

        if pdf_path:
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

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        return {
            'success': False,
            'error': error_msg,
            'pdf_path': None,
            'output_dir': 'output'
        }
