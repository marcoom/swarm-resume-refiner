"""LaTeX Generator for Harvard-Formatted Resumes.

Generates LaTeX directly from structured resume JSON data and compiles to PDF.
Implements Harvard resume formatting standards with proper alignment and styling.
"""

import json
import re
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..constants import (
    JOB_ANALYSIS_FILE,
    LATEX_VSPACE_SECTION,
)
from ..utils import sanitize_for_filename

logger = logging.getLogger(__name__)


def escape_latex(text: str) -> str:
    r"""
    Escape special LaTeX characters in text.

    IMPORTANT: Backslashes must be escaped FIRST, before any other
    replacements that introduce backslashes (like % -> \%).
    Otherwise, the backslashes we add get escaped again.

    Args:
        text: String to escape

    Returns:
        LaTeX-safe string
    """
    # Escape backslashes FIRST, before adding any LaTeX commands
    text = text.replace('\\', r'\textbackslash{}')

    # Now escape other special characters (order doesn't matter for these)
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def format_section_title(title: str) -> str:
    """
    Format section title to Title Case with proper word spacing.

    Converts underscores and hyphens to spaces, normalizes whitespace,
    and applies Title Case formatting.

    Args:
        title: Raw section title string

    Returns:
        Formatted title in Title Case with space-separated words

    Examples:
        >>> format_section_title("volunteer_work")
        "Volunteer Work"
        >>> format_section_title("AWARDS")
        "Awards"
        >>> format_section_title("professional-development")
        "Professional Development"
    """
    if not title:
        return title

    # Replace underscores and hyphens with spaces
    formatted = title.replace('_', ' ').replace('-', ' ')

    # Normalize multiple spaces to single space
    formatted = re.sub(r'\s+', ' ', formatted)

    # Apply Title Case
    formatted = formatted.title()

    # Strip leading/trailing spaces
    formatted = formatted.strip()

    return formatted


def bold_keywords(text: str, keywords: List[str]) -> str:
    """
    Apply bold formatting to specific keywords in text.

    Uses a placeholder approach to avoid regex/escaping issues:
    1. Find keywords in original text and replace with placeholders
    2. Escape the entire text (placeholders remain safe)
    3. Replace placeholders with \\textbf{escaped_keyword}

    Args:
        text: The text to process
        keywords: List of keywords to make bold

    Returns:
        Text with keywords wrapped in \\textbf{}
    """
    if not keywords:
        return escape_latex(text)

    # Work with original unescaped text
    result = text

    # Sort keywords by length (longest first) to avoid partial matches
    sorted_keywords = sorted(keywords, key=len, reverse=True)

    # Replace keywords with unique placeholders
    placeholders = {}
    for i, keyword in enumerate(sorted_keywords):
        placeholder = f"<<<BOLD{i}>>>"

        # Find keyword (case-insensitive)
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        match = pattern.search(result)

        if match:
            # Get the actual matched text (preserves original case)
            matched_text = match.group()
            # Replace with placeholder (only first occurrence)
            result = result.replace(matched_text, placeholder, 1)
            # Store mapping
            placeholders[placeholder] = matched_text

    # Now escape the entire text (placeholders are safe from escaping)
    result = escape_latex(result)

    # Replace placeholders with bolded, escaped keywords
    for placeholder, original_keyword in placeholders.items():
        # Escape the original keyword
        escaped_keyword = escape_latex(original_keyword)
        # Create bold version
        bolded = f"\\textbf{{{escaped_keyword}}}"
        # Replace placeholder
        result = result.replace(placeholder, bolded)

    return result


