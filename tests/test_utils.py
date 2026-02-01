"""
Unit tests for utilities.
"""

import pytest
from src.utils import (
    calculate_skill_match,
    validate_resume_text,
    sanitize_text,
    format_duration
)


def test_calculate_skill_match():
    """Test skill match calculation."""
    candidate_skills = ["Python", "LangGraph", "JavaScript"]
    required_skills = ["Python", "LangGraph", "LangChain"]
    
    match = calculate_skill_match(candidate_skills, required_skills)
    
    assert 0 <= match <= 100
    assert match == pytest.approx(66.67, rel=0.01)


def test_calculate_skill_match_perfect():
    """Test perfect skill match."""
    skills = ["Python", "LangGraph"]
    
    match = calculate_skill_match(skills, skills)
    
    assert match == 100.0


def test_calculate_skill_match_no_match():
    """Test no skill match."""
    candidate_skills = ["JavaScript", "React"]
    required_skills = ["Python", "LangGraph"]
    
    match = calculate_skill_match(candidate_skills, required_skills)
    
    assert match == 0.0


def test_validate_resume_text_valid():
    """Test valid resume text."""
    text = """
    John Doe
    Experience: 5 years
    Skills: Python, LangGraph
    Education: BS Computer Science
    """
    
    assert validate_resume_text(text) is True


def test_validate_resume_text_invalid():
    """Test invalid resume text."""
    assert validate_resume_text("") is False
    assert validate_resume_text("Too short") is False


def test_sanitize_text():
    """Test text sanitization."""
    text = """
    Line 1
    
    
    Line 2
    
    Line 3
    """
    
    sanitized = sanitize_text(text)
    
    assert "Line 1\nLine 2\nLine 3" in sanitized
    assert "\n\n\n" not in sanitized


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(30) == "30 minutes"
    assert format_duration(60) == "1 hour"
    assert format_duration(90) == "1 hour 30 minutes"
    assert format_duration(120) == "2 hours"
