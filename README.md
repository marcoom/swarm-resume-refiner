# Resume Refiner Crew

**AI-Powered Resume Optimization with Multi-Agent Intelligence**

An intelligent system that transforms your resume into a job-specific, ATS-optimized document using collaborative AI agents powered by CrewAI.

---

## Overview

Finding the right job is challenging, and getting past the initial screening is often the hardest part. **Applicant Tracking Systems (ATS)** are software tools used by over 75% of employers to automatically filter and rank resumes before a human ever sees them. If your resume isn't optimized for both ATS algorithms and the specific job description, it might never reach a hiring manager—even if you're qualified.

**Resume Refiner Crew** solves this problem by analyzing your resume against a specific job posting and automatically generating a tailored, ATS-friendly version. The system rewrites your resume in a way that emphasizes the most relevant skills for the role (using words from the job description), removes irrelevant content to reach a target number of pages, and uses clear and professional writing, in standarized sections, all without hallucinating or exaggerating the facts from your original resume.

This project leverages **Multi-Agent Systems (MAS)**, a branch of artificial intelligence where multiple specialized AI agents work cooperatively toward a shared goal. Instead of a single AI trying to handle everything, seven specialized agents collaborate—each with unique expertise—to transform your resume. This cooperative approach mirrors how expert teams work together: one agent parses documents, another analyzes job requirements, another optimizes content, and so on. The result is a professionally formatted resume that maximizes your chances of getting noticed.

Whether you're applying for your dream job or conducting a job search campaign, Resume Refiner Crew helps you put your best foot forward with minimal effort.

---

## Key Features

- **Intelligent Resume Parsing** - Automatically extracts content from PDF resumes into structured format
- **Job Fit Scoring** - Analyzes how well your background matches job requirements with weighted scoring (technical skills 35%, experience 25%, soft skills 20%, education 10%, industry 10%)
- **ATS Optimization** - Ensures your resume passes Applicant Tracking Systems with proper keywords and formatting
- **Fact-Checking** - Verifies all claims against your original resume to prevent AI hallucinations
- **Word Count Control** - Automatically adjusts resume length to fit single-page (400-600 words) or two-page (600-800 words) formats
- **Harvard Formatting** - Generates professional, clean resumes following Harvard Business School standards
- **PDF Output** - Produces publication-ready PDF resumes with LaTeX typesetting
- **Comprehensive Reports** - Creates detailed analysis reports with strengths, gaps, and improvement suggestions

---

## How It Works

Resume Refiner Crew uses a **sequential pipeline** of seven specialized AI agents that work together to transform your resume:

### 1. Resume Parser Agent
**Role:** PDF Parsing Specialist
**Task:** Converts your PDF resume into clean markdown format, preserving all structure and content without modifications.

### 2. Job Analyzer Agent
**Role:** Job Requirements Analyst
**Task:** Reads the job description, extracts technical skills, soft skills, experience requirements, and responsibilities. Scores your candidacy across multiple dimensions using the parsed resume as context.

### 3. Resume Analyzer Agent
**Role:** Resume Optimization Expert
**Task:** Compares your resume against job requirements and creates structured optimization suggestions. Identifies missing keywords, recommends content improvements with before/after examples, and flags irrelevant sections for removal.

### 4. Resume Writer Agent
**Role:** Resume Markdown Specialist
**Task:** Applies optimization suggestions to create a tailored resume in markdown format. Uses the Word Counter Tool iteratively to ensure the resume meets target length (85-115% of specified word count).

### 5. Fact Checker Agent
**Role:** Resume Verification Specialist
**Task:** Cross-references every claim in the optimized resume against your original resume. Removes any embellishments, hallucinations, or unverifiable content to ensure absolute accuracy.

### 6. Harvard Formatter Agent
**Role:** Harvard Formatting Specialist
**Task:** Structures the verified resume into Harvard-compliant format with proper sections (work experience, education, certifications, skills). Identifies 3-5 keywords per experience to emphasize with bold formatting.

### 7. Report Generator Agent
**Role:** Career Report Generator
**Task:** Creates a comprehensive markdown report combining job analysis, optimization details, and actionable next steps for your job search.

### Final Step: PDF Generation
After all agents complete their tasks, the system uses LaTeX to compile the structured resume into a professional PDF with proper typesetting, alignment, and Harvard formatting standards.

**Output:** A tailored, fact-checked, ATS-optimized resume in both markdown and PDF formats, plus a detailed analysis report.

---

## Prerequisites

Before installing, ensure you have the following:

- **Python** 3.10 or higher
- **LaTeX Distribution** (for PDF generation)
  - Ubuntu/Debian: `sudo apt-get install texlive-latex-base texlive-latex-extra`
  - macOS: `brew install --cask mactex`
  - Windows: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)
- **OpenAI API Key** (required - see Configuration section)

---

## Installation