def generate_work_experience_section(experiences: List[Dict]) -> str:
    """Generate LaTeX for work experience section."""
    if not experiences:
        return ""

    latex = r"""\begin{center}
    \textbf{Work Experience}
\end{center}

"""

    for exp in experiences:
        institution = escape_latex(exp.get('institution', ''))
        location = exp.get('location', '')
        roles = exp.get('roles', [])
        date_start = exp.get('date_start', '')
        date_end = exp.get('date_end', '')
        achievements = exp.get('achievements', [])
        keywords = exp.get('keywords_to_bold', [])

        # First line: Institution \hfill Location
        if location:
            latex += f"\\textbf{{{institution}}} \\hfill {escape_latex(location)}\n\n"
        else:
            latex += f"\\textbf{{{institution}}}\n\n"

        # Second line: Roles \hfill Dates
        roles_str = escape_latex(', '.join(roles)) if roles else ""
        dates_str = f"{escape_latex(date_start)} -- {escape_latex(date_end)}"

        if roles_str:
            latex += f"\\textbf{{{roles_str}}} \\hfill {dates_str}\n"
        else:
            latex += f"\\hfill {dates_str}\n"

        # Achievements as bullet points
        if achievements:
            latex += r"\begin{itemize}[noitemsep, topsep=0pt, partopsep=0pt, parsep=0pt]" + "\n"
            for achievement in achievements:
                # Apply bold to keywords
                formatted_achievement = bold_keywords(achievement, keywords)
                latex += f"    \\item {formatted_achievement}\n"
            latex += r"\end{itemize}" + "\n"

        latex += f"\n{LATEX_VSPACE_SECTION}\n\n"

    return latex


def generate_education_section(education_list: List[Dict]) -> str:
    """Generate LaTeX for education section."""
    if not education_list:
        return ""

    latex = r"""\begin{center}
    \textbf{Education}
\end{center}

"""

    for edu in education_list:
        institution = escape_latex(edu.get('institution', ''))
        location = edu.get('location', '')
        degree = escape_latex(edu.get('degree', ''))
        year_start = edu.get('year_start', '')
        year_end = edu.get('year_end', '')
        additional_info = edu.get('additional_info', '')

        # First line: Institution \hfill Location
        if location:
            latex += f"\\textbf{{{institution}}} \\hfill {escape_latex(location)}\n\n"
        else:
            latex += f"\\textbf{{{institution}}}\n\n"

        # Second line: Degree \hfill Years
        years_str = ""
        if year_start and year_end:
            if year_start == year_end:
                years_str = escape_latex(year_end)
            else:
                years_str = f"{escape_latex(year_start)} -- {escape_latex(year_end)}"
        elif year_end:
            years_str = escape_latex(year_end)
        elif year_start:
            years_str = escape_latex(year_start)

        if years_str:
            latex += f"{degree} \\hfill {years_str}\n"
        else:
            latex += f"{degree}\n"

        # Additional info
        if additional_info:
            latex += f"\n{escape_latex(additional_info)}\n"

        latex += f"\n{LATEX_VSPACE_SECTION}\n\n"

    return latex


def generate_summary_section(summary: Optional[str]) -> str:
    """Generate LaTeX for summary/objective section."""
    if not summary:
        return ""

    latex = r"""\begin{center}
    \textbf{Summary}
\end{center}

"""
    latex += f"{escape_latex(summary)}\n\n"
    latex += f"{LATEX_VSPACE_SECTION}\n\n"

    return latex


def generate_certifications_section(certifications: List[Dict]) -> str:
    """Generate LaTeX for certifications section."""
    if not certifications:
        return ""

    latex = r"""\begin{center}
    \textbf{Courses and Certifications}
\end{center}

"""

    for cert in certifications:
        year = escape_latex(cert.get('year', ''))
        name = escape_latex(cert.get('name', ''))
        provider = escape_latex(cert.get('provider', ''))
        grade = cert.get('grade', '')

        # Format: year | name | provider | grade
        parts = [year, name, provider]
        if grade:
            parts.append(escape_latex(grade))

        cert_line = ' | '.join(parts)
        latex += f"{cert_line}\n\n"

    latex += f"{LATEX_VSPACE_SECTION}\n\n"
    return latex


def generate_skills_section(skills: Optional[Dict[str, List[str]]]) -> str:
    """Generate LaTeX for skills section."""
    if not skills:
        return ""

    latex = r"""\begin{center}
    \textbf{Skills}
\end{center}

"""

    for category, skill_list in skills.items():
        category_escaped = escape_latex(category)
        skills_str = escape_latex(', '.join(skill_list))
        latex += f"\\textbf{{{category_escaped}:}} {skills_str}\n\n"

    latex += f"{LATEX_VSPACE_SECTION}\n\n"
    return latex


