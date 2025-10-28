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

### 1. Clone the Repository

```bash
git clone https://github.com/marcoom/resume-refiner-crew.git
cd resume-refiner-crew
```

### 2. Create Virtual Environment

It is recommended to create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows
```

### 3. Install UV Package Manager

```bash
pip install uv
```

### 4. Install Dependencies

```bash
uv pip install -e .
```

This command installs the project and all dependencies defined in `pyproject.toml` using UV's fast resolver.

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
DEVELOPER_MODE=false                        # Default: false (see Developer Mode section for details)
```

### 3. Prepare Input Files

Place your files in the appropriate locations:

- **Your Resume PDF:** Save as `knowledge/CV.pdf` (or set custom path in `RESUME_PDF_PATH`)
- **Job Description:** Create `knowledge/job_description.txt` with the complete job posting text

---

## Usage

Resume Refiner Crew can be used in two ways: **Web UI** (recommended for most users) or **Command Line**.

### Web Interface (Recommended)

The easiest way to use Resume Refiner Crew is through the Streamlit web interface:

```bash
./start.sh
```

Or directly:

```bash
streamlit run streamlit_app.py
```

The web interface will open in your browser at `http://localhost:8501` and provides:

- **Visual file upload** - Drag and drop your resume PDF
- **Guided inputs** - Clear form fields for all settings
- **Real-time progress** - Watch the agents work with live logs
- **Interactive results** - View reports and download files with one click
- **Optional JSON editing** - Fine-tune the structured resume before PDF generation
- **No file management** - Upload files directly, no need to place them in folders

This is the recommended method for users who prefer a graphical interface and want to process multiple resumes without managing configuration files.

### Command Line Interface

For automation or integration into workflows, use the CLI:

```bash
crewai run
```

**Before running**, ensure your input files are in place:
- Resume PDF: `knowledge/CV.pdf`
- Job Description: `knowledge/job_description.txt`

This command will:
1. Parse your resume PDF
2. Analyze the job description
3. Generate optimization suggestions
4. Create a tailored resume
5. Verify all facts
6. Format in Harvard style
7. Generate a PDF resume
8. Create a comprehensive report

### Alternative CLI Commands

```bash
resume_refiner_crew    # Same as crewai run
run_crew               # Another alias
```

### Expected Runtime

The complete pipeline typically takes 3-5 minutes depending on resume complexity and API response times.

### Monitoring Progress

- **Web UI**: Real-time progress indicators and live log streaming
- **CLI**: Verbose terminal output showing each agent's reasoning and actions

---

## Docker Usage

Resume Refiner Crew is available as a Docker container, providing an isolated environment with all dependencies pre-installed. This is the easiest way to run the application without manually installing Python, LaTeX, or other dependencies.

### Prerequisites

- **Docker** or **Docker Desktop** installed on your system
  - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
  - macOS: [Install Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
  - Windows: [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

### Using Pre-built Image from Docker Hub

The easiest way to get started is to pull the pre-built image from Docker Hub:

```bash
docker pull marcoom/swarm-resume-refiner:1.0.0
```

Run the container with environment variables:

```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e OPENAI_MODEL=gpt-5-mini \
  -e TARGET_RESUME_WORDS=500 \
  -e DEVELOPER_MODE=false \
  marcoom/swarm-resume-refiner:1.0.0
```

**Environment Variables Explained:**
- `OPENAI_API_KEY` - **(Required)** Your OpenAI API key
- `OPENAI_MODEL` - *(Optional)* Model to use (default: `gpt-5-mini`)
- `TARGET_RESUME_WORDS` - *(Optional)* Target word count (default: `500`; single page: 400-600, two pages: 600-800)
- `DEVELOPER_MODE` - *(Optional)* Set to `true` to simulate execution without API calls (default: `false`)

**On Windows (PowerShell)**, use `${PWD}` instead of `$(pwd)`:

```powershell
docker run -p 8501:8501 `
  -e OPENAI_API_KEY=your_openai_api_key_here `
  -e OPENAI_MODEL=gpt-5-mini `
  -e TARGET_RESUME_WORDS=500 `
  -e DEVELOPER_MODE=false `
  marcoom/swarm-resume-refiner:1.0.0
```

**Using an environment file** (recommended for managing multiple variables):

```bash
# Create .env file with your configuration
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
TARGET_RESUME_WORDS=500
DEVELOPER_MODE=false
EOF

# Run with --env-file
docker run -p 8501:8501 \
  --env-file .env \
  marcoom/swarm-resume-refiner:1.0.0
```

The Streamlit web interface will be available at `http://localhost:8501`.

### Building and Running Locally

If you prefer to build the Docker image from source:

#### 1. Build the Image

```bash
docker build -t swarm-resume-refiner .
```

#### 2. Run the Container

```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e OPENAI_MODEL=gpt-5-mini \
  -e TARGET_RESUME_WORDS=500 \
  -e DEVELOPER_MODE=false \
  swarm-resume-refiner
```

Or use an environment file:

```bash
docker run -p 8501:8501 \
  --env-file .env \
  swarm-resume-refiner
```

---

## Developer Mode

**Developer Mode** allows you to test the application's UI and workflows without running the actual multi-agent system. This is particularly useful during development when you want to:

- Test changes to the Streamlit interface without waiting for agents to complete
- Iterate quickly on UI improvements without incurring API costs
- Validate the flow from processing to results display
- Test with consistent, known output data

### How It Works

When `DEVELOPER_MODE=true`, the system:

1. **Skips crew execution** - No agents are run, no API calls are made
2. **Simulates logs** - Writes realistic log messages to `.crewai_temp/crew_logs.txt` with 1-second delays between entries
3. **Uses fixture files** - Copies pre-generated output files from `tests/fixtures/output/` to `output/`
4. **Maintains normal flow** - All other parts of the system (PDF generation, file downloads, UI components) work exactly as they would with real execution

### Using Developer Mode

Edit your `.env` file:

```bash
DEVELOPER_MODE=true
```

Once enabled, use the application normally.

The execution will complete in approximately 13 seconds (one second per log message) instead of 3-5 minutes.

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
│   ├── main.py                      # Entry point, pipeline execution (CLI)
│   ├── models.py                    # Pydantic models (JobRequirements, ResumeOptimization, etc.)
│   ├── streamlit_runner.py          # Wrapper for running crew with custom parameters (Web UI)
│   └── utils.py                     # Utility functions (storage cleanup)
│
├── knowledge/
│   ├── CV.pdf                       # Your input resume (place your PDF here for CLI)
│   └── job_description.txt          # Target job posting (plain text, for CLI)
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
├── streamlit_app.py                 # Streamlit web interface
├── start.sh                         # Launch script for web UI
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
