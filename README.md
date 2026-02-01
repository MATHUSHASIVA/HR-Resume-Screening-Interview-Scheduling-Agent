# HR Resume Screening & Interview Scheduling Agent

An intelligent, automated HR screening system built with **LangGraph** that streamlines resume analysis, candidate evaluation, and interview coordination using agentic AI workflows.

![HR Resume Screening AI System](Images/HR%20Resume%20Screening%20AI%20System.jpeg)

---

## 🎯 Overview

This system automates the entire HR screening workflow from resume parsing to interview scheduling using a **multi-agent architecture** powered by LangGraph. It processes resumes, evaluates candidates against job requirements, and generates personalized interview materials or rejection emails with constructive feedback.


### Key Features

✅ **Multi-Agent Architecture**: Three specialized agents working in orchestrated workflow  
✅ **Intelligent Resume Parsing**: Extract skills, experience, education with high accuracy  
✅ **Smart Candidate Scoring**: 0-100 scoring system with detailed reasoning  
✅ **Automated Interview Coordination**: Generate questions, emails, and time slots  
✅ **Production-Ready**: Error handling, retry logic, structured logging  
✅ **Configurable**: Customizable scoring weights, thresholds, and interview slots  
✅ **Multi-Job Support**: Handle different roles with specific requirements  
✅ **Web Interface**: Interactive Streamlit app with visual results

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HR SCREENING WORKFLOW                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     START     │
                    └───────┬───────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │  AGENT 1: Resume Analyzer     │
            │  • Extract candidate info     │
            │  • Parse skills & experience  │
            │  • Score against requirements │
            │  • Classify fit level         │
            └───────────┬───────────────────┘
                        │
                        ▼
            ┌───────────────────────────────┐
            │  AGENT 3: Decision Supervisor │
            │  • Evaluate score (>= 70?)    │
            │  • Route to accept/reject     │
            └─────┬──────────────────┬──────┘
                  │                  │
         Score >= 70            Score < 70
                  │                  │
                  ▼                  ▼
    ┌─────────────────────┐  ┌────────────────────┐
    │ AGENT 2: Interview  │  │  AGENT 2: Interview│
    │ Coordinator (Accept)│  │ Coordinator (Reject)│
    │ • Gen. questions    │  │ • Gen. rejection   │
    │ • Create invitation │  │   email w/ feedback│
    │ • Propose slots     │  │                    │
    │ • Suggest reviewers │  │                    │
    └─────────┬───────────┘  └─────────┬──────────┘
              │                        │
              └────────┬───────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │  FINALIZE        │
            │  • Log summary   │
            │  • Save results  │
            └────────┬─────────┘
                     │
                     ▼
                  ┌─────┐
                  │ END │
                  └─────┘
```

### Agent Responsibilities

| Agent                      | Role                     | Key Functions                                             |
|----------------------------|--------------------------|-----------------------------------------------------------|
| **Resume Analyzer**        | Parse & evaluate resumes | Extract info, calculate skill match, generate 0-100 score |
| **Interview Coordinator**  |  Manage interviews       | Create questions, draft emails, schedule slots            |
| **Decision Supervisor**    | Orchestrate workflow     | Route decisions, flag edge cases, log outcomes            |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Groq API key 

### Installation

1. **Navigate to project directory**
```bash
cd ZeloraTech
```

2. **Activate virtual environment** 
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Verify environment setup**
```bash
# Environment file (.env) is already configured with:
# GROQ_API_KEY=your_api_key
# LLM_MODEL=llama-3.3-70b-versatile
```

### Run the System

**Option 1: Web Interface (Streamlit App)** 
```bash
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

**Option 2: Single Candidate Processing**
```bash
python main.py
```

**Option 3: Demo Mode**
```bash
python demo.py
```

**Option 4: View Booked Interview Slots**
```bash
python src/view_bookings.py
```

**Option 5: Manage Bookings (view, cancel, clear)**
```bash
python src/manage_bookings.py
```

---

## 📅 Interview Booking Management

The system now includes intelligent booking management with business rules:

### Scheduling Rules & Constraints
- **Business Hours Only**: 10:00 AM - 12:00 PM OR 2:00 PM - 5:00 PM
- **Weekdays Only**: Monday through Friday (weekends automatically skipped)
- **Holiday Checking**: Skips company holidays and public holidays
- **Conflict Prevention**: Checks existing bookings before proposing slots

### Automatic Booking Check
- **Smart Scheduling**: System finds available time slots within business hours
- **Holiday-Aware**: Automatically skips configured company holidays
- **Conflict Prevention**: Interview slots checked against existing bookings
- **Auto-Booking**: First available slot is automatically booked for qualified candidates

