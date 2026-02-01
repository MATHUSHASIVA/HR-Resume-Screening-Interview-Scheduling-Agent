"""
Agent 1: Resume Analyzer
Responsible for extracting information from resumes and scoring candidates.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict

from src.models import ResumeAnalysis, ScreeningScore, AgentState, JobRequirements
from src.config import GROQ_API_KEY, LLM_MODEL, SCORING_WEIGHTS
from src.utils import setup_logger, retry_on_failure, calculate_skill_match, ValidationError


logger = setup_logger(__name__)


class ResumeAnalyzerAgent:
    """Agent for analyzing resumes and scoring candidates."""
    
    def __init__(self):
        """Initialize the Resume Analyzer agent."""
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0.1,
        )
        logger.info("Resume Analyzer Agent initialized")
    
    @retry_on_failure(max_retries=3)
    def extract_resume_data(self, resume_text: str) -> ResumeAnalysis:
        """
        Extract structured information from resume text.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            ResumeAnalysis object with extracted information
        """
        logger.info("Starting resume data extraction")
        
        parser = PydanticOutputParser(pydantic_object=ResumeAnalysis)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR analyst specializing in resume parsing.
Extract detailed information from the resume and structure it precisely.

Key Instructions:
- Extract ALL skills mentioned (technical and soft skills)
- Parse work experience with complete details
- Calculate total years of experience accurately
- Extract education with degrees and institutions
- Identify contact information carefully
- Provide a concise professional summary

{format_instructions}"""),
            ("user", "Resume:\n\n{resume_text}")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "resume_text": resume_text,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Parse the response content
            parsed = parser.parse(response.content)
            
            logger.info(f"Successfully extracted resume data for: {parsed.candidate_info.name or 'Unknown'}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error in resume extraction: {e}")
            # Fallback: try with more explicit prompting
            return self._extract_with_structured_output(resume_text)
    
    def _extract_with_structured_output(self, resume_text: str) -> ResumeAnalysis:
        """Fallback method using structured output."""
        logger.info("Using structured output fallback for resume extraction")
        
        llm_with_structure = self.llm.with_structured_output(ResumeAnalysis)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract structured information from the resume.
Focus on: candidate info, skills, experience, education, and years of experience.
Be thorough and accurate."""),
            ("user", "{resume_text}")
        ])
        
        chain = prompt | llm_with_structure
        result = chain.invoke({"resume_text": resume_text})
        
        return result
    
    @retry_on_failure(max_retries=3)
    def score_candidate(
        self, 
        resume_analysis: ResumeAnalysis, 
        job_requirements: JobRequirements
    ) -> ScreeningScore:
        """
        Score candidate against job requirements.
        
        Args:
            resume_analysis: Parsed resume data
            job_requirements: Job requirements to match against
            
        Returns:
            ScreeningScore with detailed evaluation
        """
        logger.info(f"Scoring candidate: {resume_analysis.candidate_info.name}")
        
        # Calculate skill match
        skill_match = calculate_skill_match(
            resume_analysis.skills,
            job_requirements.required_skills + job_requirements.preferred_skills
        )
        
        parser = PydanticOutputParser(pydantic_object=ScreeningScore)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR screener evaluating candidates.

Scoring Criteria:
1. Skills Match (40%): How well candidate's skills align with required/preferred skills
2. Experience (25%): Years and relevance of work experience
3. Education (15%): Educational background match
4. Overall Relevance (20%): Domain knowledge and career trajectory

Scoring Guidelines:
- 85-100: Exceptional fit, exceeds requirements
- 75-84: Strong fit, meets all key requirements
- 60-74: Moderate fit, meets most requirements
- 50-59: Marginal fit, missing some key requirements
- 0-49: Not suitable, significant gaps

Classification Rules:
- Score >= 75: "Strong Fit"
- Score 50-74: "Moderate Fit"
- Score < 50: "Not Suitable"

Provide detailed reasoning, specific strengths, and any gaps.

{format_instructions}"""),
            ("user", """Job Requirements:
Title: {job_title}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Min Experience: {min_experience} years
Education: {education}

Candidate Profile:
Name: {candidate_name}
Skills: {candidate_skills}
Experience: {years_experience} years
Education: {candidate_education}
Summary: {candidate_summary}

Calculated Skill Match: {skill_match}%

Provide a comprehensive screening evaluation.""")
        ])
        
        try:
            chain = prompt | self.llm
            
            response = chain.invoke({
                "job_title": job_requirements.title,
                "required_skills": ", ".join(job_requirements.required_skills),
                "preferred_skills": ", ".join(job_requirements.preferred_skills),
                "min_experience": job_requirements.min_years_experience or 0,
                "education": ", ".join(job_requirements.education_requirements),
                "candidate_name": resume_analysis.candidate_info.name or "Unknown",
                "candidate_skills": ", ".join(resume_analysis.skills),
                "years_experience": resume_analysis.years_of_experience or 0,
                "candidate_education": ", ".join([f"{e.degree} from {e.institution}" for e in resume_analysis.education]),
                "candidate_summary": resume_analysis.summary,
                "skill_match": round(skill_match, 1),
                "format_instructions": parser.get_format_instructions()
            })
            
            parsed = parser.parse(response.content)
            
            logger.info(f"Candidate scored: {parsed.score}/100 - {parsed.classification}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error in candidate scoring: {e}")
            return self._score_with_structured_output(resume_analysis, job_requirements, skill_match)
    
    def _score_with_structured_output(
        self, 
        resume_analysis: ResumeAnalysis, 
        job_requirements: JobRequirements,
        skill_match: float
    ) -> ScreeningScore:
        """Fallback scoring method."""
        logger.info("Using structured output fallback for scoring")
        
        llm_with_structure = self.llm.with_structured_output(ScreeningScore)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Evaluate this candidate against job requirements. Score 0-100, classify fit level, explain reasoning."),
            ("user", """Job: {job_title}
Required: {required_skills}
Candidate Skills: {candidate_skills}
Experience: {years_experience} years (Min: {min_experience})
Skill Match: {skill_match}%

Provide screening score and classification.""")
        ])
        
        chain = prompt | llm_with_structure
        
        result = chain.invoke({
            "job_title": job_requirements.title,
            "required_skills": ", ".join(job_requirements.required_skills),
            "candidate_skills": ", ".join(resume_analysis.skills),
            "years_experience": resume_analysis.years_of_experience or 0,
            "min_experience": job_requirements.min_years_experience or 0,
            "skill_match": round(skill_match, 1)
        })
        
        return result
    
    def process(self, state: Dict) -> Dict:
        """
        Main processing method for the agent node.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with resume analysis and screening score
        """
        logger.info("=== Resume Analyzer Agent: Processing ===")
        
        try:
            # Convert job_requirements dict to Pydantic model if needed
            from src.models import JobRequirements
            job_req = state["job_requirements"]
            if isinstance(job_req, dict):
                job_req = JobRequirements(**job_req)
            
            # Extract resume data
            resume_analysis = self.extract_resume_data(state["resume_text"])
            
            # Score candidate
            screening_score = self.score_candidate(
                resume_analysis, 
                job_req
            )
            
            # Update state
            return {
                "resume_analysis": resume_analysis,
                "screening_score": screening_score,
                "current_step": "analyzed"
            }
            
        except Exception as e:
            logger.error(f"Resume Analyzer failed: {e}")
            return {
                "error": f"Resume analysis failed: {str(e)}",
                "current_step": "error"
            }
