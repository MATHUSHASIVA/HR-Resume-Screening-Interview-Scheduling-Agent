"""
Unit tests for Resume Analyzer Agent.
"""

import pytest
from src.agents.resume_analyzer import ResumeAnalyzerAgent
from src.models import JobRequirements, ResumeAnalysis, ScreeningScore


@pytest.fixture
def resume_analyzer():
    """Create Resume Analyzer instance."""
    return ResumeAnalyzerAgent()


@pytest.fixture
def sample_resume_text():
    """Sample resume text."""
    return """
    John Doe
    john.doe@email.com | +1-555-1234
    
    EXPERIENCE
    Senior AI Engineer at TechCorp (2020-2023)
    - Built RAG systems using LangChain and Pinecone
    - Developed multi-agent workflows with LangGraph
    - Optimized LLM performance for production
    
    SKILLS
    Python, LangGraph, LangChain, OpenAI API, RAG Systems, Vector Databases
    
    EDUCATION
    MS in Computer Science, Stanford University, 2020
    """


@pytest.fixture
def sample_job_requirements():
    """Sample job requirements."""
    return JobRequirements(
        title="AI Engineer",
        required_skills=["Python", "LangGraph", "LangChain", "RAG Systems"],
        preferred_skills=["OpenAI API", "Vector Databases"],
        min_years_experience=2,
        education_requirements=["Bachelor's or Master's in CS"],
        responsibilities=["Build AI systems", "Develop RAG pipelines"],
        department="AI Engineering"
    )


def test_extract_resume_data(resume_analyzer, sample_resume_text):
    """Test resume data extraction."""
    result = resume_analyzer.extract_resume_data(sample_resume_text)
    
    assert isinstance(result, ResumeAnalysis)
    assert result.candidate_info is not None
    assert len(result.skills) > 0
    assert len(result.experience) > 0


def test_score_candidate(resume_analyzer, sample_resume_text, sample_job_requirements):
    """Test candidate scoring."""
    # First extract resume
    resume_analysis = resume_analyzer.extract_resume_data(sample_resume_text)
    
    # Then score
    score = resume_analyzer.score_candidate(resume_analysis, sample_job_requirements)
    
    assert isinstance(score, ScreeningScore)
    assert 0 <= score.score <= 100
    assert score.classification in ["Strong Fit", "Moderate Fit", "Not Suitable"]
    assert len(score.reasoning) > 0


def test_process_method(resume_analyzer, sample_resume_text, sample_job_requirements):
    """Test the complete process method."""
    state = {
        "resume_text": sample_resume_text,
        "job_requirements": sample_job_requirements
    }
    
    result = resume_analyzer.process(state)
    
    assert "resume_analysis" in result
    assert "screening_score" in result
    assert "current_step" in result
    assert result["current_step"] == "analyzed"
