"""
Utility functions for logging, PDF parsing, and error handling.
"""

import logging
import colorlog
from typing import Optional
import PyPDF2
from functools import wraps
import time
from src.config import LOG_LEVEL, LOG_FORMAT, MAX_RETRIES, RETRY_DELAY


def setup_logger(name: str) -> logging.Logger:
    """Set up colored logger with consistent formatting."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        LOG_FORMAT,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    return logger


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF parsing fails
    """
    logger = setup_logger(__name__)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text += page.extract_text() + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
                
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text.strip()
            
    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """
    Decorator for retrying functions on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logger(func.__name__)
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
                        raise
            
        return wrapper
    return decorator


def validate_resume_text(text: str) -> bool:
    """
    Validate that resume text contains minimum required content.
    
    Args:
        text: Resume text to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not text or len(text.strip()) < 50:
        return False
    
    # Check for common resume indicators
    indicators = ['experience', 'education', 'skills', 'work', 'university', 'degree']
    text_lower = text.lower()
    
    matches = sum(1 for indicator in indicators if indicator in text_lower)
    
    return matches >= 2


def sanitize_text(text: str) -> str:
    """
    Clean and sanitize text content.
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)


def calculate_skill_match(candidate_skills: list[str], required_skills: list[str]) -> float:
    """
    Calculate percentage of required skills matched by candidate.
    
    Args:
        candidate_skills: List of candidate's skills
        required_skills: List of required skills
        
    Returns:
        Match percentage (0-100)
    """
    if not required_skills:
        return 100.0
    
    # Normalize to lowercase for comparison
    candidate_skills_lower = {skill.lower().strip() for skill in candidate_skills}
    required_skills_lower = {skill.lower().strip() for skill in required_skills}
    
    matched = len(candidate_skills_lower & required_skills_lower)
    total = len(required_skills_lower)
    
    return (matched / total) * 100


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes} minutes"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    
    return f"{hours} hour{'s' if hours > 1 else ''} {mins} minutes"


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class AgentExecutionError(Exception):
    """Custom exception for agent execution errors."""
    pass