def render_mixed_content(content: List[Union[str, List[str]]]) -> str:
    """Render mixed content (paragraphs and lists) to LaTeX.

    Args:
        content: List of content blocks where each block is either:
                 - str: A paragraph of text
                 - List[str]: A bullet list

    Returns:
        LaTeX-formatted string
    """
    latex = ""

    for block in content:
        if isinstance(block, str):
            # This is a paragraph
            latex += f"{escape_latex(block)}\n\n"
        elif isinstance(block, list):
            # This is a bullet list
            latex += r"\begin{itemize}[noitemsep, topsep=0pt, partopsep=0pt, parsep=0pt]" + "\n"
            for item in block:
                latex += f"    \\item {escape_latex(item)}\n"
            latex += r"\end{itemize}" + "\n\n"

    return latex


def generate_additional_sections(
    languages: Optional[List] = None,
    projects: Optional[List] = None,
    additional_sections: Optional[Dict] = None
) -> str:
    """Generate LaTeX for additional sections."""
    latex = ""

    # Languages
    if languages:
        latex += r"""\begin{center}
    \textbf{Languages}
\end{center}

"""
        latex += render_mixed_content(languages)
        latex += f"{LATEX_VSPACE_SECTION}\n\n"

    # Projects
    if projects:
        latex += r"""\begin{center}
    \textbf{Projects}
\end{center}

"""
        latex += render_mixed_content(projects)
        latex += f"{LATEX_VSPACE_SECTION}\n\n"

    # Additional sections
    if additional_sections:
        for section_name, section_content in additional_sections.items():
            section_name_formatted = format_section_title(section_name)
            section_name_escaped = escape_latex(section_name_formatted)
            latex += r"\begin{center}" + "\n"
            latex += f"    \\textbf{{{section_name_escaped}}}\n"
            latex += r"\end{center}" + "\n\n"

            latex += render_mixed_content(section_content)

            latex += f"{LATEX_VSPACE_SECTION}\n\n"

    return latex


def generate_complete_latex(resume_data: Dict) -> str:
    """
    Generate complete LaTeX document from structured resume data.

    Args:
        resume_data: Dictionary containing HarvardFormattedResume data

    Returns:
        Complete LaTeX document as string
    """
    # Extract metadata
    candidate_name = resume_data.get('candidate_name', 'Candidate Name')
    contact_info = resume_data.get('contact_info', '')

    # Start LaTeX document
    latex = r"""\documentclass[11pt]{article}
\usepackage{graphicx}
\setlength{\parindent}{0pt}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage[left=1.06cm,top=1.7cm,right=1.06cm,bottom=0.49cm]{geometry}

% Hyperref setup
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    urlcolor=blue,
    pdfborder={0 0 0}
}

\begin{document}

% Header: Name and Contact
\begin{center}
    \textbf{""" + escape_latex(candidate_name) + r"""}\\
    \hrulefill
\end{center}

\begin{center}
    """ + escape_latex(contact_info) + r"""
\end{center}

\vspace{0.5pt}

"""

    # Add sections in order: Summary, Work Experience, Education, then others
    latex += generate_summary_section(resume_data.get('summary'))
    latex += generate_work_experience_section(resume_data.get('work_experience', []))
    latex += generate_education_section(resume_data.get('education', []))
    latex += generate_certifications_section(resume_data.get('certifications', []))
    latex += generate_skills_section(resume_data.get('skills'))
    latex += generate_additional_sections(
        languages=resume_data.get('languages'),
        projects=resume_data.get('projects'),
        additional_sections=resume_data.get('additional_sections')
    )

    latex += r"\end{document}"

    return latex


