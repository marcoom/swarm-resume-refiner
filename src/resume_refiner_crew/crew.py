import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from .models import (
    JobRequirements,
    ResumeOptimization,
    HarvardFormattedResume
)


@CrewBase
class ResumeRefinerCrew():
    """ResumeCrew for resume optimization and interview preparation"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        """Sample resume PDF for testing"""
        self.pdf_tool = PDFSearchTool(pdf="./knowledge/CV.pdf")  # Tool for agents that need CV access
        self.job_description = TextFileKnowledgeSource(file_paths=["job_description.txt"])

        # Configure LLM from environment variables for OpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.llm = LLM(model=model)

    @agent
    def resume_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyzer'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )

    @agent
    def job_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyzer'],
            verbose=True,
            llm=self.llm,
            knowledge_sources=[self.job_description],
            tools=[self.pdf_tool]
        )

    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_writer'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )

    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            llm=self.llm
        )

    @agent
    def harvard_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['harvard_formatter'],
            verbose=True,
            llm=self.llm
        )

    @task
    def analyze_job_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_job_task'],
            output_file='output/job_analysis.json',
            output_pydantic=JobRequirements
        )

    @task
    def optimize_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resume_task'],
            output_file='output/resume_optimization.json',
            output_pydantic=ResumeOptimization
        )

    @task
    def generate_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_resume_task'],
            output_file='output/optimized_resume.md'
        )

    @task
    def verify_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['verify_resume_task'],
            output_file='output/verified_resume.md'
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='output/final_report.md'
        )

    @task
    def harvard_format_task(self) -> Task:
        return Task(
            config=self.tasks_config['harvard_format_task'],
            output_file='output/structured_resume.json',
            output_pydantic=HarvardFormattedResume
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            memory=False
        )
