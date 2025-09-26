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
            # Get BKT state
            bkt_state = self.bkt_service.get_knowledge_state(student_username, subject)
            
            # Get DKT prediction
            dkt_prediction = self.dkt_service.predict_performance(student_username, subject)
            
            return {
                'success': True,
                'bkt_mastery': bkt_state.get('mastery_level', 0.1),
                'dkt_prediction': dkt_prediction.get('predicted_performance', 0.5),
                'combined_confidence': (bkt_state.get('mastery_level', 0.1) + dkt_prediction.get('predicted_performance', 0.5)) / 2,
                'knowledge_state': {
                    'bkt': bkt_state,
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
            # Update BKT
            bkt_update = self.bkt_service.update_mastery(
                student_username, 
                subject, 
                is_correct, 
                difficulty_level
            )
            
            # Update DKT
            dkt_update = self.dkt_service.update_knowledge_state(
                student_username,
                subject,
                question_id,
                is_correct,
                time_spent
            )
            
            # Generate adaptive feedback
            mastery_level = bkt_update.get('new_mastery', 0.1)
            
            if mastery_level > 0.8:
                difficulty_advice = "Questions getting HARDER"
                adaptation_message = "🚀 Great progress! Let's challenge you with harder questions."
            elif mastery_level > 0.5:
                difficulty_advice = "Maintaining current difficulty"
                adaptation_message = "📚 You're doing well. Keep practicing at this level."
            else:
                difficulty_advice = "Questions getting EASIER"
                adaptation_message = "💪 Let's try easier questions to build your confidence."
            
            return {
                'success': True,
                'bkt_update': bkt_update,
                'dkt_update': dkt_update,
                'orchestrated_feedback': {
                    'mastery_change': f"Mastery level: {mastery_level * 100:.1f}%",
                    'difficulty_adaptation': difficulty_advice,
                    'adaptation_message': adaptation_message
                },
                'new_mastery_level': mastery_level,
                'predicted_performance': dkt_update.get('predicted_performance', 0.5)
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