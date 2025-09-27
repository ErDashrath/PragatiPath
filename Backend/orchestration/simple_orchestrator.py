"""
Simplified Orchestration Without LangGraph

This provides a working adaptive learning orchestration system using the same 
BKT/DKT integration but without the LangGraph complexity.

Author: AI Assistant  
Date: 2024-12-26
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from django.contrib.auth.models import User
from core.models import StudentProfile
from student_model.bkt import BKTService
from student_model.dkt import DKTService
from assessment.models import AdaptiveQuestion
from assessment.improved_models import Subject, Chapter

logger = logging.getLogger(__name__)

class SimpleAdaptiveOrchestrator:
    """
    Simplified orchestrator that provides the same functionality as LangGraph 
    version but with direct method calls instead of workflow orchestration.
    """
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
    
    def run_adaptive_session(
        self,
        student_id: str,
        subject_code: str = 'quantitative_aptitude',
        chapter_id: Optional[int] = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Run a complete adaptive learning session
        
        Args:
            student_id: ID of the student (User ID)
            subject_code: Subject code from SUBJECT_CHOICES
            chapter_id: Optional specific chapter ID  
            max_iterations: Maximum number of questions
            
        Returns:
            Dictionary with session results and analytics
        """
        
        try:
            logger.info(f"🎯 Starting adaptive session for student: {student_id}")
            
            # Initialize session
            session_data = self._initialize_session(
                student_id, subject_code, chapter_id, max_iterations
            )
            
            if not session_data['success']:
                return session_data
            
            # Run question loop
            questions_attempted = 0
            session_log = []
            
            while questions_attempted < max_iterations:
                logger.info(f"📝 Question {questions_attempted + 1}/{max_iterations}")
                
                # Analyze knowledge state
                knowledge_analysis = self._analyze_knowledge(session_data)
                
                # Select question based on analysis
                question_result = self._select_question(session_data, knowledge_analysis)
                
                if not question_result['success']:
                    break
                
                # Log this iteration
                iteration_log = {
                    'iteration': questions_attempted + 1,
                    'question_id': question_result['question']['id'],
                    'question_difficulty': question_result['question']['difficulty'],
                    'question_chapter': question_result['question']['chapter_name'],
                    'bkt_mastery': knowledge_analysis['bkt_mastery'],
                    'dkt_prediction': knowledge_analysis['dkt_prediction'],
                    'combined_mastery': knowledge_analysis['combined_mastery']
                }
                
                session_log.append(iteration_log)
                
                # Simulate answer for demo (in real app, this comes from frontend)
                simulated_answer = self._simulate_answer(
                    question_result['question'], knowledge_analysis['combined_mastery']
                )
                
                # Process answer and update knowledge
                self._update_knowledge(
                    session_data, 
                    question_result['question'], 
                    simulated_answer
                )
                
                questions_attempted += 1
                
                # Check if mastery achieved
                if knowledge_analysis['combined_mastery'] > 0.9:
                    logger.info("🎉 High mastery achieved, ending session")
                    break
            
            # Generate final results
            return self._generate_session_results(
                session_data, questions_attempted, session_log
            )
            
        except Exception as e:
            logger.error(f"❌ Adaptive session failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "student_id": student_id
            }
    
    def _initialize_session(
        self, student_id: str, subject_code: str, 
        chapter_id: Optional[int], max_iterations: int
    ) -> Dict[str, Any]:
        """Initialize the session with database validation"""
        
        try:
            # Get and validate user
            user = User.objects.get(id=int(student_id))
            
            # Ensure user has StudentProfile
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bkt_parameters': {},
                    'dkt_hidden_state': [],
                    'fundamentals': {
                        'listening': 0.5, 'grasping': 0.5, 
                        'retention': 0.5, 'application': 0.5
                    },
                    'interaction_history': []
                }
            )
            
            # Get and validate subject
            subject_obj = Subject.objects.get(code=subject_code, is_active=True)
            
            # Get and validate chapter if specified
            chapter_obj = None
            if chapter_id:
                chapter_obj = Chapter.objects.get(
                    id=chapter_id, 
                    subject=subject_obj, 
                    is_active=True
                )
            else:
                # Default to first chapter
                chapter_obj = subject_obj.chapters.filter(is_active=True).first()
            
            # Create skill ID
            skill_id = f"{subject_code}_chapter_{chapter_obj.chapter_number}" if chapter_obj else f"{subject_code}_general"
            
            return {
                'success': True,
                'user': user,
                'subject_obj': subject_obj,
                'chapter_obj': chapter_obj,
                'skill_id': skill_id,
                'max_iterations': max_iterations,
                'mastery_threshold': 0.8
            }
            
        except Exception as e:
            logger.error(f"❌ Session initialization failed: {e}")
            return {
                'success': False,
                'error_message': f"Initialization failed: {str(e)}"
            }
    
    def _analyze_knowledge(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current knowledge state using BKT and DKT"""
        
        try:
            user = session_data['user']
            skill_id = session_data['skill_id']
            
            # Get BKT analysis
            bkt_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            bkt_mastery = bkt_params.P_L
            
            # Get DKT analysis
            dkt_state = self.dkt_service.get_dkt_state(user)
            
            # Handle DKT predictions safely
            if hasattr(dkt_state, 'skill_predictions') and isinstance(dkt_state.skill_predictions, dict):
                dkt_prediction = dkt_state.skill_predictions.get(skill_id, 0.5)
            else:
                # Fallback if skill_predictions is not available or not a dict
                dkt_prediction = 0.5
            
            # Combine BKT and DKT insights (weighted average)
            combined_mastery = (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
            return {
                'bkt_mastery': bkt_mastery,
                'dkt_prediction': dkt_prediction,
                'combined_mastery': combined_mastery,
                'bkt_params': bkt_params,
                'dkt_state': dkt_state
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge analysis failed: {e}")
            return {
                'bkt_mastery': 0.5,
                'dkt_prediction': 0.5,
                'combined_mastery': 0.5,
                'error': str(e)
            }
    
    def _select_question(
        self, session_data: Dict[str, Any], 
        knowledge_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select optimal question based on knowledge analysis"""
        
        try:
            subject_obj = session_data['subject_obj']
            chapter_obj = session_data['chapter_obj']
            combined_mastery = knowledge_analysis['combined_mastery']
            
            # Determine difficulty based on mastery
            if combined_mastery < 0.3:
                target_difficulty = "easy"
            elif combined_mastery < 0.6:
                target_difficulty = "moderate"
            else:
                target_difficulty = "difficult"
            
            # Query filters
            question_filter = {
                'subject': subject_obj.code,
                'difficulty_level': target_difficulty,
                'is_active': True
            }
            
            if chapter_obj:
                question_filter['chapter'] = chapter_obj
            
            # Get questions
            questions = AdaptiveQuestion.objects.filter(**question_filter).order_by('?')
            
            if questions.exists():
                selected_question = questions.first()
                
                question_data = {
                    'id': str(selected_question.id),
                    'subject_code': subject_obj.code,
                    'subject_name': subject_obj.name,
                    'chapter_name': selected_question.chapter.name if selected_question.chapter else "General",
                    'chapter_id': selected_question.chapter.id if selected_question.chapter else None,
                    'difficulty': selected_question.difficulty_level,
                    'text': selected_question.question_text,
                    'options': [
                        selected_question.option_a,
                        selected_question.option_b,
                        selected_question.option_c,
                        selected_question.option_d
                    ],
                    'correct_answer': selected_question.answer,
                    'tags': selected_question.tags,
                    'topic': selected_question.topic
                }
                
                return {
                    'success': True,
                    'question': question_data,
                    'target_difficulty': target_difficulty
                }
            else:
                # Fallback to any difficulty
                fallback_filter = {'subject': subject_obj.code, 'is_active': True}
                if chapter_obj:
                    fallback_filter['chapter'] = chapter_obj
                
                questions = AdaptiveQuestion.objects.filter(**fallback_filter).order_by('?')
                
                if questions.exists():
                    selected_question = questions.first()
                    question_data = {
                        'id': str(selected_question.id),
                        'subject_code': subject_obj.code,
                        'subject_name': subject_obj.name,
                        'chapter_name': selected_question.chapter.name if selected_question.chapter else "General",
                        'difficulty': selected_question.difficulty_level,
                        'text': selected_question.question_text,
                        'options': [selected_question.option_a, selected_question.option_b, selected_question.option_c, selected_question.option_d],
                        'correct_answer': selected_question.answer
                    }
                    
                    return {'success': True, 'question': question_data, 'fallback': True}
                else:
                    return {
                        'success': False,
                        'error_message': f"No questions found for {subject_obj.name}"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Question selection failed: {e}")
            return {
                'success': False,
                'error_message': f"Question selection failed: {str(e)}"
            }
    
    def _simulate_answer(self, question: Dict[str, Any], mastery_level: float) -> Dict[str, Any]:
        """Simulate student answer based on mastery (for demo purposes)"""
        
        import random
        
        # Higher mastery = higher chance of correct answer
        is_correct = random.random() < (0.3 + (mastery_level * 0.7))
        
        if is_correct:
            student_answer = question['correct_answer']
        else:
            # Random incorrect answer
            options = ['a', 'b', 'c', 'd']
            options.remove(question['correct_answer'])
            student_answer = random.choice(options)
        
        return {
            'answer': student_answer,
            'is_correct': is_correct,
            'response_time': random.uniform(10.0, 60.0)  # Random response time
        }
    
    def _update_knowledge(
        self, session_data: Dict[str, Any], 
        question: Dict[str, Any], 
        answer_result: Dict[str, Any]
    ):
        """Update BKT and DKT knowledge models"""
        
        try:
            user = session_data['user']
            skill_id = session_data['skill_id']
            
            interaction_data = {
                'timestamp': datetime.now().isoformat(),
                'question_id': question['id'],
                'response_time': answer_result['response_time']
            }
            
            # Update BKT
            self.bkt_service.update_skill_bkt_with_progression(
                user=user,
                skill_id=skill_id,
                is_correct=answer_result['is_correct'],
                interaction_data=interaction_data
            )
            
            # Update DKT  
            self.dkt_service.update_dkt_knowledge(
                user=user,
                skill_id=skill_id,
                is_correct=answer_result['is_correct'],
                interaction_data=interaction_data
            )
            
            logger.info(f"📊 Updated knowledge models: correct={answer_result['is_correct']}")
            
        except Exception as e:
            logger.error(f"❌ Knowledge update failed: {e}")
    
    def _generate_session_results(
        self, session_data: Dict[str, Any], 
        questions_attempted: int, 
        session_log: list
    ) -> Dict[str, Any]:
        """Generate comprehensive session results"""
        
        try:
            # Get final knowledge analysis
            final_analysis = self._analyze_knowledge(session_data)
            
            # Calculate session statistics
            correct_answers = sum(1 for log in session_log if log.get('simulated_correct', False))
            accuracy = (correct_answers / questions_attempted * 100) if questions_attempted > 0 else 0
            
            # Generate chapter statistics
            chapter_stats = {}
            if session_data.get('chapter_obj'):
                chapter_obj = session_data['chapter_obj']
                from django.db.models import Count
                chapter_questions = AdaptiveQuestion.objects.filter(
                    subject=session_data['subject_obj'].code,
                    chapter=chapter_obj,
                    is_active=True
                )
                
                difficulty_counts = chapter_questions.values('difficulty_level').annotate(
                    count=Count('id')
                )
                chapter_stats = {
                    'total_questions': chapter_questions.count(),
                    'difficulty_breakdown': {item['difficulty_level']: item['count'] for item in difficulty_counts},
                    'chapter_name': chapter_obj.name,
                    'chapter_number': chapter_obj.chapter_number
                }
            
            return {
                "success": True,
                "student_id": session_data['user'].id,
                "subject": {
                    "code": session_data['subject_obj'].code,
                    "name": session_data['subject_obj'].name,
                    "id": session_data['subject_obj'].id
                },
                "chapter": {
                    "id": session_data['chapter_obj'].id if session_data.get('chapter_obj') else None,
                    "name": session_data['chapter_obj'].name if session_data.get('chapter_obj') else None,
                    "number": session_data['chapter_obj'].chapter_number if session_data.get('chapter_obj') else None,
                    "stats": chapter_stats
                } if session_data.get('chapter_obj') else None,
                "questions_attempted": questions_attempted,
                "accuracy_percentage": round(accuracy, 1),
                "final_skill": session_data['skill_id'],
                "bkt_mastery": final_analysis['bkt_mastery'],
                "dkt_prediction": final_analysis['dkt_prediction'],
                "combined_mastery": final_analysis['combined_mastery'],
                "session_log": session_log,
                "recommendation": self._generate_recommendation(final_analysis),
                "session_complete": True,
                "orchestration_method": "simplified_direct"
            }
            
        except Exception as e:
            logger.error(f"❌ Results generation failed: {e}")
            return {
                "success": False,
                "error_message": f"Results generation failed: {str(e)}"
            }
    
    def _generate_recommendation(self, knowledge_analysis: Dict[str, Any]) -> str:
        """Generate recommendation based on final knowledge state"""
        
        combined_mastery = knowledge_analysis['combined_mastery']
        
        if combined_mastery >= 0.9:
            return "Excellent mastery! Ready for advanced topics or next chapter."
        elif combined_mastery >= 0.7:
            return "Good understanding. Consider practicing more difficult questions."
        elif combined_mastery >= 0.5:
            return "Moderate understanding. Focus on practice with mixed difficulties."
        else:
            return "Need more practice. Focus on fundamental concepts and easier questions."

# Create global instance
simple_orchestrator = SimpleAdaptiveOrchestrator()