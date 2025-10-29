"""Resume Refiner Crew configuration and orchestration."""

import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai_tools import PDFSearchTool

from .constants import (
    AGENTS_CONFIG,
    TASKS_CONFIG,
    DEFAULT_RESUME_PATH,
    DEFAULT_JOB_DESC_PATH,
    DEFAULT_OPENAI_MODEL,
)
from .models import (
    JobRequirements,
    ResumeOptimization,
    HarvardFormattedResume,
)
from .tools.word_counter_tool import WordCounterTool
from .utils import validate_path_exists


@CrewBase
class ResumeRefinerCrew():
    """Resume optimization crew with multi-agent AI pipeline."""

    agents_config = str(AGENTS_CONFIG)
    tasks_config = str(TASKS_CONFIG)

    def __init__(
        self,
        job_description_path: str = str(DEFAULT_JOB_DESC_PATH),
        resume_pdf_path: str = str(DEFAULT_RESUME_PATH)
    ) -> None:
        """Initialize crew with job description and resume.

        Args:
            job_description_path: Path to job description text file.
                Note: TextFileKnowledgeSource will prepend "knowledge/" to relative paths.
            resume_pdf_path: Path to resume PDF file (used as-is by PDFSearchTool).

        Raises:
            FileNotFoundError: If resume PDF doesn't exist.
        """
        resume_path_obj = Path(resume_pdf_path)
        validate_path_exists(resume_path_obj, "resume PDF")

        self.job_description_path = job_description_path
        self.resume_pdf_path = resume_pdf_path
        self.job_description = TextFileKnowledgeSource(file_paths=[job_description_path])
        self.pdf_search_tool = PDFSearchTool(pdf=resume_pdf_path)

        model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.llm = LLM(model=model)

    # PARSE RESUME
    # Parse PDF resume to markdown format
    @agent
    def resume_parser(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_parser'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_search_tool]
        )

    @task
    def parse_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['parse_resume_task'],
            output_file='output/parsed_resume.md',
            agent=self.resume_parser()
        )

    # ANALYZE JOB
    # Analyze job descriptions and score candidate fit
    @agent
    def job_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyzer'],
            verbose=True,
            llm=self.llm,
            knowledge_sources=[self.job_description]
        )

    @task
    def analyze_job_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_job_task'],
            output_file='output/job_analysis.json',
            output_pydantic=JobRequirements,
            agent=self.job_analyzer(),
            context=[self.parse_resume_task()]
        )

    # OPTIMIZE RESUME
    # Analyze resumes and provide structured optimization suggestions
    @agent
    def resume_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyzer'],
            verbose=True,
            llm=self.llm
        )

    @task
    def optimize_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resume_task'],
            output_file='output/resume_optimization.json',
            output_pydantic=ResumeOptimization,
            agent=self.resume_analyzer(),
            context=[self.parse_resume_task(), self.analyze_job_task()]
        )

    # GENERATE RESUME
    # Create beautifully formatted, ATS-optimized resumes in markdown
    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_writer'],
            verbose=True,
            llm=self.llm,
            tools=[WordCounterTool()]
        )

    @task
    def generate_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_resume_task'],
            output_file='output/optimized_resume.md',
            agent=self.resume_writer(),
            context=[self.parse_resume_task(), self.optimize_resume_task()]
        )

    # VERIFY RESUME
    # Verify all claims in the optimized resume against the original CV
    # and remove any hallucinated content
    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            verbose=True,
            llm=self.llm
        )

    @task
    def verify_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['verify_resume_task'],
            output_file='output/verified_resume.md',
            agent=self.fact_checker(),
            context=[self.parse_resume_task(), self.generate_resume_task()]
        )

    # FORMAT TO HARVARD
    # Parse and structure resume content into Harvard-compliant format 
    # with precise data extraction
    @agent
    def harvard_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['harvard_formatter'],
            verbose=True,
            llm=self.llm
        )

    @task
    def harvard_format_task(self) -> Task:
        return Task(
            config=self.tasks_config['harvard_format_task'],
            output_file='output/structured_resume.json',
            output_pydantic=HarvardFormattedResume,
            agent=self.harvard_formatter(),
            context=[self.verify_resume_task()]
        )

    # GENERATE REPORT
    # Create comprehensive, visually appealing, and actionable reports 
    # from job application analysis
    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            llm=self.llm
        )
    
    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='output/final_report.md',
            agent=self.report_generator(),
            context=[self.analyze_job_task(), self.optimize_resume_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            memory=False,
            output_log_file=".crewai_temp/crew_logs.txt"
        )
