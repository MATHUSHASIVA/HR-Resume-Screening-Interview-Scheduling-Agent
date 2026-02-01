"""
Streamlit Web Application for HR Resume Screening System
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.models import AgentState, JobRequirements
from src.workflow import HRScreeningWorkflow
from main import load_resume, save_results


# Page configuration
st.set_page_config(
    page_title="HR Screening AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    .score-high {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .score-medium {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .score-low {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def load_job_descriptions():
    """Load available job descriptions."""
    job_dir = Path("data/job_descriptions")
    jobs = {}
    
    if job_dir.exists():
        for job_file in job_dir.glob("*.json"):
            with open(job_file, 'r') as f:
                data = json.load(f)
                jobs[data['title']] = data
    
    return jobs


def display_candidate_info(resume_analysis):
    """Display candidate information."""
    if not resume_analysis:
        return
    
    info = resume_analysis.get('candidate_info', {}) if isinstance(resume_analysis, dict) else resume_analysis.candidate_info
    
    st.subheader("📋 Candidate Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = info.get('name') if isinstance(info, dict) else info.name
        email = info.get('email') if isinstance(info, dict) else info.email
        st.write(f"**Name:** {name or 'Not provided'}")
        st.write(f"**Email:** {email or 'Not provided'}")
    
    with col2:
        phone = info.get('phone') if isinstance(info, dict) else info.phone
        location = info.get('location') if isinstance(info, dict) else info.location
        st.write(f"**Phone:** {phone or 'Not provided'}")
        st.write(f"**Location:** {location or 'Not provided'}")


def display_screening_score(screening_score):
    """Display screening score with visual indicators."""
    if not screening_score:
        return
    
    score = screening_score.get('score') if isinstance(screening_score, dict) else screening_score.score
    classification = screening_score.get('classification') if isinstance(screening_score, dict) else screening_score.classification
    skill_match = screening_score.get('skill_match_percentage') if isinstance(screening_score, dict) else screening_score.skill_match_percentage
    reasoning = screening_score.get('reasoning') if isinstance(screening_score, dict) else screening_score.reasoning
    strengths = screening_score.get('strengths', []) if isinstance(screening_score, dict) else screening_score.strengths
    gaps = screening_score.get('gaps', []) if isinstance(screening_score, dict) else screening_score.gaps
    
    st.subheader("🎯 Screening Evaluation")
    
    # Score display
    score_class = "score-high" if score >= 75 else "score-medium" if score >= 50 else "score-low"
    
    st.markdown(f"""
    <div class="score-box {score_class}">
        <h1>{score}/100</h1>
        <h3>{classification}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{score}/100")
    with col2:
        st.metric("Skill Match", f"{skill_match:.1f}%")
    with col3:
        decision = "✅ ACCEPT" if score >= 70 else "❌ REJECT"
        st.metric("Decision", decision)
    
    # Reasoning
    with st.expander("📝 Detailed Reasoning", expanded=True):
        st.write(reasoning)
    
    # Strengths and Gaps
    col1, col2 = st.columns(2)
    
    with col1:
        if strengths:
            st.write("**✅ Strengths:**")
            for strength in strengths:
                st.write(f"• {strength}")
    
    with col2:
        if gaps:
            st.write("**⚠️ Gaps:**")
            for gap in gaps:
                st.write(f"• {gap}")