def compile_latex_to_pdf(
    tex_content: str,
    output_dir: Path,
    filename_base: str
) -> Optional[str]:
    """Compile LaTeX content to PDF.

    Args:
        tex_content: LaTeX document content.
        output_dir: Directory to save output files.
        filename_base: Base name for output files (without extension).

    Returns:
        Path to generated PDF, or None if compilation failed.

    Raises:
        FileNotFoundError: If pdflatex is not installed.
        subprocess.TimeoutExpired: If compilation exceeds timeout.
    """
    tex_path = output_dir / f"{filename_base}.tex"

    try:
        _write_tex_file(tex_path, tex_content)
        _run_pdflatex(tex_path, output_dir)
        _cleanup_auxiliary_files(output_dir, filename_base, tex_path)

        pdf_path = output_dir / f"{filename_base}.pdf"
        if pdf_path.exists():
            logger.info(f"PDF generated successfully: {pdf_path}")
            return str(pdf_path)
        else:
            logger.error("PDF file was not created")
            return None

    except subprocess.TimeoutExpired:
        logger.error("LaTeX compilation timed out")
        return None
    except FileNotFoundError:
        logger.error("pdflatex not found. Please install a LaTeX distribution.")
        return None
    except Exception as e:
        logger.error(f"Error compiling LaTeX: {e}", exc_info=True)
        return None


def _write_tex_file(tex_path: Path, content: str) -> None:
    """Write LaTeX content to file."""
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"LaTeX file written: {tex_path}")


def _run_pdflatex(tex_path: Path, output_dir: Path) -> None:
    """Run pdflatex compiler."""
    logger.info("Compiling LaTeX to PDF...")
    subprocess.run(
        [
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory',
            str(output_dir),
            str(tex_path)
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=True
    )


def _cleanup_auxiliary_files(
    output_dir: Path,
    filename_base: str,
    tex_path: Path
) -> None:
    """Clean up auxiliary LaTeX files."""
    for ext in ['.aux', '.log', '.out', '.tex']:
        aux_file = output_dir / f"{filename_base}{ext}"
        if aux_file.exists():
            aux_file.unlink()

    if tex_path.exists():
        tex_path.unlink()


def _load_resume_data(json_path: Path) -> Dict:
    """Load structured resume data from JSON file."""
    if not json_path.exists():
        raise FileNotFoundError(f"Structured resume JSON not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_job_title(job_analysis_path: Path) -> str:
    """Load job title from job analysis file."""
    if not job_analysis_path.exists():
        logger.warning("job_analysis.json not found, using default job title")
        return 'Position'

    with open(job_analysis_path, 'r', encoding='utf-8') as f:
        job_analysis = json.load(f)

    return job_analysis.get('job_title', 'Position')


def _extract_candidate_names(candidate_name: str) -> Tuple[str, str]:
    """Extract first and last names from candidate name string."""
    name_parts = candidate_name.split()
    if len(name_parts) >= 2:
        return name_parts[0], name_parts[-1]
    return candidate_name, ""


def _generate_pdf_filename(
    first_name: str,
    last_name: str,
    job_title: str
) -> str:
    """Generate PDF filename from candidate and job information."""
    first_clean = sanitize_for_filename(first_name)
    last_clean = sanitize_for_filename(last_name)
    title_clean = sanitize_for_filename(job_title)

    return f"CV_{last_clean}_{first_clean}_{title_clean}"


def generate_resume_pdf_from_json(
    json_path: str = "output/structured_resume.json",
    output_dir: str = "output"
) -> Optional[str]:
    """Generate PDF resume from structured JSON data.

    Args:
        json_path: Path to structured_resume.json file.
        output_dir: Directory to save output PDF.

    Returns:
        Path to generated PDF, or None if generation failed.
    """
    try:
        logger.info("Starting PDF generation from structured data...")

        base_dir = Path.cwd()
        json_full_path = base_dir / json_path
        output_full_dir = base_dir / output_dir

        resume_data = _load_resume_data(json_full_path)
        logger.info("Structured resume data loaded successfully")

        candidate_name = resume_data.get('candidate_name', 'Resume')
        job_title = _load_job_title(base_dir / JOB_ANALYSIS_FILE)

        first_name, last_name = _extract_candidate_names(candidate_name)
        filename_base = _generate_pdf_filename(first_name, last_name, job_title)

        logger.info(f"Generating PDF: {filename_base}.pdf")

        latex_content = generate_complete_latex(resume_data)
        pdf_path = compile_latex_to_pdf(latex_content, output_full_dir, filename_base)

        return pdf_path

    except FileNotFoundError as e:
        logger.error(str(e))
        return None
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # Allow running directly for testing
    result = generate_resume_pdf_from_json()
    if result:
        print(f"Success! PDF generated at: {result}")
    else:
        print("Failed to generate PDF")