This project uses [UV](https://docs.astral.sh/uv/) for fast, reliable dependency management.

### 1. Install UV Package Manager

```bash
pip install uv
```

### 2. Clone the Repository

```bash
git clone https://github.com/marcoom/resume-refiner-crew.git
cd resume-refiner-crew
```

### 3. Install Dependencies

```bash
crewai install
```

This command uses UV to lock and install all dependencies defined in `pyproject.toml`.

---

## Configuration

### 1. Create OpenAI API Key

This project requires an OpenAI API key to function. **Note: OpenAI API usage is a paid service** and you will be charged based on token consumption.

**Steps to create your API key:**

1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account (or create one if needed)
3. Click "Create new secret key"
4. Copy the generated API key (you won't be able to see it again)
5. Store it securely

**Important Notes:**
- You must have a paid OpenAI account with credits to use the API
- Monitor your usage at [https://platform.openai.com/usage](https://platform.openai.com/usage)
- **Disclaimer:** The author of this project takes no responsibility for any charges incurred through OpenAI API usage or any misuse of API keys. Users are solely responsible for managing their API keys securely and monitoring their usage costs.

### 2. Set Up Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize these settings
OPENAI_MODEL=gpt-5-mini                    # Default: gpt-5-mini
TARGET_RESUME_WORDS=500                     # Default: 500 (400-600 for 1 page, 600-800 for 2 pages)
```

### 3. Prepare Input Files

Place your files in the appropriate locations:

- **Your Resume PDF:** Save as `knowledge/CV.pdf` (or set custom path in `RESUME_PDF_PATH`)
- **Job Description:** Create `knowledge/job_description.txt` with the complete job posting text

---

## Usage

### Basic Usage

Run the complete pipeline:

```bash
crewai run
```

This command will:
1. Parse your resume PDF
2. Analyze the job description
3. Generate optimization suggestions
4. Create a tailored resume
5. Verify all facts
6. Format in Harvard style
7. Generate a PDF resume
8. Create a comprehensive report

### Alternative Commands

```bash
resume_refiner_crew    # Same as crewai run
run_crew               # Another alias
```

### Expected Runtime

The complete pipeline typically takes 3-5 minutes depending on resume complexity and API response times.

### Monitoring Progress

The system runs in verbose mode, so you'll see each agent's progress, reasoning, and actions in the terminal output.

---

## Project Structure

```
resume-refiner-crew/
│
├── src/resume_refiner_crew/
│   ├── config/
│   │   ├── agents.yaml              # Agent definitions (roles, goals, backstories)
│   │   └── tasks.yaml               # Task definitions with descriptions and expected outputs
│   │
│   ├── tools/
│   │   ├── word_counter_tool.py     # Tool for iterative word count validation
│   │   └── latex_generator.py       # LaTeX generation and PDF compilation
│   │
│   ├── crew.py                      # Crew orchestration, agent/task initialization
│   ├── main.py                      # Entry point, pipeline execution
│   ├── models.py                    # Pydantic models (JobRequirements, ResumeOptimization, etc.)
│   └── utils.py                     # Utility functions (storage cleanup)
│
├── knowledge/
│   ├── CV.pdf                       # Your input resume (place your PDF here)
│   └── job_description.txt          # Target job posting (plain text)
│
├── output/                          # All generated files go here
│   ├── parsed_resume.md             # Original resume in markdown
│   ├── job_analysis.json            # Job requirements and scoring
│   ├── resume_optimization.json     # Optimization suggestions
│   ├── optimized_resume.md          # Tailored resume (markdown)
│   ├── verified_resume.md           # Fact-checked resume
│   ├── structured_resume.json       # Harvard-formatted data
│   ├── final_report.md              # Comprehensive analysis report
│   └── CV_[LastName]_[FirstName]_[JobTitle].pdf  # Final PDF resume
│
├── templates/                       # LaTeX templates for reference
│
├── .env                             # Environment configuration (not in git)
├── .env.example                     # Example environment configuration
├── pyproject.toml                   # Project dependencies and metadata
├── CLAUDE.md                        # Technical documentation for Claude Code
├── LICENSE                          # MIT License
└── README.md                        # This file
```

---

## Output Files

After running the pipeline, you'll find these files in the `output/` directory:

| File | Description |
|------|-------------|
| `parsed_resume.md` | Your original resume converted from PDF to markdown format |
| `job_analysis.json` | Structured analysis of job requirements with candidate scoring |
| `resume_optimization.json` | Detailed optimization suggestions with before/after examples |
| `optimized_resume.md` | Your resume with optimizations applied (markdown) |
| `verified_resume.md` | Fact-checked version with hallucinations removed |
| `structured_resume.json` | Harvard-formatted structured data ready for PDF generation |
| `final_report.md` | Comprehensive report with job fit analysis and recommendations |
| `CV_[LastName]_[FirstName]_[JobTitle].pdf` | **Final PDF resume** ready to submit |

The PDF filename is automatically constructed from your name (extracted from the resume) and the job title (from the job posting).

---

## Technical Notes

### Why Not Use Local Open-Source LLMs?

During development, I attempted to run this system using local open-source language models on consumer-grade GPU hardware. Unfortunately, the results were unsatisfactory for several reasons:

- **Model Size Constraints:** To fit within consumer GPU memory (typically 8-12GB VRAM), only smaller models could be used. These models lack the sophisticated reasoning capabilities needed for complex tasks like resume optimization.
- **Poor Prompt Following:** Smaller models struggled to follow detailed instructions, often deviating from the structured output format required by the pipeline.
- **Inconsistent Quality:** The agents would frequently miss important details, hallucinate information, or produce inconsistently formatted outputs.

For these reasons, **an OpenAI API key is required** to use this system. OpenAI's models (like GPT-4 and GPT-5) provide the reliability, instruction-following capability, and reasoning power necessary for high-quality resume optimization.

### Future Considerations

As open-source models continue to improve, particularly larger models that can run on more powerful hardware or cloud infrastructure, local LLM support may become viable in future versions.

---

## Acknowledgments

This project was inspired by and built upon excellent resources from the CrewAI community:

- **CrewAI YouTube Tutorial** by Tony Kipkemboi: [Resume Optimization with CrewAI](https://www.youtube.com/watch?v=ppE1CXhRNF8)
  Original repository: [https://github.com/tonykipkemboi/resume-optimization-crew](https://github.com/tonykipkemboi/resume-optimization-crew)

- **Multi AI Agent Systems with CrewAI** - Free course by CrewAI and DeepLearning.AI:
  [https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/)

Special thanks to the CrewAI team for creating an excellent framework for building multi-agent AI systems.

---

## License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for full license text.
