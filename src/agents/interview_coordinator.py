"""
Agent 2: Interview Coordinator
Generates interview questions, email templates, and schedules.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from datetime import datetime, timedelta
from typing import Dict, List

from src.models import (
    InterviewCoordination, InterviewQuestion, EmailTemplate, 
    InterviewSlot, ResumeAnalysis, ScreeningScore, JobRequirements
)
from src.config import (
    GROQ_API_KEY, LLM_MODEL, NUM_INTERVIEW_QUESTIONS, 
    NUM_INTERVIEW_SLOTS, COMPANY_NAME, HR_SIGNATURE, 
    INTERVIEW_AVAILABILITY, DEFAULT_INTERVIEW_DURATION
)
from src.utils import (
    setup_logger, retry_on_failure, format_duration, 
    load_booked_slots, save_booking, is_slot_available,
    is_holiday, is_within_business_hours
)


logger = setup_logger(__name__)


class InterviewCoordinatorAgent:
    """Agent for coordinating interviews and generating communications."""
    
    def __init__(self):
        """Initialize the Interview Coordinator agent."""
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0.3,  # Slightly higher for creative questions
        )
        logger.info("Interview Coordinator Agent initialized")
    
    @retry_on_failure(max_retries=3)
    def generate_interview_questions(
        self,
        resume_analysis: ResumeAnalysis,
        job_requirements: JobRequirements,
        screening_score: ScreeningScore
    ) -> List[InterviewQuestion]:
        """
        Generate personalized interview questions based on candidate background.
        
        Args:
            resume_analysis: Candidate's resume data
            job_requirements: Job requirements
            screening_score: Screening evaluation
            
        Returns:
            List of interview questions
        """
        logger.info("Generating interview questions")
        
        llm_with_structure = self.llm.with_structured_output(
            InterviewQuestion
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert interviewer designing targeted interview questions.

Create ONE highly relevant interview question based on:
- Candidate's specific background and experience
- Job requirements and responsibilities
- Identified strengths and gaps from screening

Question Categories:
- Technical: Assess specific technical skills
- Behavioral: Evaluate soft skills and work style
- Experience: Deep dive into past projects
- Problem-Solving: Assess analytical thinking
- Culture Fit: Alignment with company values

Make questions:
- Specific to this candidate's background
- Open-ended and thought-provoking
- Relevant to job requirements
- Professional and respectful"""),
            ("user", """Job: {job_title}
Key Responsibilities: {responsibilities}

Candidate Background:
- Skills: {skills}
- Experience: {experience_summary}
- Strengths: {strengths}
- Areas to probe: {gaps}

Generate ONE {category} interview question.""")
        ])
        
        chain = prompt | llm_with_structure
        
        # Define question categories
        categories = [
            "Technical", "Technical", "Technical",
            "Behavioral", "Behavioral",
            "Experience", "Experience",
            "Problem-Solving"
        ]
        
        questions = []
        
        for category in categories[:NUM_INTERVIEW_QUESTIONS]:
            try:
                question = chain.invoke({
                    "job_title": job_requirements.title,
                    "responsibilities": ", ".join(job_requirements.responsibilities[:3]),
                    "skills": ", ".join(resume_analysis.skills[:10]),
                    "experience_summary": resume_analysis.summary[:200],
                    "strengths": ", ".join(screening_score.strengths[:3]),
                    "gaps": ", ".join(screening_score.gaps[:2]) if screening_score.gaps else "None identified",
                    "category": category
                })
                questions.append(question)
                
            except Exception as e:
                logger.warning(f"Failed to generate {category} question: {e}")
        
        logger.info(f"Generated {len(questions)} interview questions")
        return questions
    
    @retry_on_failure(max_retries=3)
    def generate_invitation_email(
        self,
        resume_analysis: ResumeAnalysis,
        job_requirements: JobRequirements,
        screening_score: ScreeningScore,
        interview_slots: List[InterviewSlot]
    ) -> EmailTemplate:
        """Generate invitation email for qualified candidates."""
        logger.info("Generating invitation email")
        
        llm_with_structure = self.llm.with_structured_output(EmailTemplate)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are writing a professional interview invitation email for {COMPANY_NAME}.

Guidelines:
- Warm and welcoming tone
- Express genuine interest in the candidate
- Clearly state the position
- Present ONE scheduled interview time slot
- State the specific date, time, and timezone clearly
- Mention the interview duration
- Ask candidate to confirm their availability for this specific time
- Be concise and professional
- Use proper paragraph breaks (double newlines \\n\\n between paragraphs)
- End with {COMPANY_NAME} signature on a new line

IMPORTANT: Present ONLY ONE scheduled interview time slot, not multiple options.

Format:
Dear [Name],

[Introduction and interest paragraph expressing interest in the candidate]

[Interview details paragraph with THE scheduled time slot, duration, and asking for confirmation]

[Closing paragraph]

