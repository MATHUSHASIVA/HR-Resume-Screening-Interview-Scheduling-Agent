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


def load_booked_slots() -> list:
    """
    Load all booked interview slots from storage.
    
    Returns:
        List of booked interview slots
    """
    import json
    from pathlib import Path
    
    booking_file = Path("data/booked_slots.json")
    
    if not booking_file.exists():
        return []
    
    try:
        with open(booking_file, 'r') as f:
            bookings = json.load(f)
            return bookings if isinstance(bookings, list) else []
    except (json.JSONDecodeError, Exception) as e:
        logger = setup_logger(__name__)
        logger.warning(f"Failed to load booked slots: {e}")
        return []


def save_booking(candidate_name: str, date: str, time: str, timezone: str) -> bool:
    """
    Save a booked interview slot to storage.
    
    Args:
        candidate_name: Name of the candidate
        date: Interview date
        time: Interview time
        timezone: Timezone
        
    Returns:
        True if successful, False otherwise
    """
    import json
    from pathlib import Path
    from datetime import datetime
    
    logger = setup_logger(__name__)
    
    try:
        booking_file = Path("data/booked_slots.json")
        booking_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing bookings
        bookings = load_booked_slots()
        
        # Create new booking entry
        new_booking = {
            "candidate_name": candidate_name,
            "date": date,
            "time": time,
            "timezone": timezone,
            "booked_at": datetime.now().isoformat()
        }
        
        bookings.append(new_booking)
        
        # Save back to file
        with open(booking_file, 'w') as f:
            json.dump(bookings, f, indent=2)
        
        logger.info(f"Booked slot: {date} at {time} for {candidate_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save booking: {e}")
        return False


def is_slot_available(date: str, time: str) -> bool:
    """
    Check if a specific interview slot is available (not already booked).
    
    Args:
        date: Interview date to check
        time: Interview time to check
        
    Returns:
        True if available, False if already booked
    """
    bookings = load_booked_slots()
    
    for booking in bookings:
        if booking.get('date') == date and booking.get('time') == time:
            return False
    
    return True


def is_holiday(date) -> bool:
    """
    Check if a given date is a company holiday.
    
    Args:
        date: datetime object or date string
        
    Returns:
        True if it's a holiday, False otherwise
    """
    from src.config import COMPANY_HOLIDAYS
    from datetime import datetime
    
    # Convert to date string if datetime object
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)
    
    return date_str in COMPANY_HOLIDAYS


def is_within_business_hours(time_str: str) -> bool:
    """
    Check if a time is within business hours (10 AM - 12 PM or 2 PM - 5 PM).
    
    Args:
        time_str: Time string (e.g., "10:00 AM", "3:00 PM")
        
    Returns:
        True if within business hours, False otherwise
    """
    from datetime import datetime
    
    try:
        # Parse time string
        time_obj = datetime.strptime(time_str.strip(), "%I:%M %p")
        hour = time_obj.hour
        minute = time_obj.minute
        
        # Convert to total minutes for easier comparison
        total_minutes = hour * 60 + minute
        
        # Morning hours: 10:00 AM (600 min) to 12:00 PM (720 min)
        morning_start = 10 * 60  # 600
        morning_end = 12 * 60    # 720
        
        # Afternoon hours: 2:00 PM (840 min) to 5:00 PM (1020 min)
        afternoon_start = 14 * 60  # 840
        afternoon_end = 17 * 60    # 1020
        
        # Check if time falls within either range
        in_morning = morning_start <= total_minutes <= morning_end
        in_afternoon = afternoon_start <= total_minutes <= afternoon_end
        
        return in_morning or in_afternoon
        
    except Exception as e:
        logger = setup_logger(__name__)
        logger.warning(f"Failed to parse time '{time_str}': {e}")
        return False


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class AgentExecutionError(Exception):
    """Custom exception for agent execution errors."""
    pass
