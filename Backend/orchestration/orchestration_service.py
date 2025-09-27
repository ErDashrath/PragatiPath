"""
Orchestration Service for BKT/DKT Integration
Provides unified interface for adaptive learning orchestration.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import StudentProfile
from student_model.bkt import BKTService
from student_model.dkt import DKTService

logger = logging.getLogger(__name__)

class OrchestrationService:
    """
    Orchestrates BKT and DKT services for comprehensive adaptive learning.
    """
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
        logger.info("OrchestrationService initialized with BKT and DKT services")
    
    def initialize_student_session(self, student_username: str, subject: str) -> Dict[str, Any]:
        """
        Initialize a new adaptive learning session with proper BKT/DKT setup.
        
        Args:
            student_username: Username of the student
            subject: Subject for the session
            
        Returns:
            Dict containing initialization status and parameters
        """
        try:
            # Get or create user
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username=student_username)
            if created:
                logger.info(f"Created new user: {student_username}")
            
            # Initialize BKT parameters for the subject skill
            skill_id = f"{subject}_skill"
            bkt_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            
            # Initialize DKT state
            dkt_init = self.dkt_service.initialize_student(student_username, subject)
            
            logger.info(f"✅ Initialized session for {student_username} in {subject}")
            
            return {
                'success': True,
                'student_username': student_username,
                'subject': subject,
                'skill_id': skill_id,
                'initial_mastery': bkt_params.P_L,
                'bkt_initialized': True,
                'dkt_initialized': dkt_init.get('success', False),
                'ready_for_adaptive_learning': True
            }
            
        except Exception as e:
            print(f"❌ Failed to initialize session for {student_username}: {e}")  # Use print instead of logger
            return {
                'success': False,
                'error': str(e),
                'ready_for_adaptive_learning': False
            }
    
    def get_comprehensive_knowledge_state(self, student_username: str, subject: str) -> Dict[str, Any]:
        """
        Get comprehensive knowledge state from both BKT and DKT.
        
        Args:
            student_username: Username of the student
            subject: Subject to analyze
            
        Returns:
            Dict containing BKT and DKT knowledge state
        """
        try:
            # Get user object for BKT state
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(username=student_username)
            except User.DoesNotExist:
                logger.error(f"User {student_username} not found for knowledge state")
                return {
                    'success': False,
                    'error': f'User {student_username} not found',
                    'bkt_mastery': 0.1,
                    'dkt_prediction': 0.5,
                    'combined_confidence': 0.3
                }
            
            # Get BKT state using proper method
            skill_id = f"{subject}_skill"
            print(f"🔍 DEBUG - Getting BKT state for {student_username}, skill: {skill_id}")
            bkt_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            bkt_mastery = bkt_params.P_L
            print(f"🔍 DEBUG - Retrieved BKT mastery: {bkt_mastery:.3f}")
            
            # Get DKT prediction
            dkt_prediction = self.dkt_service.predict_performance(student_username, subject)
            dkt_score = dkt_prediction.get('predicted_performance', 0.5)
            
            # Calculate combined confidence
            combined_confidence = (bkt_mastery + dkt_score) / 2
            
            logger.info(f"📊 Knowledge state - BKT: {bkt_mastery:.3f}, DKT: {dkt_score:.3f}, Combined: {combined_confidence:.3f}")
            
            return {
                'success': True,
                'bkt_mastery': bkt_mastery,
                'dkt_prediction': dkt_score,
                'combined_confidence': combined_confidence,
                'knowledge_state': {
                    'bkt': {'mastery_level': bkt_mastery, 'skill_id': skill_id},
                    'dkt': dkt_prediction
                },
                'timestamp': str(timezone.now())
            }
        except Exception as e:
            logger.error(f"Failed to get comprehensive knowledge state: {e}")
            return {
                'success': False,
                'error': str(e),
                'bkt_mastery': 0.1,
                'dkt_prediction': 0.5,
                'combined_confidence': 0.3
            }
    
    def get_comprehensive_knowwledge_state(self, student_username: str, subject: str) -> Dict[str, Any]:
        """
        Typo-tolerant version of get_comprehensive_knowledge_state.
        This handles the typo in simple_frontend_api.py
        """
        return self.get_comprehensive_knowledge_state(student_username, subject)
    
    def process_interaction(self, student_username: str, subject: str, question_id: str, 
                          is_correct: bool, time_spent: int, difficulty_level: str = 'medium') -> Dict[str, Any]:
        """
        Process student interaction through both BKT and DKT.
        
        Args:
            student_username: Username of the student
            subject: Subject of the question
            question_id: ID of the question
            is_correct: Whether the answer was correct
            time_spent: Time spent on question (seconds)
            difficulty_level: Difficulty level of the question
            
        Returns:
            Dict containing orchestrated feedback and updates
        """
        try:
            # Get user object for BKT updates
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(username=student_username)
            except User.DoesNotExist:
                logger.error(f"User {student_username} not found")
                return {
                    'success': False,
                    'error': f'User {student_username} not found'
                }
            
            # Update BKT - using proper method name and parameters
            skill_id = f"{subject}_skill"
            
            print(f"🔍 DEBUG - Before BKT update for {student_username}, skill: {skill_id}")
            old_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            print(f"🔍 DEBUG - Old BKT mastery: {old_params.P_L:.3f}")
            
            updated_bkt_params, _ = self.bkt_service.update_skill_bkt_with_progression(
                user=user,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={
                    'timestamp': str(timezone.now()),
                    'question_id': question_id,
                    'difficulty': difficulty_level,
                    'time_spent': time_spent
                }
            )
            
            print(f"🔍 DEBUG - After BKT update - New mastery: {updated_bkt_params.P_L:.3f}")
            
            bkt_update = {
                'success': True,
                'old_mastery': updated_bkt_params.P_L0,
                'new_mastery': updated_bkt_params.P_L,
                'skill_id': skill_id
            }
            
            # Update DKT
            dkt_update = self.dkt_service.update_knowledge_state(
                student_username,
                subject,
                question_id,
                is_correct,
                time_spent
            )
            
            # Generate intelligent adaptive feedback based on performance and mastery changes
            mastery_level = updated_bkt_params.P_L
            old_mastery = old_params.P_L
            mastery_change = mastery_level - old_mastery
            
            print(f"🎯 Generating feedback: correct={is_correct}, old_mastery={old_mastery:.3f}, new_mastery={mastery_level:.3f}, change={mastery_change:+.3f}")
            
            # Generate contextually appropriate messages
            if is_correct:
                # Correct answer - positive reinforcement with appropriate next steps
                if mastery_level > 0.9:
                    difficulty_advice = "Questions getting HARDER"
                    adaptation_message = "🎉 Excellent! You've mastered this level. Time for advanced challenges!"
                elif mastery_level > 0.7:
                    difficulty_advice = "Questions getting HARDER" 
                    adaptation_message = "🚀 Great progress! Questions will get harder to challenge you more."
                elif mastery_level > 0.4:
                    difficulty_advice = "Gradually getting HARDER"
                    adaptation_message = "👍 Good work! We'll gradually increase the challenge level."
                else:
                    difficulty_advice = "Building confidence"
                    adaptation_message = "✅ Nice job! Let's build more confidence before increasing difficulty."
            else:
                # Wrong answer - supportive guidance based on mastery level
                if mastery_level > 0.8:
                    # High mastery student made a mistake - probably just a slip
                    difficulty_advice = "Staying at current level"
                    adaptation_message = "🤔 Don't worry! Even experts make mistakes. Let's continue at this level."
                elif mastery_level > 0.5:
                    # Medium mastery - might need to step back slightly
                    difficulty_advice = "Slightly EASIER questions"
                    adaptation_message = "� Let's try some slightly easier questions to reinforce your understanding."
                elif mastery_level > 0.2:
                    # Lower mastery - definitely need easier questions
                    difficulty_advice = "Questions getting EASIER"
                    adaptation_message = "💪 Let's try easier questions to build your confidence step by step."
                else:
                    # Very low mastery - focus on fundamentals
                    difficulty_advice = "Back to basics"
                    adaptation_message = "📚 Let's focus on building strong fundamentals with easier questions."
            
            # Additional context based on mastery change direction
            if mastery_change > 0.1:
                difficulty_advice += " (big improvement!)"
            elif mastery_change < -0.1:
                difficulty_advice += " (need more practice)"
            
            print(f"📢 Final feedback: {difficulty_advice} - {adaptation_message}")
            
            logger.info(f"✅ Updated BKT mastery: {mastery_level:.3f} for {student_username} (change: {mastery_change:+.3f})")
            
            return {
                'success': True,
                'bkt_update': bkt_update,
                'dkt_update': dkt_update,
                'bkt_mastery': mastery_level,  # Add direct access for API compatibility
                'dkt_prediction': dkt_update.get('predicted_performance', 0.5),  # Add direct access
                'new_mastery_level': mastery_level,  # Keep existing field
                'predicted_performance': dkt_update.get('predicted_performance', 0.5),  # Keep existing field
                'orchestrated_feedback': {
                    'mastery_change': f"Mastery level: {mastery_level * 100:.1f}%",
                    'difficulty_adaptation': difficulty_advice,
                    'adaptation_message': adaptation_message
                },
                'knowledge_state': {
                    'bkt': {
                        'mastery_level': mastery_level,
                        'skill_id': skill_id,
                        'transition_prob': updated_bkt_params.P_T,
                        'guess_prob': updated_bkt_params.P_G,
                        'slip_prob': updated_bkt_params.P_S
                    },
                    'dkt': dkt_update
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process interaction: {e}")
            return {
                'success': False,
                'error': str(e),
                'orchestrated_feedback': {
                    'mastery_change': "Unable to calculate mastery change",
                    'difficulty_adaptation': "Maintaining current difficulty",
                    'adaptation_message': "Continue practicing to improve your skills."
                }
            }

# Create singleton instance
orchestration_service = OrchestrationService()

# Legacy compatibility
class LegacyOrchestrationService:
    """Legacy compatibility wrapper"""
    
    def __init__(self):
        self.service = orchestration_service
    
    def get_comprehensive_knowledge_state(self, *args, **kwargs):
        return self.service.get_comprehensive_knowledge_state(*args, **kwargs)
    
    def get_comprehensive_knowwledge_state(self, *args, **kwargs):
        return self.service.get_comprehensive_knowwledge_state(*args, **kwargs)
    
    def process_interaction(self, *args, **kwargs):
        return self.service.process_interaction(*args, **kwargs)