"""
Configuration and constants for the HR screening system.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Scoring Thresholds
STRONG_FIT_THRESHOLD = 75
MODERATE_FIT_THRESHOLD = 50
QUALIFIED_CANDIDATE_THRESHOLD = 70

# Interview Settings
DEFAULT_INTERVIEW_DURATION = 60  # minutes
NUM_INTERVIEW_QUESTIONS = 8
NUM_INTERVIEW_SLOTS = 3

# Email Templates Settings
COMPANY_NAME = "Zelora Tech"
HR_EMAIL = "hr@zeloratech.com"
HR_SIGNATURE = """
Best regards,
The Zelora Tech Talent Team
hr@zeloratech.com
"""

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Configurable Scoring Weights
SCORING_WEIGHTS = {
    "skills_match": 0.40,
    "experience_years": 0.25,
    "education": 0.15,
    "relevance": 0.20,
}

# Interview Time Slots (configurable)
INTERVIEW_AVAILABILITY = {
    "days_ahead": 7,  # Propose slots within next 7 days
    "preferred_times": [
        "10:00 AM",
        "2:00 PM",
        "4:00 PM"
    ],
    "timezone": "IST"  # India Standard Time (UTC+5:30) - Sri Lanka Time
}
