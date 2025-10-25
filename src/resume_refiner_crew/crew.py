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

    # ANALYZE JOB
    # Analyze job descriptions and score candidate fit
    @agent
    def job_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyzer'],
            verbose=True,
            llm=self.llm,
            knowledge_sources=[self.job_description],
            tools=[self.pdf_tool]
        )
    
    @task
    def analyze_job_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_job_task'],
            output_file='output/job_analysis.json',
            output_pydantic=JobRequirements,
            agent=self.job_analyzer()
        )
    
    # OPTIMIZE RESUME
    # Analyze resumes and provide structured optimization suggestions
    @agent
    def resume_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_analyzer'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )
    
    @task
    def optimize_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['optimize_resume_task'],
            output_file='output/resume_optimization.json',
            output_pydantic=ResumeOptimization,
            agent=self.resume_analyzer(),
            context=[self.analyze_job_task()]
        )
    
    # GENERATE RESUME
    # Create beautifully formatted, ATS-optimized resumes in markdown
    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_writer'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )
    
    @task
    def generate_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_resume_task'],
            output_file='output/optimized_resume.md',
            agent=self.resume_writer(),
            context=[self.optimize_resume_task()]
        )

    # VERIFY RESUME
    # Verify all claims in the optimized resume against the original CV 
    # and remove any hallucinated content
    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            verbose=True,
            llm=self.llm,
            tools=[self.pdf_tool]
        )
    
    @task
    def verify_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config['verify_resume_task'],
            output_file='output/verified_resume.md',
            agent=self.fact_checker(),
            context=[self.generate_resume_task()]
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
            memory=False
        )
