"""Constants used across the Resume Refiner Crew application.

This module centralizes all magic numbers, hardcoded paths, and configuration
values to maintain consistency and improve maintainability.
"""

from pathlib import Path
from typing import Dict, Tuple

# Directory Paths
CREWAI_TEMP_DIR = Path(".crewai_temp")
OUTPUT_DIR = Path("output")
FIXTURES_DIR = Path("tests/fixtures")
KNOWLEDGE_DIR = Path("knowledge")
CONFIG_DIR = Path("config")

# Configuration Files
AGENTS_CONFIG = CONFIG_DIR / "agents.yaml"
TASKS_CONFIG = CONFIG_DIR / "tasks.yaml"

# Default Input/Output Paths
DEFAULT_RESUME_PATH = KNOWLEDGE_DIR / "CV.pdf"
DEFAULT_JOB_DESC_PATH = Path("job_description.txt")  # TextFileKnowledgeSource will prepend "knowledge/"
DEFAULT_RESUME_BEST_PRACTICES_PATH = Path("resume_best_practices.txt")  # TextFileKnowledgeSource will prepend "knowledge/"
FIXTURE_LOGS_FILE = FIXTURES_DIR / "crew_logs.txt"
CREW_LOGS_FILE = CREWAI_TEMP_DIR / "crew_logs.txt"

# Output File Names
PARSED_RESUME_FILE = OUTPUT_DIR / "parsed_resume.md"
JOB_ANALYSIS_FILE = OUTPUT_DIR / "job_analysis.json"
RESUME_OPTIMIZATION_FILE = OUTPUT_DIR / "resume_optimization.json"
OPTIMIZED_RESUME_FILE = OUTPUT_DIR / "optimized_resume.md"
VERIFIED_RESUME_FILE = OUTPUT_DIR / "verified_resume.md"
STRUCTURED_RESUME_FILE = OUTPUT_DIR / "structured_resume.json"
FINAL_REPORT_FILE = OUTPUT_DIR / "final_report.md"

# Word Count Configuration
DEFAULT_TARGET_WORDS = 500
MIN_TARGET_WORDS = 300
MAX_TARGET_WORDS = 1000
WORD_COUNT_TOLERANCE_MIN = 0.85
WORD_COUNT_TOLERANCE_MAX = 1.15
DEFAULT_RESUME_LANGUAGE = "Auto"

# LaTeX Configuration
LATEX_VSPACE_SECTION = "\\vspace{12pt}"
LATEX_VSPACE_SMALL = "\\vspace{6pt}"
LATEX_VSPACE_LARGE = "\\vspace{18pt}"

# PDF Generation
PDF_FILENAME_TEMPLATE = "CV_{last_name}_{first_name}_{job_title}.pdf"

# OpenAI Configuration
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# Streamlit Progress Tracking
# Maps task names to (position, agent_name, status_text)
TASKS_INFO: Dict[str, Tuple[int, str, str]] = {
    "parse_resume_task": (1, "Resume PDF Parser", "Parsing your resume"),
    "analyze_job_task": (2, "Job Analyzer", "Analyzing the provided job description"),
    "optimize_resume_task": (3, "Resume Analyzer", "Identifying improvements to be made"),
    "generate_resume_task": (4, "Resume Writer", "Generating optimized resume"),
    "verify_resume_task": (5, "Fact Checker", "Verifying resume accuracy"),
    "harvard_format_task": (6, "Harvard Formatter", "Formatting resume structure"),
    "generate_report_task": (7, "Report Generator", "Generating final report"),
}

TOTAL_TASKS = len(TASKS_INFO)

# Validation Limits
MAX_FILENAME_LENGTH = 255
MIN_API_KEY_LENGTH = 20
MIN_TARGET_WORDS = 100
MAX_TARGET_WORDS_LIMIT = 2000

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Scoring Weights (for JobRequirements)
DEFAULT_SCORING_FACTORS = {
    "technical_skills": 0.35,
    "soft_skills": 0.20,
    "experience": 0.25,
    "education": 0.10,
    "industry": 0.10,
}
