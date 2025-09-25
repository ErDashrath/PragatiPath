"""
LangGraph Orchestration for Adaptive Learning System

This module orchestrates BKT and DKT services using LangGraph to provide
intelligent adaptive learning workflows with real-time decision making.
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
import logging
from dataclasses import dataclass
from datetime import datetime
import json

from django.contrib.auth.models import User
from core.models import StudentProfile
from student_model.bkt import BKTService
from student_model.dkt import DKTService
from assessment.models import AdaptiveQuestion, QuestionAttempt

logger = logging.getLogger(__name__)

# ============================================================================
# State Definitions
# ============================================================================

@dataclass
class AdaptiveLearningState:
    """State object for the adaptive learning workflow"""
    # Student context
    student_id: str
    user: Optional[User] = None
    
    # Current session
    subject: str = ""
    skill_id: str = ""
    difficulty_level: str = "medium"
    
    # Question selection
    current_question: Optional[Dict[str, Any]] = None
    question_pool: List[Dict[str, Any]] = None
    
    # Student response
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time: Optional[float] = None
    interaction_data: Dict[str, Any] = None
    
    # Knowledge tracking
    bkt_state: Dict[str, Any] = None
    dkt_state: Dict[str, Any] = None
    mastery_threshold: float = 0.8
    
    # Adaptation decisions
    next_difficulty: str = ""
    next_skill: str = ""
    recommendation: str = ""
    
    # Workflow control
    session_complete: bool = False
    error_message: str = ""
    iteration_count: int = 0
    max_iterations: int = 20

    def __post_init__(self):
        if self.interaction_data is None:
            self.interaction_data = {}
        if self.question_pool is None:
            self.question_pool = []

# ============================================================================
# LangGraph Nodes
# ============================================================================

class AdaptiveLearningOrchestrator:
    """LangGraph orchestrator for adaptive learning workflow"""
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for adaptive learning"""
        
        workflow = StateGraph(AdaptiveLearningState)
        
        # Add nodes
        workflow.add_node("initialize_session", self.initialize_session)
        workflow.add_node("analyze_knowledge_state", self.analyze_knowledge_state)
        workflow.add_node("select_question", self.select_question)
        workflow.add_node("process_response", self.process_response)
        workflow.add_node("update_knowledge", self.update_knowledge)
        workflow.add_node("make_adaptation_decision", self.make_adaptation_decision)
        workflow.add_node("finalize_session", self.finalize_session)
        
        # Define workflow edges
        workflow.set_entry_point("initialize_session")
        
        workflow.add_edge("initialize_session", "analyze_knowledge_state")
        workflow.add_edge("analyze_knowledge_state", "select_question")
        
        # Conditional edge after question selection
        workflow.add_conditional_edges(
            "select_question",
            self.should_continue_session,
            {
                "continue": "process_response",
                "end": END
            }
        )
        
        workflow.add_edge("process_response", "update_knowledge")
        workflow.add_edge("update_knowledge", "make_adaptation_decision")
        
        # Conditional edge for next iteration or end
        workflow.add_conditional_edges(
            "make_adaptation_decision", 
            self.should_continue_session,
            {
                "continue": "analyze_knowledge_state",
                "end": "finalize_session"
            }
        )
        
        workflow.add_edge("finalize_session", END)
        
        return workflow
    
    # ========================================================================
    # Node Implementation Methods
    # ========================================================================
    
    def initialize_session(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Initialize the adaptive learning session"""
        try:
            logger.info(f"🚀 Initializing adaptive session for student: {state.student_id}")
            
            # Get user object
            student_profile = StudentProfile.objects.get(id=state.student_id)
            state.user = student_profile.user
            
            # Initialize tracking data
            state.iteration_count = 0
            state.session_complete = False
            
            # Set default subject if not provided
            if not state.subject:
                state.subject = "mathematics"
            
            # Set default skill if not provided  
            if not state.skill_id:
                state.skill_id = f"{state.subject}_basic"
            
            logger.info(f"✅ Session initialized - Subject: {state.subject}, Skill: {state.skill_id}")
            
        except Exception as e:
            logger.error(f"❌ Session initialization failed: {e}")
            state.error_message = f"Initialization failed: {str(e)}"
        
        return state
    
    def analyze_knowledge_state(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Analyze current knowledge state using both BKT and DKT"""
        try:
            logger.info(f"🧠 Analyzing knowledge state for skill: {state.skill_id}")
            
            # Get BKT analysis
            bkt_params = self.bkt_service.get_skill_bkt_params(state.user, state.skill_id)
            state.bkt_state = {"mastery_probability": bkt_params.P_L}
            
            # Get DKT analysis  
            dkt_prediction = self.dkt_service.get_skill_prediction(state.user, state.skill_id)
            state.dkt_state = {"predictions": {state.skill_id: dkt_prediction}}
            
            # Log analysis results
            bkt_mastery = state.bkt_state.get('mastery_probability', 0.5)
            dkt_prediction = state.dkt_state.get('predictions', {}).get(state.skill_id, 0.5)
            
            logger.info(f"📊 BKT Mastery: {bkt_mastery:.3f}, DKT Prediction: {dkt_prediction:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Knowledge analysis failed: {e}")
            state.error_message = f"Knowledge analysis failed: {str(e)}"
        
        return state
    
    def select_question(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Select optimal question based on knowledge analysis"""
        try:
            logger.info(f"🎯 Selecting adaptive question for iteration {state.iteration_count + 1}")
            
            # Determine optimal difficulty based on BKT/DKT analysis
            bkt_mastery = state.bkt_state.get('mastery_probability', 0.5)
            dkt_prediction = state.dkt_state.get('predictions', {}).get(state.skill_id, 0.5)
            
            # Combine BKT and DKT insights (weighted average)
            combined_mastery = (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
            # Adaptive difficulty selection
            if combined_mastery < 0.3:
                target_difficulty = "easy"
            elif combined_mastery < 0.7:
                target_difficulty = "medium" 
            else:
                target_difficulty = "hard"
            
            state.difficulty_level = target_difficulty
            
            # Mock question selection (in real system, query from database)
            state.current_question = {
                "id": f"q_{state.iteration_count + 1}_{target_difficulty}",
                "subject": state.subject,
                "skill_id": state.skill_id,
                "difficulty": target_difficulty,
                "text": f"Adaptive {target_difficulty} question for {state.skill_id}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            }
            
            logger.info(f"🎲 Selected {target_difficulty} question (combined mastery: {combined_mastery:.3f})")
            
        except Exception as e:
            logger.error(f"❌ Question selection failed: {e}")
            state.error_message = f"Question selection failed: {str(e)}"
        
        return state
    
    def process_response(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Process student response (this would be called after student answers)"""
        try:
            logger.info(f"📝 Processing student response for question {state.current_question['id']}")
            
            # In real implementation, this data comes from frontend
            # For demo, we'll simulate based on difficulty and mastery
            if state.student_answer is None:
                # Simulate student performance based on current mastery
                bkt_mastery = state.bkt_state.get('mastery_probability', 0.5)
                difficulty = state.current_question['difficulty']
                
                # Adjust success probability based on difficulty
                success_prob = bkt_mastery
                if difficulty == "easy":
                    success_prob += 0.2
                elif difficulty == "hard":
                    success_prob -= 0.2
                
                success_prob = max(0.1, min(0.9, success_prob))  # Clamp between 0.1-0.9
                
                # Simulate response
                import random
                state.is_correct = random.random() < success_prob
                state.student_answer = "A" if state.is_correct else "B"
                state.response_time = random.uniform(10, 60)
            
            # Update interaction data
            state.interaction_data.update({
                "question_id": state.current_question['id'],
                "difficulty": state.current_question['difficulty'],
                "response_time": state.response_time,
                "timestamp": datetime.now().isoformat()
            })
            
            result = "✅ Correct" if state.is_correct else "❌ Incorrect"
            logger.info(f"📊 Response processed: {result} in {state.response_time:.1f}s")
            
        except Exception as e:
            logger.error(f"❌ Response processing failed: {e}")
            state.error_message = f"Response processing failed: {str(e)}"
        
        return state
    
    def update_knowledge(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Update both BKT and DKT knowledge models"""
        try:
            logger.info(f"🔄 Updating knowledge models (BKT + DKT)")
            
            # Update BKT
            try:
                self.bkt_service.update_skill_bkt(
                    user=state.user,
                    skill_id=state.skill_id,
                    is_correct=state.is_correct,
                    interaction_data=state.interaction_data
                )
                logger.info("✅ BKT updated successfully")
            except Exception as bkt_error:
                logger.warning(f"⚠️ BKT update failed: {bkt_error}")
            
            # Update DKT
            try:
                dkt_result = self.dkt_service.update_dkt_knowledge(
                    user=state.user,
                    skill_id=state.skill_id,
                    is_correct=state.is_correct,
                    interaction_data=state.interaction_data
                )
                logger.info("✅ DKT updated successfully")
            except Exception as dkt_error:
                logger.warning(f"⚠️ DKT update failed: {dkt_error}")
            
            # Get updated knowledge states for next iteration
            updated_bkt_params = self.bkt_service.get_skill_bkt_params(state.user, state.skill_id)
            state.bkt_state = {"mastery_probability": updated_bkt_params.P_L}
            updated_dkt_prediction = self.dkt_service.get_skill_prediction(state.user, state.skill_id)
            state.dkt_state = {"predictions": {state.skill_id: updated_dkt_prediction}}
            
        except Exception as e:
            logger.error(f"❌ Knowledge update failed: {e}")
            state.error_message = f"Knowledge update failed: {str(e)}"
        
        return state
    
    def make_adaptation_decision(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Make intelligent adaptation decisions based on updated knowledge"""
        try:
            logger.info(f"🤖 Making adaptation decisions")
            
            # Get current mastery levels
            bkt_mastery = state.bkt_state.get('mastery_probability', 0.5) if state.bkt_state else 0.5
            dkt_prediction = state.dkt_state.get('predictions', {}).get(state.skill_id, 0.5) if state.dkt_state else 0.5
            
            combined_mastery = (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
            # Make adaptation decisions
            if combined_mastery >= state.mastery_threshold:
                # Student has mastered current skill
                state.recommendation = "advance_skill"
                state.next_skill = f"{state.subject}_advanced"
                state.next_difficulty = "medium"
                
                # Check if we should end session (mastery achieved)
                if state.iteration_count >= 3:  # Minimum questions per skill
                    state.session_complete = True
                    
            elif combined_mastery < 0.3:
                # Student struggling, provide easier content
                state.recommendation = "reinforce_skill"  
                state.next_skill = state.skill_id  # Same skill
                state.next_difficulty = "easy"
                
            else:
                # Continue with current skill, adjust difficulty
                state.recommendation = "continue_skill"
                state.next_skill = state.skill_id
                state.next_difficulty = "medium"
            
            # Update for next iteration
            state.skill_id = state.next_skill
            state.difficulty_level = state.next_difficulty
            state.iteration_count += 1
            
            # Check termination conditions
            if (state.iteration_count >= state.max_iterations or 
                state.recommendation == "advance_skill" and combined_mastery >= 0.9):
                state.session_complete = True
            
            logger.info(f"🎯 Decision: {state.recommendation} (mastery: {combined_mastery:.3f})")
            
        except Exception as e:
            logger.error(f"❌ Adaptation decision failed: {e}")
            state.error_message = f"Adaptation decision failed: {str(e)}"
        
        return state
    
    def finalize_session(self, state: AdaptiveLearningState) -> AdaptiveLearningState:
        """Finalize the adaptive learning session"""
        try:
            logger.info(f"🏁 Finalizing adaptive session")
            
            # Generate session summary
            bkt_mastery = state.bkt_state.get('mastery_probability', 0.5) if state.bkt_state else 0.5
            dkt_prediction = state.dkt_state.get('predictions', {}).get(state.skill_id, 0.5) if state.dkt_state else 0.5
            
            session_summary = {
                "student_id": state.student_id,
                "subject": state.subject,
                "final_skill": state.skill_id,
                "questions_attempted": state.iteration_count,
                "final_bkt_mastery": bkt_mastery,
                "final_dkt_prediction": dkt_prediction,
                "recommendation": state.recommendation,
                "session_complete": True
            }
            
            logger.info(f"📊 Session completed: {state.iteration_count} questions, final mastery: {bkt_mastery:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Session finalization failed: {e}")
            state.error_message = f"Session finalization failed: {str(e)}"
        
        return state
    
    # ========================================================================
    # Conditional Edge Methods  
    # ========================================================================
    
    def should_continue_session(self, state: AdaptiveLearningState) -> str:
        """Determine if session should continue or end"""
        
        # Check for errors
        if state.error_message:
            logger.error(f"🚫 Session ending due to error: {state.error_message}")
            return "end"
        
        # Check completion conditions
        if state.session_complete:
            logger.info(f"✅ Session complete after {state.iteration_count} iterations")
            return "end"
        
        # Check iteration limit
        if state.iteration_count >= state.max_iterations:
            logger.info(f"⏰ Session ending due to iteration limit ({state.max_iterations})")
            return "end"
        
        logger.info(f"🔄 Continuing session (iteration {state.iteration_count}/{state.max_iterations})")
        return "continue"
    
    # ========================================================================
    # Public Interface Methods
    # ========================================================================
    
    def run_adaptive_session(self, student_id: str, subject: str = None, 
                           max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run a complete adaptive learning session using LangGraph orchestration
        
        Args:
            student_id: UUID of the student
            subject: Subject area for the session
            max_iterations: Maximum number of questions/iterations
            
        Returns:
            Dictionary with session results and analytics
        """
        
        try:
            logger.info(f"🎯 Starting LangGraph adaptive session for student: {student_id}")
            
            # Initialize state
            initial_state = AdaptiveLearningState(
                student_id=student_id,
                subject=subject or "mathematics",
                max_iterations=max_iterations
            )
            
            # Compile and run workflow
            app = self.workflow.compile()
            
            # Execute workflow
            final_state = None
            for state in app.stream(initial_state):
                final_state = state
                logger.debug(f"Workflow state: {list(state.keys())}")
            
            # Extract final state
            if isinstance(final_state, dict):
                # Get the last state from the dict
                final_state = list(final_state.values())[-1]
            
            # Build result summary
            result = {
                "success": not bool(final_state.error_message),
                "student_id": student_id,
                "subject": final_state.subject,
                "questions_attempted": final_state.iteration_count,
                "final_skill": final_state.skill_id,
                "recommendation": final_state.recommendation,
                "session_complete": final_state.session_complete,
                "bkt_mastery": final_state.bkt_state.get('mastery_probability', 0.5) if final_state.bkt_state else 0.5,
                "dkt_prediction": final_state.dkt_state.get('predictions', {}).get(final_state.skill_id, 0.5) if final_state.dkt_state else 0.5,
                "error_message": final_state.error_message
            }
            
            logger.info(f"🎉 Adaptive session completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Adaptive session failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "student_id": student_id
            }

# ============================================================================
# Singleton Instance
# ============================================================================

# Create global orchestrator instance
adaptive_orchestrator = AdaptiveLearningOrchestrator()