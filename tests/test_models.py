"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError
from src.models import (
    CandidateInfo, JobRequirements, ScreeningScore,
    AgentState, InterviewSlot
)


def test_candidate_info():
    """Test CandidateInfo model."""
    info = CandidateInfo(
        name="John Doe",
        email="john@email.com",
        phone="+1-555-1234"
    )
    
    assert info.name == "John Doe"
    assert info.email == "john@email.com"


def test_job_requirements():
    """Test JobRequirements model."""
    job = JobRequirements(
        title="AI Engineer",
        required_skills=["Python", "LangGraph"],
        min_years_experience=3
    )
    
    assert job.title == "AI Engineer"
    assert len(job.required_skills) == 2


def test_screening_score_valid():
    """Test valid ScreeningScore."""
    score = ScreeningScore(
        score=85,
        classification="Strong Fit",
        reasoning="Excellent candidate",
        strengths=["Great skills"],
        gaps=[],
        skill_match_percentage=90.0
    )
    
    assert score.score == 85
    assert score.classification == "Strong Fit"


def test_screening_score_invalid():
    """Test invalid ScreeningScore (score out of range)."""
    with pytest.raises(ValidationError):
        ScreeningScore(
            score=150,  # Invalid: > 100
            classification="Strong Fit",
            reasoning="Test",
            skill_match_percentage=90.0
        )


def test_interview_slot():
    """Test InterviewSlot model."""
    slot = InterviewSlot(
        date="Monday, Feb 3, 2026",
        time="10:00 AM",
        duration_minutes=60,
        timezone="EST"
    )
    
    assert slot.duration_minutes == 60
    assert slot.timezone == "EST"


def test_agent_state():
    """Test AgentState model."""
    job = JobRequirements(
        title="Test Job",
        required_skills=["Python"]
    )
    
    state = AgentState(
        resume_text="Sample resume",
        job_requirements=job
    )
    
    assert state.resume_text == "Sample resume"
    assert state.current_step == "start"
    assert state.decision is None
