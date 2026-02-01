"""
Agent 3: Decision Supervisor
Orchestrates workflow and makes routing decisions.
"""

from typing import Dict, Literal
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, QUALIFIED_CANDIDATE_THRESHOLD
from src.utils import setup_logger


logger = setup_logger(__name__)


class DecisionSupervisorAgent:
    """Agent for orchestrating workflow and making routing decisions."""
    
    def __init__(self):
        """Initialize the Decision Supervisor agent."""
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0,  # Deterministic for routing
        )
        logger.info("Decision Supervisor Agent initialized")
    
    def route_after_screening(self, state: Dict) -> Literal["coordinate_accept", "coordinate_reject"]:
        """
        Route candidate based on screening score.
        
        Args:
            state: Current agent state with screening_score
            
        Returns:
            Next step in workflow
        """
        logger.info("=== Decision Supervisor: Routing After Screening ===")
        
        screening_score = state.get("screening_score")
        
        if not screening_score:
            logger.error("No screening score found")
            return "coordinate_reject"
        
        # Handle both dict and Pydantic model
        if isinstance(screening_score, dict):
            score = screening_score.get("score", 0)
            classification = screening_score.get("classification", "Not Suitable")
        else:
            score = screening_score.score
            classification = screening_score.classification
        
        logger.info(f"Candidate Score: {score}/100 - {classification}")
        
        # Routing logic based on threshold
        if score >= QUALIFIED_CANDIDATE_THRESHOLD:
            logger.info(f"✓ Candidate QUALIFIED (score {score} >= {QUALIFIED_CANDIDATE_THRESHOLD})")
            logger.info(f"→ Routing to: Interview Coordination (Accept)")
            return "coordinate_accept"
        else:
            logger.info(f"✗ Candidate NOT QUALIFIED (score {score} < {QUALIFIED_CANDIDATE_THRESHOLD})")
            logger.info(f"→ Routing to: Rejection Email Generation")
            return "coordinate_reject"
    
    def should_require_human_review(self, state: Dict) -> bool:
        """
        Determine if human review is required.
        
        Args:
            state: Current agent state
            
        Returns:
            True if human review needed
        """
        screening_score = state.get("screening_score")
        
        if not screening_score:
            return True
        
        # Handle both dict and Pydantic model
        if isinstance(screening_score, dict):
            score = screening_score.get("score", 0)
            gaps = screening_score.get("gaps", [])
        else:
            score = screening_score.score
            gaps = screening_score.gaps
        
        # Borderline cases (65-75) might need human review
        if 65 <= score <= 75:
            logger.info(f"⚠ Borderline score ({score}): Human review recommended")
            return True
        
        # High-potential candidates with gaps
        if score >= 80 and gaps and len(gaps) > 2:
            logger.info(f"⚠ High score with significant gaps: Human review recommended")
            return True
        
        return False
    
    def log_decision_summary(self, state: Dict) -> None:
        """Log comprehensive decision summary."""
        logger.info("\n" + "="*60)
        logger.info("DECISION SUMMARY")
        logger.info("="*60)
        
        resume_analysis = state.get("resume_analysis")
        screening_score = state.get("screening_score")
        decision = state.get("decision")
        
        if resume_analysis:
            # Handle both dict and Pydantic model
            if isinstance(resume_analysis, dict):
                candidate_info = resume_analysis.get("candidate_info", {})
                if isinstance(candidate_info, dict):
                    name = candidate_info.get("name", "Unknown")
                    email = candidate_info.get("email", "Not provided")
                else:
                    name = getattr(candidate_info, 'name', "Unknown") or "Unknown"
                    email = getattr(candidate_info, 'email', "Not provided") or "Not provided"
            else:
                name = resume_analysis.candidate_info.name or "Unknown"
                email = resume_analysis.candidate_info.email or "Not provided"
            
            logger.info(f"Candidate: {name}")
            logger.info(f"Email: {email}")
        
        if screening_score:
            # Handle both dict and Pydantic model
            if isinstance(screening_score, dict):
                score = screening_score.get("score", 0)
                classification = screening_score.get("classification", "Unknown")
                skill_match = screening_score.get("skill_match_percentage", 0)
            else:
                score = screening_score.score
                classification = screening_score.classification
                skill_match = screening_score.skill_match_percentage
            
            logger.info(f"Score: {score}/100")
            logger.info(f"Classification: {classification}")
            logger.info(f"Skill Match: {skill_match:.1f}%")
        
        if decision:
            logger.info(f"Decision: {decision.upper()}")
        
        human_review = self.should_require_human_review(state)
        logger.info(f"Human Review Required: {'Yes' if human_review else 'No'}")
        
        logger.info("="*60 + "\n")
    
    def handle_error(self, state: Dict) -> Dict:
        """
        Handle errors in workflow.
        
        Args:
            state: Current state with error
            
        Returns:
            Error handling response
        """
        error = state.get("error", "Unknown error")
        logger.error(f"Workflow Error: {error}")
        
        return {
            "current_step": "failed",
            "decision": "review",
            "error": error
        }
