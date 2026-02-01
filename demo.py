"""
Interactive demo script for testing different candidates.
"""

import json
from pathlib import Path

from src.models import AgentState, JobRequirements
from src.workflow import HRScreeningWorkflow
from src.utils import setup_logger
from main import load_job_requirements, load_resume, print_results, save_results


logger = setup_logger(__name__)


def run_demo():
    """Run demo with multiple candidates."""
    print("\n" + "="*70)
    print("HR SCREENING SYSTEM - DEMO MODE")
    print("="*70 + "\n")
    
    # Load job requirements
    job_file = "data/job_descriptions/ai_engineer.json"
    job_requirements = load_job_requirements(job_file)
    
    print(f"📋 Job Position: {job_requirements.title}")
    print(f"🔧 Required Skills: {', '.join(job_requirements.required_skills[:5])}...")
    print(f"⏱️  Min Experience: {job_requirements.min_years_experience} years\n")
    
    # Test candidates
    candidates = [
        {
            "name": "Strong Fit Candidate (Nethmika Perera)",
            "file": "data/resumes/candidate_strong_fit.txt",
            "expected": "Should PASS (score >= 70)"
        },
        {
            "name": "Moderate Fit Candidate (Amali Fernando)",
            "file": "data/resumes/candidate_moderate_fit.txt",
            "expected": "May PASS or FAIL (borderline)"
        },
        {
            "name": "Not Suitable Candidate (Kavindu Silva)",
            "file": "data/resumes/candidate_not_suitable.txt",
            "expected": "Should FAIL (score < 70)"
        }
    ]
    
    # Initialize workflow once
    workflow = HRScreeningWorkflow()
    
    results_summary = []
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{'='*70}")
        print(f"PROCESSING CANDIDATE {i}/3: {candidate['name']}")
        print(f"Expected: {candidate['expected']}")
        print(f"{'='*70}\n")
        
        try:
            # Load resume
            resume_text = load_resume(candidate['file'])
            
            # Create state
            state = AgentState(
                resume_text=resume_text,
                job_requirements=job_requirements,
                candidate_id=f"DEMO_CAND_{i}"
            )
            
            # Run workflow
            final_state = workflow.run(state)
            
            # Print results
            print_results(final_state)
            
            # Save results
            from pathlib import Path
            Path("output/demo").mkdir(parents=True, exist_ok=True)
            save_results(final_state, output_dir="output/demo")
            
            # Collect summary
            if final_state.screening_score:
                results_summary.append({
                    "name": candidate['name'],
                    "score": final_state.screening_score.score,
                    "classification": final_state.screening_score.classification,
                    "decision": final_state.decision,
                    "expected": candidate['expected']
                })
            
            # Pause between candidates
            if i < len(candidates):
                input("\nPress Enter to continue to next candidate...")
        
        except Exception as e:
            logger.error(f"Failed to process {candidate['name']}: {e}")
            results_summary.append({
                "name": candidate['name'],
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "="*70)
    print("DEMO SUMMARY")
    print("="*70 + "\n")
    
    for result in results_summary:
        if "error" in result:
            print(f"❌ {result['name']}: ERROR - {result['error']}")
        else:
            decision_emoji = "✅" if result['decision'] == "accept" else "❌"
            print(f"{decision_emoji} {result['name']}")
            print(f"   Score: {result['score']}/100")
            print(f"   Classification: {result['classification']}")
            print(f"   Decision: {result['decision'].upper()}")
            print(f"   Expected: {result['expected']}\n")
    
    print("="*70)
    print("✅ Demo completed!")
    print("📁 Results saved in: output/demo/")
    print("\n💡 Tip: Check booked interview slots with: python view_bookings.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()
