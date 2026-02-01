"""
Main entry point for the HR Screening System.
"""

import json
from pathlib import Path
from datetime import datetime

from src.models import AgentState, JobRequirements
from src.workflow import HRScreeningWorkflow
from src.utils import setup_logger, extract_text_from_pdf, sanitize_text


logger = setup_logger(__name__)


def load_job_requirements(job_file: str) -> JobRequirements:
    """Load job requirements from JSON file."""
    logger.info(f"Loading job requirements from: {job_file}")
    
    with open(job_file, 'r') as f:
        data = json.load(f)
    
    return JobRequirements(**data)


def load_resume(resume_file: str) -> str:
    """Load resume from text or PDF file."""
    logger.info(f"Loading resume from: {resume_file}")
    
    file_path = Path(resume_file)
    
    if file_path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(resume_file)
    else:
        with open(resume_file, 'r', encoding='utf-8') as f:
            text = f.read()
    
    return sanitize_text(text)


def save_results(state: AgentState, output_dir: str = "output"):
    """Save workflow results to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate_name = "unknown"
    
    if state.resume_analysis and state.resume_analysis.candidate_info.name:
        candidate_name = state.resume_analysis.candidate_info.name.replace(" ", "_").lower()
    
    filename = f"{candidate_name}_{timestamp}.json"
    filepath = output_path / filename
    
    # Convert to dict for JSON serialization
    results = {
        "candidate_info": state.resume_analysis.candidate_info.dict() if state.resume_analysis else None,
        "screening_score": state.screening_score.dict() if state.screening_score else None,
        "decision": state.decision,
        "interview_coordination": state.interview_coordination.dict() if state.interview_coordination else None,
        "timestamp": state.timestamp.isoformat(),
        "error": state.error
    }
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {filepath}")
    return filepath


def print_results(state: AgentState):
    """Print formatted results to console."""
    print("\n" + "="*70)
    print("HR SCREENING RESULTS")
    print("="*70 + "\n")
    
    # Candidate Info
    if state.resume_analysis:
        info = state.resume_analysis.candidate_info
        print(f"📋 CANDIDATE INFORMATION")
        print(f"   Name: {info.name or 'Not provided'}")
        print(f"   Email: {info.email or 'Not provided'}")
        print(f"   Phone: {info.phone or 'Not provided'}")
        print(f"   Location: {info.location or 'Not provided'}\n")
    
    # Screening Score
    if state.screening_score:
        score = state.screening_score
        print(f"🎯 SCREENING EVALUATION")
        print(f"   Score: {score.score}/100")
        print(f"   Classification: {score.classification}")
        print(f"   Skill Match: {score.skill_match_percentage:.1f}%")
        print(f"\n   Reasoning: {score.reasoning}\n")
        
        if score.strengths:
            print(f"   ✅ Strengths:")
            for strength in score.strengths:
                print(f"      • {strength}")
        
        if score.gaps:
            print(f"\n   ⚠️  Gaps:")
            for gap in score.gaps:
                print(f"      • {gap}")
        print()
    
    # Decision
    if state.decision:
        decision_emoji = "✅" if state.decision == "accept" else "❌"
        print(f"{decision_emoji} DECISION: {state.decision.upper()}\n")
    
    # Interview Coordination
    if state.interview_coordination:
        coord = state.interview_coordination
        
        if state.decision == "accept":
            print(f"📅 INTERVIEW COORDINATION")
            print(f"\n   Interview Questions ({len(coord.interview_questions)} total):")
            for i, q in enumerate(coord.interview_questions[:3], 1):  # Show first 3
                print(f"      {i}. [{q.category}] {q.question}")
            
            if coord.interview_slots:
                print(f"\n   📅 Proposed Time Slots (Business Hours: 10 AM-12 PM or 2 PM-5 PM):")
                for i, slot in enumerate(coord.interview_slots, 1):
                    if i == 1:
                        print(f"      {i}. {slot.date} at {slot.time} ({slot.timezone}) 🔒 AUTO-BOOKED")
                    else:
                        print(f"      {i}. {slot.date} at {slot.time} ({slot.timezone}) ✓ Available")
                if coord.interview_slots:
                    print(f"\n      ℹ️  Notes:")
                    print(f"         • First slot automatically booked")
                    print(f"         • All slots validated: weekdays only, no holidays, business hours")
                    print(f"         • Conflicts checked against existing bookings")
            
            if coord.recommended_interviewers:
                print(f"\n   Recommended Interviewers:")
                for interviewer in coord.recommended_interviewers:
                    print(f"      • {interviewer}")
        
        # Email
        if coord.email_template:
            email = coord.email_template
            print(f"\n📧 EMAIL PREVIEW")
            print(f"   Subject: {email.subject}")
            print(f"   ---")
            print(f"   {email.body[:300]}...")
            print()
    
    # Error
    if state.error:
        print(f"❌ ERROR: {state.error}\n")
    
    print("="*70 + "\n")


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("HR RESUME SCREENING & INTERVIEW SCHEDULING SYSTEM")
    print("Powered by LangGraph & Groq")
    print("="*70 + "\n")
    
    # Example: Process a candidate
    job_file = "data/job_descriptions/ai_engineer.json"
    resume_file = "data/resumes/candidate_strong_fit.txt"
    
    try:
        # Load data
        job_requirements = load_job_requirements(job_file)
        resume_text = load_resume(resume_file)
        
        # Create initial state
        initial_state = AgentState(
            resume_text=resume_text,
            job_requirements=job_requirements,
            candidate_id=f"CAND_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Initialize and run workflow
        workflow = HRScreeningWorkflow()
        
        # Print workflow description
        print(workflow.get_workflow_description())
        
        # Execute workflow
        final_state = workflow.run(initial_state)
        
        # Print results
        print_results(final_state)
        
        # Save results (create directory if needed)
        from pathlib import Path
        Path("output").mkdir(parents=True, exist_ok=True)
        output_file = save_results(final_state)
        print(f"✅ Results saved to: {output_file}")
        
        # Show booking info if candidate was accepted
        if final_state.decision == "accept" and final_state.interview_coordination:
            slots = final_state.interview_coordination.interview_slots
            if slots:
                print(f"\n📅 Interview Slot Auto-Booked:")
                print(f"   Date: {slots[0].date}")
                print(f"   Time: {slots[0].time} ({slots[0].timezone})")
                print(f"   Duration: 60 minutes")
                print(f"\n📊 Booking Management:")
                print(f"   • View all bookings: python src/view_bookings.py")
                print(f"   • Manage bookings: python src/manage_bookings.py")
        
        # Try to visualize workflow
        try:
            workflow.visualize("workflow_diagram.png")
        except Exception as e:
            logger.warning(f"Could not generate visualization: {e}")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
