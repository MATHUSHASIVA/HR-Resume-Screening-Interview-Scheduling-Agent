"""
Core Pydantic models for state management and structured outputs.
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class CandidateInfo(BaseModel):
    """Extracted candidate information from resume."""
    name: Optional[str] = Field(None, description="Candidate's full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    

class Education(BaseModel):
    """Educational background."""
    degree: str = Field(..., description="Degree or certification name")
    institution: str = Field(..., description="School/University name")
    year: Optional[str] = Field(None, description="Graduation year or period")
    field_of_study: Optional[str] = Field(None, description="Major/Field of study")


class Experience(BaseModel):
    """Work experience entry."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    duration: Optional[str] = Field(None, description="Time period (e.g., '2020-2023')")
    description: Optional[str] = Field(None, description="Job responsibilities and achievements")


class ResumeAnalysis(BaseModel):
    """Complete resume analysis output."""
    candidate_info: CandidateInfo = Field(..., description="Basic candidate information")
    skills: List[str] = Field(default_factory=list, description="Technical and soft skills")
    experience: List[Experience] = Field(default_factory=list, description="Work history")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    years_of_experience: Optional[float] = Field(None, description="Total years of professional experience")
    summary: str = Field(..., description="Brief professional summary")


class ScreeningScore(BaseModel):
    """Candidate screening evaluation."""
    score: int = Field(..., ge=0, le=100, description="Overall fit score (0-100)")
    classification: Literal["Strong Fit", "Moderate Fit", "Not Suitable"] = Field(
        ..., description="Candidate classification"
    )
    reasoning: str = Field(..., description="Detailed explanation of the score")
    strengths: List[str] = Field(default_factory=list, description="Key strengths matching job requirements")
    gaps: List[str] = Field(default_factory=list, description="Missing qualifications or concerns")
    skill_match_percentage: float = Field(..., ge=0, le=100, description="Percentage of required skills matched")


class InterviewQuestion(BaseModel):
    """Interview question with context."""
    question: str = Field(..., description="The interview question")
    category: str = Field(..., description="Question category (e.g., 'Technical', 'Behavioral', 'Experience')")
    reasoning: str = Field(..., description="Why this question is relevant for this candidate")


class EmailTemplate(BaseModel):
    """Email template for candidate communication."""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    tone: str = Field(..., description="Email tone (e.g., 'Professional', 'Friendly')")


class InterviewSlot(BaseModel):
    """Proposed interview time slot."""
    date: str = Field(..., description="Interview date")
    time: str = Field(..., description="Interview time")
    duration_minutes: int = Field(default=60, description="Interview duration in minutes")
    timezone: str = Field(default="UTC", description="Timezone for the interview")


class InterviewCoordination(BaseModel):
    """Interview coordination output."""
    interview_questions: List[InterviewQuestion] = Field(
        default_factory=list, description="Suggested interview questions"
    )
    email_template: EmailTemplate = Field(..., description="Email template for candidate")
    interview_slots: List[InterviewSlot] = Field(
        default_factory=list, description="Proposed interview time slots"
    )
    recommended_interviewers: List[str] = Field(
        default_factory=list, description="Suggested interviewers based on candidate background"
    )


class JobRequirements(BaseModel):
    """Job requirements and description."""
    title: str = Field(..., description="Job title")
    required_skills: List[str] = Field(..., description="Must-have skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    min_years_experience: Optional[float] = Field(None, description="Minimum years of experience required")
    education_requirements: List[str] = Field(default_factory=list, description="Education requirements")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
    department: Optional[str] = Field(None, description="Department or team")


class AgentState(BaseModel):
    """Central state for the LangGraph workflow."""
    # Input
    resume_text: str = Field(..., description="Raw resume text content")
    job_requirements: JobRequirements = Field(..., description="Job requirements to match against")
    
    # Resume Analysis
    resume_analysis: Optional[ResumeAnalysis] = Field(None, description="Parsed resume data")
    screening_score: Optional[ScreeningScore] = Field(None, description="Screening evaluation")
    
    # Interview Coordination
    interview_coordination: Optional[InterviewCoordination] = Field(
        None, description="Interview scheduling and questions"
    )
    
    # Workflow Control
    current_step: str = Field(default="start", description="Current workflow step")
    decision: Optional[Literal["accept", "reject", "review"]] = Field(
        None, description="Final decision on candidate"
    )
    error: Optional[str] = Field(None, description="Error message if any")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")
    candidate_id: Optional[str] = Field(None, description="Unique candidate identifier")
    
    class Config:
        arbitrary_types_allowed = True


class WorkflowDecision(BaseModel):
    """Decision output from supervisor."""
    next_step: Literal["analyze", "screen", "coordinate", "send_invitation", "send_rejection", "end"] = Field(
        ..., description="Next step in workflow"
    )
    reasoning: str = Field(..., description="Explanation for routing decision")
    requires_human_review: bool = Field(default=False, description="Whether human review is needed")