![Interview Slots](Images/Interview%20Slots.jpeg)

---

## 📊 State Management with LangGraph

LangGraph manages workflow state using Pydantic models:

```python
AgentState:
├── Input
│   ├── resume_text: str
│   └── job_requirements: JobRequirements
│
├── Processing
│   ├── resume_analysis: ResumeAnalysis
│   ├── screening_score: ScreeningScore
│   └── interview_coordination: InterviewCoordination
│
└── Control
    ├── current_step: str
    ├── decision: "accept" | "reject" | "review"
    └── error: Optional[str]
```
## 📂 Project Structure

```
ZeloraTech/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── resume_analyzer.py      # Agent 1: Resume parsing & scoring
│   │   ├── interview_coordinator.py # Agent 2: Interview management
│   │   └── supervisor.py            # Agent 3: Workflow orchestration
│   ├── models.py                    # Pydantic data models
│   ├── config.py                    # Configuration & constants
│   ├── utils.py                     # Utilities (logging, PDF parsing)
│   └── workflow.py                  # LangGraph workflow definition
├── data/
│   ├── job_descriptions/
│   │   ├── ai_engineer.json         # AI Engineer role requirements
│   │   └── backend_engineer.json    # Backend Engineer role
│   └── resumes/
│       ├── candidate_strong_fit.txt # High-scoring candidate (Nethmika Perera)
│       ├── candidate_moderate_fit.txt # Borderline candidate (Amali Fernando)
│       └── candidate_not_suitable.txt # Low-scoring candidate (Kavindu Silva)
├── output/                          # Generated results (JSON)
├── tests/                           # Unit tests
├── main.py                          # Main entry point
├── demo.py                          # Interactive demo
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables
└── README.md                        # This file
```
---

## 💡 Usage Examples
## Example 1: Strong Fit Candidate (Nethmika Perera)

### Input
**Job Requirements:**
```json
{
  "title": "AI Engineer",
  "required_skills": ["Python", "LangGraph", "LangChain", "OpenAI API", "RAG Systems"],
  "min_years_experience": 3,
  "education_requirements": ["Bachelor's in CS or related field"]
}
```

**Resume:** `data/resumes/candidate_strong_fit.txt`
- Name: Nethmika Perera
- Experience: 4+ years in AI/ML
- Skills: LangGraph, LangChain, RAG, Multi-agent systems
- Education: MS in AI from Stanford

### Execution

```bash
python main.py
```

### Output

![Strong Fit Example 1](Images/Strong%20Fit.jpeg)

![Strong Fit Example 2](Images/Strong%20Fit%202.jpeg)

```
====================================================================
HR SCREENING RESULTS
====================================================================

📋 CANDIDATE INFORMATION
   Name: Nethmika Perera
   Email: nethmika.p@email.com
   Phone: +94 77 456 7890
   Location: Colombo, Sri Lanka

🎯 SCREENING EVALUATION
   Score: 88/100
   Classification: Strong Fit
   Skill Match: 95.0%

   Reasoning: Exceptional candidate with extensive experience in LangGraph
   and agentic AI systems. Demonstrates deep expertise in RAG pipelines,
   multi-agent workflows, and production LLM applications. Strong alignment
   with all required skills and responsibilities.

   ✅ Strengths:
      • Expert-level knowledge of LangGraph and LangChain
      • Proven track record building production RAG systems
      • 4+ years experience exceeds minimum requirements
      • Strong educational background (MS in AI from Stanford)
      • Published research and community contributions

   ⚠️  Gaps:
      • None identified

✅ DECISION: ACCEPT

📅 INTERVIEW COORDINATION

   ![Interview Coordination](Images/Interviiew%20Coordination.jpeg)

   Interview Questions (8 total):
      1. [Technical] Can you walk us through your approach to building
         the multi-agent RAG system you mentioned that serves 50K+ daily
         queries? What were the key architectural decisions?

      2. [Technical] How did you achieve a 40% reduction in LLM API costs?
         What optimization strategies did you implement?

      3. [Experience] Describe your most complex LangGraph workflow. What
         challenges did you face and how did you overcome them?

      4. [Behavioral] Tell us about a time when you had to balance model
         performance with cost efficiency. How did you make trade-offs?

      5. [Behavioral] How do you stay current with rapidly evolving AI
         technologies, particularly in the LangGraph ecosystem?

      6. [Problem-Solving] If tasked with building a new RAG system from
         scratch, what would be your step-by-step approach?

      7. [Experience] You mentioned leading a team of 3 engineers. How do
         you ensure code quality and knowledge sharing in AI projects?

      8. [Technical] What's your approach to prompt engineering for
         production systems? Any specific techniques you've found effective?

   Scheduled Interview Time:
      📅 Monday, February 03, 2026 at 10:00 AM (IST)
      ⏱️  Duration: 1 hour
      🔒 Status: AUTO-BOOKED

   Recommended Interviewers:
      • HR Manager
      • AI Engineering Lead
      • Technical Lead
      • Senior Team Member

📧 EMAIL PREVIEW

   ![Invitation to Interview Email](Images/Invitation%20to%20Interview%20email.jpeg)

   Subject: Interview Invitation - AI Engineer Position at Zelora Tech
   ---
   Dear Nethmika,

   We are thoroughly impressed with your extensive experience in LangGraph,
   multi-agent systems, and production RAG pipelines. Your background aligns
   exceptionally well with our AI Engineer role at Zelora Tech.

   We would love to schedule an interview to discuss your work in more detail,
   particularly your experience building scalable agentic AI systems and your
   approach to optimizing LLM performance.

   We have scheduled your interview for Monday, February 03, 2026 at 10:00 AM (IST).
   The interview will last approximately 1 hour.

   The interview will be conducted with members of our AI Engineering team. 
   We'll discuss your technical experience, review your approach to specific 
   challenges, and answer any questions you have about Zelora Tech and the role.

   Please confirm your availability for this time, and we'll send a calendar
   invitation with video conference details.

   We're excited about the possibility of you joining our team!

   Best regards,
   The Zelora Tech Talent Team
   hr@zeloratech.com

====================================================================

✅ Results saved to: output/nethmika_perera_20260130_143022.json
```