{HR_SIGNATURE}"""),
            ("user", """Candidate: {candidate_name}
Position: {job_title}
Candidate Strengths: {strengths}

Scheduled Interview Time Slot:
{time_slot}

Duration: {duration}

Create an engaging invitation email with the scheduled interview time and ask them to confirm their availability.""")
        ])
        
        chain = prompt | llm_with_structure
        
        # Use only the first available slot (which is auto-booked)
        first_slot = interview_slots[0] if interview_slots else None
        if not first_slot:
            raise ValueError("No interview slots available")
        
        slots_text = f"{first_slot.date} at {first_slot.time} ({first_slot.timezone})"
        
        result = chain.invoke({
            "candidate_name": resume_analysis.candidate_info.name or "Candidate",
            "job_title": job_requirements.title,
            "strengths": ", ".join(screening_score.strengths[:2]),
            "time_slot": slots_text,
            "duration": format_duration(DEFAULT_INTERVIEW_DURATION)
        })
        
        logger.info("Invitation email generated")
        return result
    
    @retry_on_failure(max_retries=3)
    def generate_rejection_email(
        self,
        resume_analysis: ResumeAnalysis,
        job_requirements: JobRequirements,
        screening_score: ScreeningScore
    ) -> EmailTemplate:
        """Generate rejection email with constructive feedback."""
        logger.info("Generating rejection email")
        
        llm_with_structure = self.llm.with_structured_output(EmailTemplate)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are writing a professional rejection email for {COMPANY_NAME}.

Guidelines:
- Respectful and empathetic tone
- Thank them for their interest
- Provide brief, constructive feedback (1-2 sentences)
- Encourage future applications
- Keep it concise and professional
- Use proper paragraph breaks (double newlines \\n\\n between paragraphs)
- End with {COMPANY_NAME} signature on a new line

Format:
Dear [Name],

[Thank you paragraph]

[Feedback paragraph]

[Encouragement paragraph]

{HR_SIGNATURE}"""),
            ("user", """Candidate: {candidate_name}
Position: {job_title}
Feedback Points: {gaps}

Create a respectful rejection email with constructive feedback and proper formatting.""")
        ])
        
        chain = prompt | llm_with_structure
        
        result = chain.invoke({
            "candidate_name": resume_analysis.candidate_info.name or "Candidate",
            "job_title": job_requirements.title,
            "gaps": ", ".join(screening_score.gaps[:2]) if screening_score.gaps else "role requirements"
        })
        
        logger.info("Rejection email generated")
        return result
    
    def generate_interview_slots(self) -> List[InterviewSlot]:
        """Generate proposed interview time slots, checking for existing bookings, holidays, and business hours."""
        logger.info("Generating interview time slots with availability, holiday, and business hours check")
        
        slots = []
        start_date = datetime.now() + timedelta(days=2)  # Start 2 days from now
        
        times = INTERVIEW_AVAILABILITY["preferred_times"]
        timezone = INTERVIEW_AVAILABILITY["timezone"]
        
        # Filter times to only include those within business hours
        valid_times = [t for t in times if is_within_business_hours(t)]
        
        if not valid_times:
            logger.error("No valid times within business hours (10 AM - 12 PM or 2 PM - 5 PM)")
            return slots
        
        logger.info(f"Valid business hours times: {', '.join(valid_times)}")
        
        # Try to generate NUM_INTERVIEW_SLOTS available slots
        max_attempts = NUM_INTERVIEW_SLOTS * 15  # Prevent infinite loop
        attempt_count = 0
        slot_date = start_date
        time_index = 0
        
        while len(slots) < NUM_INTERVIEW_SLOTS and attempt_count < max_attempts:
            attempt_count += 1
            
            # Skip weekends
            while slot_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                slot_date += timedelta(days=1)
            
            # Skip holidays
            if is_holiday(slot_date):
                logger.info(f"Skipping holiday: {slot_date.strftime('%A, %B %d, %Y')}")
                slot_date += timedelta(days=1)
                continue
            
            # Create proposed slot
            proposed_date = slot_date.strftime("%A, %B %d, %Y")
            proposed_time = valid_times[time_index % len(valid_times)]
            
            # Validate business hours (double-check)
            if not is_within_business_hours(proposed_time):
                logger.warning(f"Time {proposed_time} is outside business hours, skipping")
                time_index += 1
                continue
            
            # Check if slot is available (not already booked)
            if is_slot_available(proposed_date, proposed_time):
                slot = InterviewSlot(
                    date=proposed_date,
                    time=proposed_time,
                    duration_minutes=DEFAULT_INTERVIEW_DURATION,
                    timezone=timezone
                )
                slots.append(slot)
                logger.info(f"✓ Available slot found: {proposed_date} at {proposed_time}")
            else:
                logger.info(f"✗ Slot already booked: {proposed_date} at {proposed_time}")
            
            # Move to next time slot
            time_index += 1
            
            # If we've tried all times for this day, move to next day
            if time_index % len(valid_times) == 0:
                slot_date += timedelta(days=1)
        
        if len(slots) < NUM_INTERVIEW_SLOTS:
            logger.warning(f"Only found {len(slots)} available slots out of {NUM_INTERVIEW_SLOTS} requested")
        else:
            logger.info(f"Generated {len(slots)} available interview slots")
        
        return slots
    
    def suggest_interviewers(
        self,
        job_requirements: JobRequirements,
        resume_analysis: ResumeAnalysis
    ) -> List[str]:
        """Suggest appropriate interviewers based on candidate background."""
        
        # Simple logic: suggest based on role and department
        interviewers = ["HR Manager"]
        
        if job_requirements.department:
            interviewers.append(f"{job_requirements.department} Lead")
        
        # Add technical interviewer for technical roles
        technical_keywords = ["engineer", "developer", "data", "software", "tech"]
        if any(keyword in job_requirements.title.lower() for keyword in technical_keywords):
            interviewers.append("Technical Lead")
        
        # Add senior team member
        if resume_analysis.years_of_experience and resume_analysis.years_of_experience > 5:
            interviewers.append("Senior Team Member")
        
        logger.info(f"Suggested interviewers: {', '.join(interviewers)}")
        return interviewers
    
    def process_qualified(self, state: Dict) -> Dict:
        """
        Process qualified candidates (score > 70).
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with interview coordination
        """
        logger.info("=== Interview Coordinator Agent: Processing Qualified Candidate ===")
        
        try:
            # Convert dicts back to Pydantic models if needed
            from src.models import ResumeAnalysis, ScreeningScore, JobRequirements
            
            resume_analysis = state["resume_analysis"]
            if isinstance(resume_analysis, dict):
                resume_analysis = ResumeAnalysis(**resume_analysis)
            
            job_requirements = state["job_requirements"]
            if isinstance(job_requirements, dict):
                job_requirements = JobRequirements(**job_requirements)
            
            screening_score = state["screening_score"]
            if isinstance(screening_score, dict):
                screening_score = ScreeningScore(**screening_score)
            
            # Generate interview questions
            questions = self.generate_interview_questions(
                resume_analysis, job_requirements, screening_score
            )
            
            # Generate interview slots
            slots = self.generate_interview_slots()
            
            # Automatically book the first slot for the candidate
            if slots:
                first_slot = slots[0]
                candidate_name = resume_analysis.candidate_info.name or "Unknown Candidate"
                save_booking(
                    candidate_name=candidate_name,
                    date=first_slot.date,
                    time=first_slot.time,
                    timezone=first_slot.timezone
                )
                logger.info(f"Automatically booked first slot for {candidate_name}")
            
            # Generate invitation email
            email = self.generate_invitation_email(
                resume_analysis, job_requirements, screening_score, slots
            )
            
            # Suggest interviewers
            interviewers = self.suggest_interviewers(job_requirements, resume_analysis)
            
            coordination = InterviewCoordination(
                interview_questions=questions,
                email_template=email,
                interview_slots=slots,
                recommended_interviewers=interviewers
            )
            
            logger.info("Interview coordination completed for qualified candidate")
            
            return {
                "interview_coordination": coordination,
                "decision": "accept",
                "current_step": "coordinated"
            }
            
        except Exception as e:
            logger.error(f"Interview coordination failed: {e}")
            return {
                "error": f"Interview coordination failed: {str(e)}",
                "current_step": "error"
            }
    
    def process_rejected(self, state: Dict) -> Dict:
        """
        Process rejected candidates.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with rejection email
        """
        logger.info("=== Interview Coordinator Agent: Processing Rejected Candidate ===")
        
        try:
            # Convert dicts back to Pydantic models if needed
            from src.models import ResumeAnalysis, ScreeningScore, JobRequirements
            
            resume_analysis = state.get("resume_analysis")
            if resume_analysis and isinstance(resume_analysis, dict):
                resume_analysis = ResumeAnalysis(**resume_analysis)
            
            job_requirements = state["job_requirements"]
            if isinstance(job_requirements, dict):
                job_requirements = JobRequirements(**job_requirements)
            
            screening_score = state.get("screening_score")
            if screening_score and isinstance(screening_score, dict):
                screening_score = ScreeningScore(**screening_score)
            
            # Generate rejection email
            email = self.generate_rejection_email(
                resume_analysis, job_requirements, screening_score
            )
            
            coordination = InterviewCoordination(
                interview_questions=[],
                email_template=email,
                interview_slots=[],
                recommended_interviewers=[]
            )
            
            logger.info("Rejection email generated")
            
            return {
                "interview_coordination": coordination,
                "decision": "reject",
                "current_step": "coordinated"
            }
            
        except Exception as e:
            logger.error(f"Rejection processing failed: {e}")
            return {
                "error": f"Rejection processing failed: {str(e)}",
                "current_step": "error"
            }
