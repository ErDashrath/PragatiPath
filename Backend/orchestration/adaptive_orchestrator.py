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
from assessment.improved_models import Subject, Chapter, SUBJECT_CHOICES

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
    
    # Current session - using real DB subjects and chapters
    subject_code: str = ""  # From SUBJECT_CHOICES in DB
    chapter_id: Optional[int] = None  # Actual Chapter ID from DB
    subject_obj: Optional['Subject'] = None  # Subject model instance (use string for forward ref)
    chapter_obj: Optional['Chapter'] = None  # Chapter model instance (use string for forward ref)
    skill_id: str = ""  # Maps to subject_code + chapter context
    difficulty_level: str = "moderate"  # From DIFFICULTY_CHOICES
    
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
        """Initialize the adaptive learning session with real DB subjects"""
        try:
            logger.info(f"🚀 Initializing adaptive session for student: {state.student_id}")
            
            # Get user object
            try:
                user = User.objects.get(id=int(state.student_id))
                state.user = user
            except User.DoesNotExist:
                # Try getting by StudentProfile
                student_profile = StudentProfile.objects.get(id=state.student_id)
                state.user = student_profile.user
            
            # Initialize tracking data
            state.iteration_count = 0
            state.session_complete = False
            
            # Get real subject from database
            if state.subject_code:
                try:
                    state.subject_obj = Subject.objects.get(code=state.subject_code, is_active=True)
                    logger.info(f"✅ Found subject: {state.subject_obj.name} ({state.subject_code})")
                except Subject.DoesNotExist:
                    logger.warning(f"⚠️ Subject {state.subject_code} not found, using default")
                    # Use first available subject
                    state.subject_obj = Subject.objects.filter(is_active=True).first()
                    if state.subject_obj:
                        state.subject_code = state.subject_obj.code
            else:
                # Default to first available subject
                state.subject_obj = Subject.objects.filter(is_active=True).first()
                if state.subject_obj:
                    state.subject_code = state.subject_obj.code
                else:
                    raise Exception("No active subjects found in database")
            
            # Get chapter if specified
            if state.chapter_id and state.subject_obj:
                try:
                    state.chapter_obj = Chapter.objects.get(
                        id=state.chapter_id, 
                        subject=state.subject_obj,
                        is_active=True
                    )
                    logger.info(f"✅ Found chapter: {state.chapter_obj.name}")
                except Chapter.DoesNotExist:
                    logger.warning(f"⚠️ Chapter {state.chapter_id} not found, using first chapter")
                    state.chapter_obj = state.subject_obj.chapters.filter(is_active=True).first()
                    if state.chapter_obj:
                        state.chapter_id = state.chapter_obj.id
            else:
                # Default to first chapter of subject
                if state.subject_obj:
                    state.chapter_obj = state.subject_obj.chapters.filter(is_active=True).first()
                    if state.chapter_obj:
                        state.chapter_id = state.chapter_obj.id
            
            # Set skill_id based on real subject and chapter
            if state.chapter_obj:
                state.skill_id = f"{state.subject_code}_chapter_{state.chapter_obj.chapter_number}"
            else:
                state.skill_id = f"{state.subject_code}_general"
            
            logger.info(f"✅ Session initialized - Subject: {state.subject_obj.name if state.subject_obj else 'None'}, Chapter: {state.chapter_obj.name if state.chapter_obj else 'None'}, Skill: {state.skill_id}")
            
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
        """Select optimal question based on knowledge analysis from real DB"""
        try:
            logger.info(f"🎯 Selecting adaptive question for iteration {state.iteration_count + 1}")
            
            # Determine optimal difficulty based on BKT/DKT analysis
            bkt_mastery = state.bkt_state.get('mastery_probability', 0.5)
            dkt_prediction = state.dkt_state.get('predictions', {}).get(state.skill_id, 0.5)
            
            # Combine BKT and DKT insights (weighted average)
            combined_mastery = (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
            # Adaptive difficulty selection using real DB difficulty choices
            if combined_mastery < 0.3:
                target_difficulty = "easy"
            elif combined_mastery < 0.6:
                target_difficulty = "moderate"
            elif combined_mastery < 0.8:
                target_difficulty = "difficult"
            else:
                target_difficulty = "difficult"  # Keep challenging for high mastery
            
            state.difficulty_level = target_difficulty
            
            # Real question selection from database using actual subjects and chapters
            if not state.subject_obj:
                logger.error("❌ No subject object available for question selection")
                state.error_message = "No subject available for question selection"
                return state
            
            # Query filters
            question_filter = {
                'subject': state.subject_code,  # Use 'subject' field, not 'subject_code'
                'difficulty_level': target_difficulty,  # Use 'difficulty_level' field, not 'difficulty'
                'is_active': True
            }
            
            # If specific chapter is selected, filter by chapter
            if state.chapter_obj:
                question_filter['chapter'] = state.chapter_obj
                logger.info(f"🔍 Searching for {target_difficulty} questions in {state.subject_obj.name} - {state.chapter_obj.name}")
            else:
                # Search across all chapters of the subject
                logger.info(f"🔍 Searching for {target_difficulty} questions across all chapters in {state.subject_obj.name}")
            
            # Get questions with the specified criteria
            questions = AdaptiveQuestion.objects.filter(**question_filter).order_by('?')
            
            if questions.exists():
                selected_question = questions.first()
                state.current_question = {
                    "id": str(selected_question.id),
                    "subject_code": state.subject_code,
                    "subject_name": state.subject_obj.name,
                    "chapter_name": selected_question.chapter.name if selected_question.chapter else "General",
                    "chapter_id": selected_question.chapter.id if selected_question.chapter else None,
                    "skill_id": state.skill_id,
                    "difficulty": selected_question.difficulty_level,  # Use difficulty_level field
                    "text": selected_question.question_text,
                    "options": [
                        selected_question.option_a,
                        selected_question.option_b, 
                        selected_question.option_c,
                        selected_question.option_d
                    ],
                    "correct_answer": selected_question.answer,  # Use 'answer' field, not 'correct_answer'
                    "explanation": getattr(selected_question, 'explanation', ''),
                    "tags": selected_question.tags,
                    "topic": selected_question.topic
                }
                logger.info(f"✅ Selected {target_difficulty} question from {state.current_question['subject_name']} - {state.current_question['chapter_name']}")
            else:
                # Fallback: try with any difficulty in the subject/chapter
                logger.warning(f"⚠️ No {target_difficulty} questions found, trying any difficulty...")
                fallback_filter = {'subject': state.subject_code, 'is_active': True}  # Fix field name
                if state.chapter_obj:
                    fallback_filter['chapter'] = state.chapter_obj
                    
                questions = AdaptiveQuestion.objects.filter(**fallback_filter).order_by('?')
                
                if questions.exists():
                    selected_question = questions.first()
                    state.current_question = {
                        "id": str(selected_question.id),
                        "subject_code": state.subject_code,
                        "subject_name": state.subject_obj.name,
                        "chapter_name": selected_question.chapter.name if selected_question.chapter else "General",
                        "chapter_id": selected_question.chapter.id if selected_question.chapter else None,
                        "skill_id": state.skill_id,
                        "difficulty": selected_question.difficulty_level,  # Fix field name
                        "text": selected_question.question_text,
                        "options": [
                            selected_question.option_a,
                            selected_question.option_b,
                            selected_question.option_c, 
                            selected_question.option_d
                        ],
                        "correct_answer": selected_question.answer,  # Fix field name
                        "explanation": getattr(selected_question, 'explanation', ''),
                        "tags": selected_question.tags,
                        "topic": selected_question.topic
                    }
                    logger.info(f"✅ Selected fallback question: {selected_question.difficulty_level} from {state.current_question['subject_name']} - {state.current_question['chapter_name']}")
                else:
                    logger.error(f"❌ No questions found for subject {state.subject_code}")
                    state.error_message = f"No questions available for {state.subject_obj.name}"
                    state.session_complete = True
            
            logger.info(f"🎲 Selected {state.difficulty_level} question (combined mastery: {combined_mastery:.3f})")
            
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
                "subject": state.subject_code,  # Fix: use subject_code
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
    
    def run_adaptive_session(self, student_id: str, subject_code: str = None, 
                           chapter_id: int = None, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run a complete adaptive learning session using LangGraph orchestration
        
        Args:
            student_id: ID of the student (User ID)
            subject_code: Subject code from SUBJECT_CHOICES (e.g., 'quantitative_aptitude')
            chapter_id: Optional specific chapter ID from Chapter table
            max_iterations: Maximum number of questions/iterations
            
        Returns:
            Dictionary with session results and analytics
        """
        
        try:
            logger.info(f"🎯 Starting LangGraph adaptive session for student: {student_id}")
            logger.info(f"📚 Subject: {subject_code}, Chapter: {chapter_id}, Max Questions: {max_iterations}")
            
            # Validate subject exists in database
            if subject_code:
                try:
                    subject_obj = Subject.objects.get(code=subject_code, is_active=True)
                    logger.info(f"✅ Valid subject: {subject_obj.name}")
                except Subject.DoesNotExist:
                    logger.error(f"❌ Subject {subject_code} not found in database")
                    available_subjects = list(Subject.objects.filter(is_active=True).values_list('code', 'name'))
                    return {
                        "success": False,
                        "error_message": f"Subject '{subject_code}' not found",
                        "available_subjects": available_subjects
                    }
            
            # Validate chapter exists if provided
            if chapter_id:
                try:
                    chapter_obj = Chapter.objects.get(id=chapter_id, is_active=True)
                    if subject_code and chapter_obj.subject.code != subject_code:
                        return {
                            "success": False,
                            "error_message": f"Chapter {chapter_id} does not belong to subject {subject_code}"
                        }
                    logger.info(f"✅ Valid chapter: {chapter_obj.name} (Chapter {chapter_obj.chapter_number})")
                except Chapter.DoesNotExist:
                    logger.error(f"❌ Chapter {chapter_id} not found")
                    return {
                        "success": False,
                        "error_message": f"Chapter {chapter_id} not found"
                    }
            
            # Initialize state with real database references
            initial_state = AdaptiveLearningState(
                student_id=str(student_id),
                subject_code=subject_code or 'quantitative_aptitude',  # Default to first subject
                chapter_id=chapter_id,
                max_iterations=max_iterations
            )
            
            # Compile and run workflow
            app = self.workflow.compile()
            
            # Execute workflow
            final_state = None
            try:
                for state_dict in app.stream(initial_state):
                    final_state = state_dict
                    logger.debug(f"Workflow state keys: {list(state_dict.keys()) if isinstance(state_dict, dict) else 'Not a dict'}")
                
                # Extract final state - LangGraph returns dict with node names as keys
                if isinstance(final_state, dict):
                    # Get the actual state from the last node in the dict
                    if final_state:
                        # Try to get the state from common final nodes
                        state_obj = None
                        for key in ['finalize_session', 'make_adaptation_decision', 'select_question', 'initialize_session']:
                            if key in final_state:
                                state_obj = final_state[key]
                                break
                        
                        if state_obj is None:
                            # If no known keys, get the last value
                            state_obj = list(final_state.values())[-1]
                        
                        final_state = state_obj
                    else:
                        raise Exception("Empty state returned from workflow")
                
                # Ensure final_state is an AdaptiveLearningState object
                if not hasattr(final_state, 'subject_code'):
                    raise Exception(f"Invalid final state type: {type(final_state)}")
                    
            except Exception as workflow_error:
                logger.error(f"❌ Workflow execution failed: {workflow_error}")
                return {
                    "success": False,
                    "error_message": f"Workflow execution failed: {str(workflow_error)}",
                    "student_id": student_id
                }
            
            # Get chapter statistics for context
            chapter_stats = {}
            if final_state.chapter_obj:
                from django.db.models import Count
                chapter_questions = AdaptiveQuestion.objects.filter(
                    subject=final_state.subject_code,  # Fix field name
                    chapter=final_state.chapter_obj,
                    is_active=True
                )
                
                # Get difficulty distribution for this chapter
                difficulty_counts = chapter_questions.values('difficulty_level').annotate(
                    count=Count('id')
                )
                chapter_stats = {
                    'total_questions': chapter_questions.count(),
                    'difficulty_breakdown': {item['difficulty_level']: item['count'] for item in difficulty_counts},
                    'chapter_name': final_state.chapter_obj.name,
                    'chapter_number': final_state.chapter_obj.chapter_number
                }
            
            # Build result summary with real database context
            result = {
                "success": not bool(final_state.error_message),
                "student_id": student_id,
                "subject": {
                    "code": final_state.subject_code,
                    "name": final_state.subject_obj.name if final_state.subject_obj else "Unknown",
                    "id": final_state.subject_obj.id if final_state.subject_obj else None
                },
                "chapter": {
                    "id": final_state.chapter_id,
                    "name": final_state.chapter_obj.name if final_state.chapter_obj else None,
                    "number": final_state.chapter_obj.chapter_number if final_state.chapter_obj else None,
                    "stats": chapter_stats
                } if final_state.chapter_obj else None,
                "questions_attempted": final_state.iteration_count,
                "final_skill": final_state.skill_id,
                "recommendation": final_state.recommendation,
                "session_complete": final_state.session_complete,
                "bkt_mastery": final_state.bkt_state.get('mastery_probability', 0.5) if final_state.bkt_state else 0.5,
                "dkt_prediction": final_state.dkt_state.get('predictions', {}).get(final_state.skill_id, 0.5) if final_state.dkt_state else 0.5,
                "final_difficulty": final_state.difficulty_level,
                "error_message": final_state.error_message,
                "workflow_metadata": {
                    "max_iterations": max_iterations,
                    "iteration_count": final_state.iteration_count,
                    "mastery_threshold": final_state.mastery_threshold
                }
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