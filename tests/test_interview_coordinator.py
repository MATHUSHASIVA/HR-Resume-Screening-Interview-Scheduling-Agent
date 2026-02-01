"""
Unit tests for Interview Coordinator Agent.
"""

import pytest
from src.agents.interview_coordinator import InterviewCoordinatorAgent
from src.models import (
    JobRequirements, ResumeAnalysis, ScreeningScore, 
    CandidateInfo, InterviewCoordination
)


@pytest.fixture
def coordinator():
    """Create Interview Coordinator instance."""
    return InterviewCoordinatorAgent()


@pytest.fixture
def sample_resume_analysis():
    """Sample resume analysis."""
    return ResumeAnalysis(
        candidate_info=CandidateInfo(
            name="John Doe",
            email="john@email.com"
        ),
        skills=["Python", "LangGraph", "LangChain"],
        experience=[],
        education=[],
        summary="Experienced AI engineer with LangGraph expertise"
    )


@pytest.fixture
def sample_screening_score():
    """Sample screening score."""
    return ScreeningScore(
        score=85,
        classification="Strong Fit",
        reasoning="Excellent match",
        strengths=["LangGraph expert", "Strong RAG background"],
        gaps=[],
        skill_match_percentage=90.0
    )


@pytest.fixture
def sample_job():
    """Sample job requirements."""
    return JobRequirements(
        title="AI Engineer",
        required_skills=["Python", "LangGraph"],
        responsibilities=["Build AI systems"],
        department="Engineering"
    )


def test_generate_interview_slots(coordinator):
    """Test interview slot generation."""
    slots = coordinator.generate_interview_slots()
    
    assert len(slots) == 3
    assert all(slot.duration_minutes == 60 for slot in slots)


def test_suggest_interviewers(coordinator, sample_job, sample_resume_analysis):
    """Test interviewer suggestions."""
    interviewers = coordinator.suggest_interviewers(sample_job, sample_resume_analysis)
    
    assert len(interviewers) > 0
    assert "HR Manager" in interviewers


def test_process_qualified(coordinator, sample_resume_analysis, sample_job, sample_screening_score):
    """Test processing qualified candidates."""
    state = {
        "resume_analysis": sample_resume_analysis,
        "job_requirements": sample_job,
        "screening_score": sample_screening_score
    }
    
    result = coordinator.process_qualified(state)
    
    assert "interview_coordination" in result
    assert result["decision"] == "accept"
    assert "current_step" in result


def test_process_rejected(coordinator, sample_resume_analysis, sample_job, sample_screening_score):
    """Test processing rejected candidates."""
    state = {
        "resume_analysis": sample_resume_analysis,
        "job_requirements": sample_job,
        "screening_score": sample_screening_score
    }
    
    result = coordinator.process_rejected(state)
    
    assert "interview_coordination" in result
    assert result["decision"] == "reject"
