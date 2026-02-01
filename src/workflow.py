"""
LangGraph workflow orchestration for HR screening system.
"""

from typing import Dict, Literal
from langgraph.graph import StateGraph, END

from src.models import AgentState
from src.agents import ResumeAnalyzerAgent, InterviewCoordinatorAgent, DecisionSupervisorAgent
from src.utils import setup_logger

# Optional: IPython for notebook visualization
try:
    from IPython.display import Image, display
except ImportError:
    Image = None
    display = None


logger = setup_logger(__name__)


class HRScreeningWorkflow:
    """LangGraph workflow for automated HR screening."""
    
    def __init__(self):
        """Initialize the workflow with all agents."""
        logger.info("Initializing HR Screening Workflow")
        
        # Initialize agents
        self.resume_analyzer = ResumeAnalyzerAgent()
        self.interview_coordinator = InterviewCoordinatorAgent()
        self.supervisor = DecisionSupervisorAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("HR Screening Workflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        logger.info("Building workflow graph")
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_resume", self._analyze_resume_node)
        workflow.add_node("coordinate_accept", self._coordinate_accept_node)
        workflow.add_node("coordinate_reject", self._coordinate_reject_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define edges
        workflow.set_entry_point("analyze_resume")
        
        # Conditional routing after resume analysis
        workflow.add_conditional_edges(
            "analyze_resume",
            self._route_after_analysis,
            {
                "coordinate_accept": "coordinate_accept",
                "coordinate_reject": "coordinate_reject"
            }
        )
        
        # Both coordination paths lead to finalization
        workflow.add_edge("coordinate_accept", "finalize")
        workflow.add_edge("coordinate_reject", "finalize")
        
        # End after finalization
        workflow.add_edge("finalize", END)
        
        logger.info("Workflow graph built successfully")
        
        return workflow.compile()
    
    def _analyze_resume_node(self, state: AgentState) -> Dict:
        """Node for resume analysis."""
        return self.resume_analyzer.process(state.dict())
    
    def _coordinate_accept_node(self, state: AgentState) -> Dict:
        """Node for coordinating accepted candidates."""
        return self.interview_coordinator.process_qualified(state.dict())
    
    def _coordinate_reject_node(self, state: AgentState) -> Dict:
        """Node for coordinating rejected candidates."""
        return self.interview_coordinator.process_rejected(state.dict())
    
    def _finalize_node(self, state: AgentState) -> Dict:
        """Final node for logging and cleanup."""
        self.supervisor.log_decision_summary(state.dict())
        return {"current_step": "completed"}
    
    def _route_after_analysis(
        self, 
        state: AgentState
    ) -> Literal["coordinate_accept", "coordinate_reject"]:
        """Routing function after resume analysis."""
        return self.supervisor.route_after_screening(state.dict())
    
    def run(self, state: AgentState) -> AgentState:
        """
        Execute the workflow.
        
        Args:
            state: Initial agent state
            
        Returns:
            Final agent state
        """
        logger.info("\n" + "="*60)
        logger.info("STARTING HR SCREENING WORKFLOW")
        logger.info("="*60 + "\n")
        
        try:
            # Run the workflow
            final_state = self.workflow.invoke(state)
            
            logger.info("\n" + "="*60)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("="*60 + "\n")
            
            return AgentState(**final_state)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            error_state = state.dict()
            error_state["error"] = str(e)
            error_state["current_step"] = "failed"
            return AgentState(**error_state)
    
    def visualize(self, output_path: str = "workflow_diagram.png") -> None:
        """
        Visualize the workflow graph.
        
        Args:
            output_path: Path to save the diagram
        """
        try:
            # Get the graph visualization
            graph_image = self.workflow.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)
            
            logger.info(f"Workflow diagram saved to: {output_path}")
            
            # Try to display if in notebook environment
            if display is not None and Image is not None:
                try:
                    display(Image(graph_image))
                except:
                    pass
                
        except Exception as e:
            logger.warning(f"Could not generate workflow visualization: {e}")
    
    def get_workflow_description(self) -> str:
        """Get a textual description of the workflow."""
        return """
HR Screening Workflow:

1. START
   ↓
2. ANALYZE RESUME (Resume Analyzer Agent)
   - Extract candidate information
   - Parse skills, experience, education
   - Score candidate against job requirements
   - Classify as Strong/Moderate/Not Suitable
   ↓
3. ROUTING DECISION (Decision Supervisor)
   - If score >= 70: Route to ACCEPT path
   - If score < 70: Route to REJECT path
   ↓
4a. COORDINATE ACCEPT (Interview Coordinator - Qualified)
    - Generate personalized interview questions
    - Create interview invitation email
    - Propose interview time slots
    - Suggest appropriate interviewers
    ↓
4b. COORDINATE REJECT (Interview Coordinator - Rejected)
    - Generate rejection email with feedback
    - Provide constructive guidance
    ↓
5. FINALIZE (Decision Supervisor)
   - Log decision summary
   - Flag for human review if needed
   ↓
6. END

Error Handling:
- Automatic retries (3 attempts) for API failures
- Graceful fallbacks for parsing errors
- Comprehensive logging at each step
- Error state capture and reporting
"""
