from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field

# Type alias for sections that can contain mixed content (paragraphs and lists)
# Each section is a list of "content blocks" where each block is either:
#   - str: A paragraph of text
#   - List[str]: A bullet list
MixedContent = List[Union[str, List[str]]]

class SkillScore(BaseModel):
    skill_name: str = Field(description="Name of the skill being scored")
    required: bool = Field(description="Whether this skill is required or nice-to-have")
    match_level: float = Field(ge=0, le=1, description="How well the candidate's experience matches (0-1)")
    years_experience: Optional[float] = Field(description="Years of experience with this skill", default=None)
    context_score: float = Field(
        ge=0, le=1,
        description="How relevant the skill usage context is to the job requirements",
        default=0.5
    )

class JobMatchScore(BaseModel):
    overall_match: float = Field(
        ge=0, le=100,
        description="Overall match percentage (0-100)"
    )
    technical_skills_match: float = Field(
        ge=0, le=100,
        description="Technical skills match percentage"
    )
    soft_skills_match: float = Field(
        ge=0, le=100,
        description="Soft skills match percentage"
    )
    experience_match: float = Field(
        ge=0, le=100,
        description="Experience level match percentage"
    )
    education_match: float = Field(
        ge=0, le=100,
        description="Education requirements match percentage"
    )
    industry_match: float = Field(
        ge=0, le=100,
        description="Industry experience match percentage"
    )
    skill_details: List[SkillScore] = Field(
        description="Detailed scoring for each skill",
        default_factory=list
    )
    strengths: List[str] = Field(
        description="List of areas where candidate exceeds requirements",
        default_factory=list
    )
    gaps: List[str] = Field(
        description="List of areas needing improvement",
        default_factory=list
    )
    scoring_factors: Dict[str, float] = Field(
        description="Weights used for different scoring components",
        default_factory=lambda: {
            "technical_skills": 0.35,
            "soft_skills": 0.20,
            "experience": 0.25,
            "education": 0.10,
            "industry": 0.10
        }
    )

class JobRequirements(BaseModel):
    technical_skills: List[str] = Field(
        description="List of required technical skills",
        default_factory=list
    )
    soft_skills: List[str] = Field(
        description="List of required soft skills",
        default_factory=list
    )
    experience_requirements: List[str] = Field(
        description="List of experience requirements",
        default_factory=list
    )
    key_responsibilities: List[str] = Field(
        description="List of key job responsibilities",
        default_factory=list
    )
    education_requirements: List[str] = Field(
        description="List of education requirements",
        default_factory=list
    )
    nice_to_have: List[str] = Field(
        description="List of preferred but not required skills",
        default_factory=list
    )
    job_title: str = Field(
        description="Job title simplified to 2-3 words maximum. Extract ONLY the core role name, excluding qualifiers, specializations, team names, seniority indicators, and locations. Examples: 'Computer Vision Engineer' (not 'Senior Computer Vision Engineer for Manufacturing'), 'Data Scientist' (not 'Data Scientist - NLP Team'), 'Product Manager' (not 'Senior Product Manager - Cloud Platform')",
        default=""
    )
    department: Optional[str] = Field(
        description="Department or team within the company",
        default=None
    )
    reporting_structure: Optional[str] = Field(
        description="Who this role reports to and any direct reports",
        default=None
    )
    job_level: Optional[str] = Field(
        description="Level of the position (e.g., Entry, Senior, Lead)",
        default=None
    )
    location_requirements: Dict[str, Any] = Field(
        description="Location details including remote/hybrid options",
        default_factory=dict
    )
    work_schedule: Optional[str] = Field(
        description="Expected work hours and schedule flexibility",
        default=None
    )
    travel_requirements: Optional[str] = Field(
        description="Expected travel frequency and scope",
        default=None
    )
    compensation: Dict[str, Any] = Field(
        description="Salary range and compensation details if provided",
        default_factory=dict
    )
    benefits: List[str] = Field(
        description="List of benefits and perks",
        default_factory=list
    )
    tools_and_technologies: List[str] = Field(
        description="Specific tools, software, or technologies used",
        default_factory=list
    )
    industry_knowledge: List[str] = Field(
        description="Required industry-specific knowledge",
        default_factory=list
    )
    certifications_required: List[str] = Field(
        description="Required certifications or licenses",
        default_factory=list
    )
    security_clearance: Optional[str] = Field(
        description="Required security clearance level if any",
        default=None
    )
    team_size: Optional[str] = Field(
        description="Size of the immediate team",
        default=None
    )
    key_projects: List[str] = Field(
        description="Major projects or initiatives mentioned",
        default_factory=list
    )
    cross_functional_interactions: List[str] = Field(
        description="Teams or departments this role interacts with",
        default_factory=list
    )
    career_growth: List[str] = Field(
        description="Career development and growth opportunities",
        default_factory=list
    )
    training_provided: List[str] = Field(
        description="Training or development programs offered",
        default_factory=list
    )
    diversity_inclusion: Optional[str] = Field(
        description="D&I statements or requirements",
        default=None
    )
    company_values: List[str] = Field(
        description="Company values mentioned in the job posting",
        default_factory=list
    )
    job_url: str = Field(
        description="URL of the job posting",
        default=""
    )
    posting_date: Optional[str] = Field(
        description="When the job was posted",
        default=None
    )
    application_deadline: Optional[str] = Field(
        description="Application deadline if specified",
        default=None
    )
    special_instructions: List[str] = Field(
        description="Any special application instructions or requirements",
        default_factory=list
    )
    match_score: JobMatchScore = Field(
        description="Detailed scoring of how well the candidate matches the job requirements"
    )
    score_explanation: List[str] = Field(
        description="Detailed explanation of how scores were calculated",
        default_factory=list
    )