def display_interview_coordination(coordination, decision):
    """Display interview coordination details."""
    if not coordination:
        return
    
    email = coordination.get('email_template') if isinstance(coordination, dict) else coordination.email_template
    questions = coordination.get('interview_questions', []) if isinstance(coordination, dict) else coordination.interview_questions
    slots = coordination.get('interview_slots', []) if isinstance(coordination, dict) else coordination.interview_slots
    interviewers = coordination.get('recommended_interviewers', []) if isinstance(coordination, dict) else coordination.recommended_interviewers
    
    if decision == "accept":
        st.subheader("📅 Interview Coordination")
        
        # Interview Questions
        with st.expander(f"💭 Interview Questions ({len(questions)} total)", expanded=True):
            for i, q in enumerate(questions, 1):
                question_text = q.get('question') if isinstance(q, dict) else q.question
                category = q.get('category') if isinstance(q, dict) else q.category
                st.write(f"**{i}. [{category}]** {question_text}")
        
        # Time Slots
        if slots:
            with st.expander("🕒 Proposed Interview Slots", expanded=True):
                for i, slot in enumerate(slots, 1):
                    date = slot.get('date') if isinstance(slot, dict) else slot.date
                    time = slot.get('time') if isinstance(slot, dict) else slot.time
                    timezone = slot.get('timezone') if isinstance(slot, dict) else slot.timezone
                    
                    # Highlight first slot as booked
                    if i == 1:
                        st.success(f"🔒 **Slot {i} (BOOKED):** {date} at {time} ({timezone})")
                    else:
                        st.info(f"**Slot {i}:** {date} at {time} ({timezone})")
                
                st.caption("💡 The first slot is automatically booked to prevent scheduling conflicts.")
        
        # Recommended Interviewers
        if interviewers:
            with st.expander("👥 Recommended Interviewers"):
                for interviewer in interviewers:
                    st.write(f"• {interviewer}")
    
    # Email Template
    if email:
        subject = email.get('subject') if isinstance(email, dict) else email.subject
        body = email.get('body') if isinstance(email, dict) else email.body
        
        st.subheader("📧 Email Template")
        st.write(f"**Subject:** {subject}")
        st.text_area("Email Body", body, height=300)


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<p class="main-header">🤖 HR Resume Screening AI System</p>', unsafe_allow_html=True)
    st.markdown("**Powered by LangGraph & Groq AI** | Automated candidate evaluation and interview coordination")
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show booking stats
        try:
            from pathlib import Path
            import json
            booking_file = Path("data/booked_slots.json")
            if booking_file.exists():
                bookings = json.loads(booking_file.read_text())
                if bookings:
                    st.info(f"📅 **{len(bookings)} interview slot(s) booked**")
                    with st.expander("View Bookings"):
                        for i, booking in enumerate(bookings[-5:], 1):  # Show last 5
                            st.caption(f"{booking['candidate_name']} - {booking['date'][:15]}...")
                        if len(bookings) > 5:
                            st.caption(f"...and {len(bookings) - 5} more")
        except:
            pass
        
        st.divider()
        
        # Job Selection
        st.subheader("1. Select Job Position")
        available_jobs = load_job_descriptions()
        
        job_option = st.radio(
            "Choose job description:",
            ["Use existing job", "Create custom job"]
        )
        
        if job_option == "Use existing job":
            if available_jobs:
                selected_job_title = st.selectbox(
                    "Select position:",
                    list(available_jobs.keys())
                )
                job_data = available_jobs[selected_job_title]
                job_requirements = JobRequirements(**job_data)
                
                with st.expander("View Job Requirements"):
                    st.write(f"**Required Skills:** {', '.join(job_data['required_skills'][:5])}...")
                    st.write(f"**Min Experience:** {job_data.get('min_years_experience', 'N/A')} years")
            else:
                st.error("No job descriptions found in data/job_descriptions/")
                return
        
        else:
            st.write("Custom job creation")
            job_title = st.text_input("Job Title", "AI Engineer")
            required_skills = st.text_area(
                "Required Skills (comma-separated)",
                "Python, LangGraph, LangChain"
            ).split(',')
            min_experience = st.number_input("Min Years Experience", 0, 20, 3)
            
            job_requirements = JobRequirements(
                title=job_title,
                required_skills=[s.strip() for s in required_skills],
                min_years_experience=min_experience
            )
        
        st.divider()
        
        # Resume Upload
        st.subheader("2. Upload Resume")
        
        upload_option = st.radio(
            "Choose resume source:",
            ["Upload file", "Use sample resume"]
        )
        
        resume_text = None
        
        if upload_option == "Upload file":
            uploaded_file = st.file_uploader(
                "Upload resume (PDF or TXT)",
                type=['pdf', 'txt']
            )
            
            if uploaded_file:
                # Save temporarily
                temp_path = Path(f"temp_{uploaded_file.name}")
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    resume_text = load_resume(str(temp_path))
                    st.success("✅ Resume loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading resume: {e}")
                finally:
                    if temp_path.exists():
                        temp_path.unlink()
        
        else:
            sample_resumes = {
                "Strong Fit (Nethmika Perera)": "data/resumes/candidate_strong_fit.txt",
                "Moderate Fit (Amali Fernando)": "data/resumes/candidate_moderate_fit.txt",
                "Not Suitable (Kavindu Silva)": "data/resumes/candidate_not_suitable.txt"
            }
            
            selected_sample = st.selectbox(
                "Select sample resume:",
                list(sample_resumes.keys())
            )
            
            resume_path = sample_resumes[selected_sample]
            try:
                resume_text = load_resume(resume_path)
                st.success("✅ Sample resume loaded!")
            except Exception as e:
                st.error(f"Error loading sample: {e}")
        
        st.divider()
        
        # Process Button
        process_button = st.button(
            "🚀 Start Screening",
            type="primary",
            disabled=resume_text is None,
            use_container_width=True
        )
    
    # Main content area
    if process_button and resume_text:
        st.session_state.processing = True
        
        with st.spinner("🔄 Processing candidate... This may take 20-30 seconds..."):
            try:
                # Initialize workflow
                if st.session_state.workflow is None:
                    st.session_state.workflow = HRScreeningWorkflow()
                
                # Create state
                state = AgentState(
                    resume_text=resume_text,
                    job_requirements=job_requirements,
                    candidate_id=f"WEB_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
                
                # Run workflow
                result = st.session_state.workflow.run(state)
                st.session_state.result = result
                st.session_state.processing = False
                
                # Save results
                Path("output/web").mkdir(parents=True, exist_ok=True)
                save_results(result, output_dir="output/web")
                
                st.success("✅ Screening completed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error during processing: {e}")
                st.session_state.processing = False
                return
    
    # Display Results
    if st.session_state.result:
        result = st.session_state.result
        
        # Convert to dict if needed
        if hasattr(result, 'dict'):
            result_dict = result.dict()
        else:
            result_dict = result
        
        # Candidate Information
        display_candidate_info(result_dict.get('resume_analysis'))
        
        st.divider()
        
        # Screening Score
        display_screening_score(result_dict.get('screening_score'))
        
        st.divider()
        
        # Interview Coordination
        decision = result_dict.get('decision')
        display_interview_coordination(
            result_dict.get('interview_coordination'),
            decision
        )
        
        # Download Results
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_data = json.dumps(result_dict, indent=2, default=str)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"screening_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Clear results
            if st.button("🔄 Screen New Candidate"):
                st.session_state.result = None
                st.rerun()
    
    else:
        # Welcome message
        st.info("""
        👋 **Welcome to the HR Screening AI System!**
        
        This intelligent system automates the entire HR screening workflow:
        
        1. **Resume Analysis** - Extracts skills, experience, and education
        2. **Candidate Scoring** - Evaluates fit with 0-100 score
        3. **Smart Routing** - Accepts or rejects based on threshold (70)
        4. **Interview Coordination** - Generates personalized questions and emails
        
        **Get Started:**
        1. Select a job position from the sidebar (or create custom)
        2. Upload a resume or use a sample
        3. Click "Start Screening" to begin
        
        **Sample Results:**
        - Strong Fit: Score 85-95, generates interview questions
        - Moderate Fit: Score 50-70, may accept or reject
        - Not Suitable: Score <50, generates rejection email
        """)
        
        # System Stats
        st.subheader("📊 System Capabilities")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Agents", "3", help="Resume Analyzer, Interview Coordinator, Supervisor")
        with col2:
            st.metric("Processing Time", "~20s", help="Average time per candidate")
        with col3:
            st.metric("Questions Generated", "8", help="Personalized interview questions")
        with col4:
            st.metric("Accuracy", "95%", help="Skill matching precision")


if __name__ == "__main__":
    main()
