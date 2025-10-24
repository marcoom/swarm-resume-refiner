"""
PDF Generator for Resume Refiner Crew

Converts the verified markdown resume to PDF using pypandoc with Harvard template.
Extracts candidate name and job title to generate properly named output file.
"""

import json
import os
import re
from pathlib import Path
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_name_from_markdown(markdown_path: str) -> Tuple[str, str, str]:
    """
    Extract candidate's name from the first heading in the markdown file.

    Args:
        markdown_path: Path to the verified_resume.md file

    Returns:
        Tuple of (full_name, first_name, last_name)
    """
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the first heading (# Name)
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not match:
            raise ValueError("No name heading found in markdown file")

        full_name = match.group(1).strip()

        # Split name into first and last
        name_parts = full_name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
        else:
            first_name = full_name
            last_name = ""

        logger.info(f"Extracted name: {full_name} (First: {first_name}, Last: {last_name})")
        return full_name, first_name, last_name

    except Exception as e:
        logger.error(f"Error extracting name from markdown: {e}")
        return "Unknown", "Unknown", "Unknown"


def extract_job_title_from_json(json_path: str) -> str:
    """
    Extract job title from the job analysis JSON file.

    Args:
        json_path: Path to the job_analysis.json file

    Returns:
        Job title as string
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        job_title = data.get('job_title', 'Position')
        logger.info(f"Extracted job title: {job_title}")
        return job_title

    except Exception as e:
        logger.error(f"Error extracting job title from JSON: {e}")
        return "Position"


def sanitize_for_filename(text: str) -> str:
    """
    Sanitize a string for use in a filename.
    Removes special characters and replaces spaces with underscores.

    Args:
        text: String to sanitize

    Returns:
        Sanitized string safe for filenames
    """
    # Remove or replace problematic characters
    # Keep alphanumeric, spaces, hyphens, and underscores
    sanitized = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim underscores from ends
    sanitized = sanitized.strip('_')

    return sanitized


def preprocess_markdown(markdown_path: str) -> str:
    """
    Preprocess the markdown to better match Harvard template formatting.
    Adds LaTeX commands for the name header with horizontal rule.

    Args:
        markdown_path: Path to the markdown file

    Returns:
        Preprocessed markdown content as string
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the first heading (name) and the contact line
    lines = content.split('\n')

    # Find the name (first # heading)
    name_idx = None
    for i, line in enumerate(lines):
        if line.startswith('# '):
            name_idx = i
            break

    if name_idx is not None and name_idx + 1 < len(lines):
        name = lines[name_idx].replace('# ', '').strip()
        contact = lines[name_idx + 1].strip()

        # Create custom LaTeX header
        latex_header = f"""\\begin{{center}}
    \\textbf{{{name}}}\\\\
    \\hrulefill
\\end{{center}}

\\begin{{center}}
    {contact}
\\end{{center}}

\\vspace{{0.5pt}}
"""

        # Replace the first two lines with the custom header
        # Remove the # heading and contact line
        lines[name_idx] = latex_header
        if name_idx + 1 < len(lines):
            lines[name_idx + 1] = ""

        content = '\n'.join(lines)

    return content


def generate_resume_pdf(
    markdown_path: str = "output/verified_resume.md",
    job_analysis_path: str = "output/job_analysis.json",
    template_path: str = "templates/harvard_resume_pandoc.tex",
    output_dir: str = "output"
) -> Optional[str]:
    """
    Generate a PDF resume from markdown using pypandoc with Harvard template.

    Args:
        markdown_path: Path to the verified markdown resume
        job_analysis_path: Path to the job analysis JSON file
        template_path: Path to the Pandoc LaTeX template
        output_dir: Directory to save the output PDF

    Returns:
        Path to the generated PDF file, or None if generation failed
    """
    try:
        import pypandoc

        logger.info("Starting PDF generation...")

        # Get absolute paths
        base_dir = Path.cwd()
        markdown_path = base_dir / markdown_path
        job_analysis_path = base_dir / job_analysis_path
        template_path = base_dir / template_path
        output_dir = base_dir / output_dir

        # Verify input files exist
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return None

        if not template_path.exists():
            logger.error(f"Template file not found: {template_path}")
            return None

        # Extract name and job title
        full_name, first_name, last_name = extract_name_from_markdown(str(markdown_path))
        job_title = extract_job_title_from_json(str(job_analysis_path))

        # Sanitize for filename
        first_name_clean = sanitize_for_filename(first_name)
        last_name_clean = sanitize_for_filename(last_name)
        job_title_clean = sanitize_for_filename(job_title)

        # Generate output filename
        output_filename = f"CV_{last_name_clean}_{first_name_clean}_{job_title_clean}.pdf"
        output_path = output_dir / output_filename

        logger.info(f"Output PDF will be: {output_filename}")

        # Preprocess markdown
        processed_content = preprocess_markdown(str(markdown_path))

        # Create temporary file for preprocessed markdown
        temp_md_path = output_dir / "temp_processed_resume.md"
        with open(temp_md_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        # Convert using pypandoc
        logger.info("Converting markdown to PDF with pypandoc...")

        pypandoc.convert_file(
            str(temp_md_path),
            'pdf',
            outputfile=str(output_path),
            extra_args=[
                f'--template={template_path}',
                '--pdf-engine=pdflatex',
                '-V', 'geometry:margin=1cm',
            ]
        )

        # Clean up temporary file
        temp_md_path.unlink()

        logger.info(f"✓ PDF generated successfully: {output_path}")
        return str(output_path)

    except ImportError:
        logger.error("pypandoc is not installed. Please install it with: pip install pypandoc")
        logger.error("Note: You also need pandoc and pdflatex installed on your system.")
        return None

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    # Allow running directly for testing
    result = generate_resume_pdf()
    if result:
        print(f"Success! PDF generated at: {result}")
    else:
        print("Failed to generate PDF")
