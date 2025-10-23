import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from .models import (
    JobRequirements,
    ResumeOptimization
)


@CrewBase
class ResumeRefinerCrew():
    """ResumeCrew for resume optimization and interview preparation"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        """Sample resume PDF for testing from https://www.hbs.edu/doctoral/Documents/job-market/CV_Mohan.pdf"""
        self.resume_pdf = PDFKnowledgeSource(file_paths="CV.pdf") # TODO get from input
        self.job_description_txt = TextFileKnowledgeSource(file_paths=["job_description.txt"])

        # Configure LLM from environment variables for Ollama
        model = os.getenv("MODEL", "llama3.1:latest")
        api_base = os.getenv("API_BASE", "http://localhost:11434")
        self.llm = LLM(
            model=f"ollama/{model}",
            base_url=api_base
        )

        # Configure embedder to use Ollama
        self.embedder = {
            "provider": "ollama",
            "config": {
                "model_name": "nomic-embed-text:latest",
                "url": f"{api_base}/api/embeddings"
            }
        }

    @agent
    def resume_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyzer'],
            verbose=True,
            llm=self.llm,
            knowledge_sources=[self.resume_pdf]
        )

    @agent
    def job_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyzer'],
            verbose=True,
            llm=self.llm,
            knowledge_sources=[self.job_description_txt]
        )

    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_writer'],
            verbose=True,
            llm=self.llm
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
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
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='output/final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            embedder=self.embedder
        )