---

## Example 2: Moderate Fit Candidate (Amali Fernando)

![Moderate Fit Sample](Images/Moderate%20Fit%20Sample.jpeg)

Candidates with scores between 50-70 are classified as Moderate Fit and may receive rejection emails with constructive feedback.

---

## Example 3: Rejection Email

![Rejection Email](Images/Rejection%20Email%20.jpeg)

Candidates who don't meet the threshold receive personalized rejection emails with constructive feedback to help them improve.

---

## ⚙️ Configuration

### Scoring Weights (`src/config.py`)

```python
SCORING_WEIGHTS = {
    "skills_match": 0.40,      # 40% - Technical skills alignment
    "experience_years": 0.25,  # 25% - Years of experience
    "education": 0.15,         # 15% - Educational background
    "relevance": 0.20,         # 20% - Overall domain relevance
}
```

### Thresholds

```python
QUALIFIED_CANDIDATE_THRESHOLD = 70  # Minimum score for interview
STRONG_FIT_THRESHOLD = 75           # Strong fit classification
MODERATE_FIT_THRESHOLD = 50         # Moderate fit classification
```

### Retry & Error Handling

```python
MAX_RETRIES = 3         # API call retries
RETRY_DELAY = 2         # Seconds between retries
```
---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=src tests/
```

### Manual Testing

Test with provided sample resumes:
```bash
# Test strong fit
python main.py

# Test all candidates
python demo.py
```
---

## 📝 Design Decisions & Trade-offs

### 1. **LangGraph for Orchestration**
- ✅ **Pros**: Clear state management, easy visualization, production-ready
- ⚠️ **Cons**: Learning curve, overkill for simple workflows
- **Decision**: Chosen for scalability and maintainability

### 2. **Groq + Llama 3.3 70B**
- ✅ **Pros**: Fast inference, cost-effective, strong reasoning
- ⚠️ **Cons**: Rate limits, less flexible than OpenAI
- **Decision**: Optimal balance of speed and quality

### 3. **Pydantic for Validation**
- ✅ **Pros**: Type safety, automatic validation, great LLM integration
- ⚠️ **Cons**: Slightly verbose
- **Decision**: Essential for structured outputs

### 4. **Threshold-Based Routing**
- ✅ **Pros**: Simple, transparent, configurable
- ⚠️ **Cons**: No ML-based decision making
- **Decision**: Sufficient for initial version, easy to upgrade
---

## 🚀 Future Enhancements

### Planned Features

- [ ] **Persistence**: Database integration for candidate history
- [ ] **Analytics Dashboard**: Screening metrics and insights
- [ ] **Multi-Language Support**: Process resumes in different languages
- [ ] **Resume Ranking**: Batch processing with comparative ranking
- [ ] **Integration**: ATS (Applicant Tracking System) connectors
- [ ] **Advanced Parsing**: Computer vision for complex resume formats

---