class ResumeOptimization(BaseModel):
    content_suggestions: List[Dict[str, Any]] = Field(
        description="List of content optimization suggestions with 'before' and 'after' examples"
    )
    skills_to_highlight: List[Union[str, Dict[str, Any]]] = Field(
        description="List of skills that should be emphasized based on job requirements"
    )
    achievements_to_add: List[Dict[str, Any]] = Field(
        description="List of achievements that should be added or modified with descriptions and metrics"
    )
    keywords_for_ats: List[Union[str, Dict[str, Any]]] = Field(
        description="List of important keywords for ATS optimization"
    )
    formatting_suggestions: List[Dict[str, Any]] = Field(
        description="List of formatting improvements with type and description"
    )

class WorkExperience(BaseModel):
    institution: str = Field(
        description="Company or organization name"
    )
    location: Optional[str] = Field(
        description="City, State/Country or 'Remote'",
        default=None
    )
    roles: List[str] = Field(
        description="Job title(s) held at this institution. Can be multiple if promoted.",
        default_factory=list
    )
    date_start: str = Field(
        description="Start date in format 'Month YYYY' (e.g., 'July 2022')"
    )
    date_end: str = Field(
        description="End date in format 'Month YYYY' or 'Present'"
    )
    achievements: List[str] = Field(
        description="List of accomplishments and responsibilities as bullet points",
        default_factory=list
    )
    keywords_to_bold: List[str] = Field(
        description="Keywords that should be bolded for emphasis in achievements",
        default_factory=list
    )

class Education(BaseModel):
    institution: str = Field(
        description="University, college, or educational institution name"
    )
    location: Optional[str] = Field(
        description="City, State/Country or 'Online' for remote programs",
        default=None
    )
    degree: str = Field(
        description="Degree name, field of study, or diploma title"
    )
    year_start: Optional[str] = Field(
        description="Start year (e.g., '2013')",
        default=None
    )
    year_end: Optional[str] = Field(
        description="End year (e.g., '2022'). Same as start_year if completed in one year.",
        default=None
    )
    additional_info: Optional[str] = Field(
        description="GPA, honors, thesis, or other relevant details",
        default=None
    )

class Certification(BaseModel):
    year: str = Field(
        description="Year obtained (e.g., '2025')"
    )
    name: str = Field(
        description="Certification or course name"
    )
    provider: str = Field(
        description="Issuing organization or institution"
    )
    grade: Optional[str] = Field(
        description="Grade, level, or score achieved (e.g., 'C2 Proficient', 'Grade A')",
        default=None
    )

class HarvardFormattedResume(BaseModel):
    # Metadata for PDF generation
    candidate_name: str = Field(
        description="Full name of the candidate (e.g., 'Marco Mongi')"
    )
    contact_info: str = Field(
        description="Full contact line with email, LinkedIn, location, etc. separated by bullets"
    )
    summary: Optional[str] = Field(
        description="Professional summary or objective statement (optional)",
        default=None
    )

    # Main sections
    work_experience: List[WorkExperience] = Field(
        description="List of work experiences in reverse chronological order",
        default_factory=list
    )
    education: List[Education] = Field(
        description="List of educational qualifications in reverse chronological order",
        default_factory=list
    )
    certifications: List[Certification] = Field(
        description="List of certifications and courses",
        default_factory=list
    )

    # Flexible additional sections
    skills: Optional[Dict[str, List[str]]] = Field(
        description="Skills organized by category (e.g., {'Technical Skills': [...], 'Soft Skills': [...]})",
        default=None
    )
    languages: Optional[MixedContent] = Field(
        description="Languages and proficiency levels. Can contain paragraphs (str) and/or bullet lists (List[str]).",
        default=None
    )
    projects: Optional[MixedContent] = Field(
        description="Notable projects or portfolio items. Can contain paragraphs (str) and/or bullet lists (List[str]).",
        default=None
    )
    additional_sections: Optional[Dict[str, MixedContent]] = Field(
        description="Any other sections not covered above with section name as key. Each section can contain paragraphs (str) and/or bullet lists (List[str]).",
        default=None
    )
