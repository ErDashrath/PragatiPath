"""
Production-Ready Adaptive Learning Session System

This module implements industry-standard adaptive learning with:
- BKT/DKT integration for knowledge tracking
- Dynamic difficulty adjustment based on performance
- Mastery level calculation and persistence
- Proper fallback mechanisms
- Session-based progress tracking

Author: AI Assistant
Date: 2024-12-26
"""

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum

from django.contrib.auth.models import User
from django.db import transaction
from core.models import StudentProfile
from student_model.bkt import BKTService
from student_model.dkt import DKTService
from assessment.models import AdaptiveQuestion
from assessment.improved_models import Subject, Chapter, StudentSession

logger = logging.getLogger(__name__)

class DifficultyLevel(Enum):
    """Standardized difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"

class MasteryLevel(Enum):
    """Industry standard mastery levels"""
    NOVICE = "novice"          # 0.0 - 0.3
    DEVELOPING = "developing"   # 0.3 - 0.5
    PROFICIENT = "proficient"  # 0.5 - 0.7
    ADVANCED = "advanced"      # 0.7 - 0.85
    EXPERT = "expert"          # 0.85 - 1.0

class AdaptiveSessionManager:
    """
    Industry-standard adaptive learning session management
    
    Key Features:
    - BKT/DKT integration for knowledge state tracking
    - Dynamic difficulty adjustment based on performance
    - Mastery level calculation and persistence
    - Proper fallback mechanisms
    - Industry-standard progression rules
    """
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
        
        # Industry standard parameters
        self.difficulty_progression = {
            DifficultyLevel.VERY_EASY: DifficultyLevel.EASY,
            DifficultyLevel.EASY: DifficultyLevel.MODERATE,
            DifficultyLevel.MODERATE: DifficultyLevel.DIFFICULT,
            DifficultyLevel.DIFFICULT: DifficultyLevel.DIFFICULT  # Stay at hardest
        }
        
        self.difficulty_regression = {
            DifficultyLevel.DIFFICULT: DifficultyLevel.MODERATE,
            DifficultyLevel.MODERATE: DifficultyLevel.EASY,
            DifficultyLevel.EASY: DifficultyLevel.VERY_EASY,
            DifficultyLevel.VERY_EASY: DifficultyLevel.VERY_EASY  # Stay at easiest
        }
        
        # Mastery thresholds (industry standard)
        self.mastery_thresholds = {
            MasteryLevel.NOVICE: (0.0, 0.3),
            MasteryLevel.DEVELOPING: (0.3, 0.5), 
            MasteryLevel.PROFICIENT: (0.5, 0.7),
            MasteryLevel.ADVANCED: (0.7, 0.85),
            MasteryLevel.EXPERT: (0.85, 1.0)
        }
        
        # Difficulty adjustment rules
        self.progression_rules = {
            "consecutive_correct_to_advance": 2,
            "consecutive_incorrect_to_regress": 2,
            "min_questions_per_difficulty": 3,
            "max_questions_total": 20,
            "target_accuracy_range": (0.6, 0.8)  # Industry standard sweet spot
        }
    
    @transaction.atomic
    def start_adaptive_session(
        self,
        student_id: int,
        subject_code: str,
        chapter_id: Optional[int] = None,
        max_questions: int = 15
    ) -> Dict[str, Any]:
        """
        Start a new adaptive learning session
        
        Args:
            student_id: Student's user ID
            subject_code: Subject code from database
            chapter_id: Optional specific chapter ID
            max_questions: Maximum questions in session
            
        Returns:
            Session initialization result with session ID and initial state
        """
        
        try:
            logger.info(f"🎯 Starting adaptive session - Student: {student_id}, Subject: {subject_code}")
            
            # Validate and get user
            user = User.objects.get(id=student_id)
            
            # Ensure student profile exists
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bkt_parameters': {},
                    'dkt_hidden_state': [],
                    'fundamentals': {'listening': 0.5, 'grasping': 0.5, 'retention': 0.5, 'application': 0.5},
                    'interaction_history': []
                }
            )
            
            # Validate subject and chapter
            subject_obj = Subject.objects.get(code=subject_code, is_active=True)
            chapter_obj = None
            if chapter_id:
                chapter_obj = Chapter.objects.get(id=chapter_id, subject=subject_obj, is_active=True)
            else:
                chapter_obj = subject_obj.chapters.filter(is_active=True).first()
            
            if not chapter_obj:
                raise ValueError(f"No active chapters found for subject {subject_code}")
            
            # Create session
            session = StudentSession.objects.create(
                student=user,
                subject=subject_obj,
                chapter=chapter_obj,
                session_type='PRACTICE',
                session_name=f"Adaptive Learning - {subject_obj.name}",
                total_questions_planned=max_questions,
                status='ACTIVE'
            )
            
            # Generate skill ID for knowledge tracking
            skill_id = f"{subject_code}_chapter_{chapter_obj.chapter_number}"
            
            # Get initial knowledge state
            bkt_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            dkt_state = self.dkt_service.get_dkt_state(user)
            
            # Calculate initial mastery and determine starting difficulty
            initial_mastery = self._calculate_combined_mastery(bkt_params.P_L, dkt_state, skill_id)
            starting_difficulty = self._determine_starting_difficulty(initial_mastery)
            
            # Initialize session state
            session_state = {
                'session_id': str(session.id),
                'student_id': student_id,
                'subject_code': subject_code,
                'chapter_id': chapter_obj.id,
                'skill_id': skill_id,
                'current_difficulty': starting_difficulty.value,
                'initial_mastery': initial_mastery,
                'questions_attempted': 0,
                'consecutive_correct': 0,
                'consecutive_incorrect': 0,
                'difficulty_history': [starting_difficulty.value],
                'performance_history': [],
                'max_questions': max_questions,
                'session_active': True,
                'mastery_progression': [initial_mastery]
            }
            
            # Save session config
            session.session_config = session_state
            session.save()
            
            logger.info(f"✅ Session started - ID: {session.id}, Starting difficulty: {starting_difficulty.value}, Initial mastery: {initial_mastery:.3f}")
            
            return {
                'success': True,
                'session_id': str(session.id),
                'initial_state': session_state,
                'starting_difficulty': starting_difficulty.value,
                'initial_mastery': initial_mastery,
                'mastery_level': self._get_mastery_level(initial_mastery).value,
                'subject_name': subject_obj.name,
                'chapter_name': chapter_obj.name
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start adaptive session: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """
        Get the next adaptive question for the session
        
        Args:
            session_id: Active session ID
            
        Returns:
            Next question data or session completion status
        """
        
        try:
            # Get session
            session = StudentSession.objects.get(id=session_id, status='ACTIVE')
            session_state = session.session_config
            
            # Check if session should end
            if (session_state['questions_attempted'] >= session_state['max_questions'] or
                not session_state['session_active']):
                return self._finalize_session(session)
            
            # Get current difficulty and find question
            current_difficulty = DifficultyLevel(session_state['current_difficulty'])
            question_data = self._select_adaptive_question(
                session_state['subject_code'],
                session_state['chapter_id'],
                current_difficulty
            )
            
            if not question_data['success']:
                # Try fallback difficulties
                fallback_question = self._try_fallback_questions(
                    session_state['subject_code'],
                    session_state['chapter_id'],
                    current_difficulty
                )
                
                if not fallback_question['success']:
                    return self._finalize_session(session)
                
                question_data = fallback_question
            
            # Update session state for tracking
            session_state['current_question'] = question_data['question']
            session.session_config = session_state
            session.save()
            
            logger.info(f"📝 Next question - Difficulty: {current_difficulty.value}, Question: {question_data['question']['id']}")
            
            return {
                'success': True,
                'question': question_data['question'],
                'current_difficulty': current_difficulty.value,
                'questions_attempted': session_state['questions_attempted'],
                'max_questions': session_state['max_questions'],
                'current_mastery': session_state['mastery_progression'][-1] if session_state['mastery_progression'] else 0.5
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get next question: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    @transaction.atomic
    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        student_answer: str,
        response_time: float
    ) -> Dict[str, Any]:
        """
        Submit student answer and update knowledge state
        
        Args:
            session_id: Active session ID
            question_id: Question that was answered
            student_answer: Student's answer (a, b, c, d)
            response_time: Time taken to answer in seconds
            
        Returns:
            Answer result with updated mastery and next difficulty
        """
        
        try:
            # Get session and question
            session = StudentSession.objects.get(id=session_id, status='ACTIVE')
            question = AdaptiveQuestion.objects.get(id=question_id)
            session_state = session.session_config
            
            # Check answer correctness
            is_correct = student_answer.lower() == question.answer.lower()
            
            # Update knowledge models
            interaction_data = {
                'question_id': question_id,
                'difficulty': question.difficulty_level,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat(),
                'chapter': question.chapter.name if question.chapter else None
            }
            
            skill_id = session_state['skill_id']
            user = session.student
            
            # Update BKT
            bkt_result, bkt_progression = self.bkt_service.update_skill_bkt_with_progression(
                user=user,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data=interaction_data
            )
            
            # Update DKT
            dkt_result = self.dkt_service.update_dkt_knowledge(
                user=user,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data=interaction_data
            )
            
            # Calculate new mastery
            new_bkt_params = self.bkt_service.get_skill_bkt_params(user, skill_id)
            updated_dkt_state = self.dkt_service.get_dkt_state(user)
            new_mastery = self._calculate_combined_mastery(new_bkt_params.P_L, updated_dkt_state, skill_id)
            
            # Update performance tracking
            self._update_performance_tracking(session_state, is_correct, new_mastery)
            
            # Determine next difficulty based on performance
            next_difficulty = self._calculate_next_difficulty(session_state)
            session_state['current_difficulty'] = next_difficulty.value
            
            # Update session statistics
            session.questions_attempted = session_state['questions_attempted']
            if is_correct:
                session.questions_correct += 1
            else:
                session.questions_incorrect += 1
            
            # Save updated state
            session.session_config = session_state
            session.save()
            
            # Prepare response
            mastery_level = self._get_mastery_level(new_mastery)
            
            result = {
                'success': True,
                'is_correct': is_correct,
                'correct_answer': question.answer,
                'explanation': getattr(question, 'explanation', ''),
                'new_mastery': round(new_mastery, 3),
                'mastery_level': mastery_level.value,
                'mastery_change': round(new_mastery - session_state['mastery_progression'][-2] if len(session_state['mastery_progression']) > 1 else 0, 3),
                'next_difficulty': next_difficulty.value,
                'difficulty_changed': next_difficulty.value != session_state['difficulty_history'][-1],
                'questions_attempted': session_state['questions_attempted'],
                'consecutive_correct': session_state['consecutive_correct'],
                'consecutive_incorrect': session_state['consecutive_incorrect'],
                'bkt_progression': bkt_progression,
                'performance_trend': self._analyze_performance_trend(session_state['performance_history'][-5:])
            }
            
            logger.info(f"✅ Answer submitted - Correct: {is_correct}, New mastery: {new_mastery:.3f}, Next difficulty: {next_difficulty.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to submit answer: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive session summary and analytics
        
        Args:
            session_id: Session ID to summarize
            
        Returns:
            Complete session analytics and mastery progression
        """
        
        try:
            session = StudentSession.objects.get(id=session_id)
            session_state = session.session_config
            
            # Calculate final statistics
            total_questions = session_state['questions_attempted']
            accuracy = (session.questions_correct / total_questions * 100) if total_questions > 0 else 0
            
            final_mastery = session_state['mastery_progression'][-1] if session_state['mastery_progression'] else 0.5
            initial_mastery = session_state['initial_mastery']
            mastery_improvement = final_mastery - initial_mastery
            
            # Analyze difficulty progression
            difficulty_stats = self._analyze_difficulty_progression(session_state['difficulty_history'])
            
            # Generate recommendations
            recommendations = self._generate_recommendations(session_state, final_mastery)
            
            summary = {
                'session_id': session_id,
                'student_id': session_state['student_id'],
                'subject_code': session_state['subject_code'],
                'total_questions': total_questions,
                'questions_correct': session.questions_correct,
                'questions_incorrect': session.questions_incorrect,
                'accuracy_percentage': round(accuracy, 1),
                'initial_mastery': round(initial_mastery, 3),
                'final_mastery': round(final_mastery, 3),
                'mastery_improvement': round(mastery_improvement, 3),
                'initial_mastery_level': self._get_mastery_level(initial_mastery).value,
                'final_mastery_level': self._get_mastery_level(final_mastery).value,
                'mastery_progression': [round(m, 3) for m in session_state['mastery_progression']],
                'difficulty_progression': session_state['difficulty_history'],
                'difficulty_stats': difficulty_stats,
                'performance_history': session_state['performance_history'],
                'recommendations': recommendations,
                'session_duration': self._calculate_session_duration(session),
                'session_complete': session.status == 'COMPLETED'
            }
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get session summary: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _calculate_combined_mastery(self, bkt_mastery: float, dkt_state, skill_id: str) -> float:
        """Calculate combined mastery using BKT and DKT (industry standard weighting)"""
        
        # Get DKT prediction safely
        dkt_prediction = 0.5  # Default fallback
        if hasattr(dkt_state, 'skill_predictions') and isinstance(dkt_state.skill_predictions, dict):
            dkt_prediction = dkt_state.skill_predictions.get(skill_id, 0.5)
        
        # Industry standard: 70% BKT (more reliable) + 30% DKT (trend detection)
        combined = (bkt_mastery * 0.7) + (dkt_prediction * 0.3)
        return max(0.0, min(1.0, combined))  # Clamp to valid range
    
    def _determine_starting_difficulty(self, mastery: float) -> DifficultyLevel:
        """Determine starting difficulty based on initial mastery"""
        
        if mastery < 0.2:
            return DifficultyLevel.VERY_EASY
        elif mastery < 0.4:
            return DifficultyLevel.EASY
        elif mastery < 0.7:
            return DifficultyLevel.MODERATE
        else:
            return DifficultyLevel.DIFFICULT
    
    def _get_mastery_level(self, mastery: float) -> MasteryLevel:
        """Convert numeric mastery to level category"""
        
        for level, (min_val, max_val) in self.mastery_thresholds.items():
            if min_val <= mastery < max_val:
                return level
        return MasteryLevel.EXPERT  # If >= 0.85
    
    def _select_adaptive_question(
        self, 
        subject_code: str, 
        chapter_id: int, 
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """Select question with specified difficulty from chapter"""
        
        try:
            questions = AdaptiveQuestion.objects.filter(
                subject=subject_code,
                chapter_id=chapter_id,
                difficulty_level=difficulty.value,
                is_active=True
            ).order_by('?')  # Random order
            
            if questions.exists():
                question = questions.first()
                return {
                    'success': True,
                    'question': {
                        'id': str(question.id),
                        'text': question.question_text,
                        'options': [question.option_a, question.option_b, question.option_c, question.option_d],
                        'correct_answer': question.answer,
                        'difficulty': question.difficulty_level,
                        'chapter': question.chapter.name if question.chapter else None,
                        'topic': question.topic,
                        'tags': question.tags
                    }
                }
            else:
                return {'success': False, 'reason': f'No {difficulty.value} questions found'}
                
        except Exception as e:
            logger.error(f"❌ Question selection failed: {e}")
            return {'success': False, 'reason': str(e)}
    
    def _try_fallback_questions(
        self, 
        subject_code: str, 
        chapter_id: int, 
        target_difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """Try fallback difficulties when target difficulty has no questions"""
        
        # Define fallback order
        all_difficulties = [DifficultyLevel.MODERATE, DifficultyLevel.EASY, DifficultyLevel.DIFFICULT, DifficultyLevel.VERY_EASY]
        
        # Remove target difficulty and try others
        fallback_difficulties = [d for d in all_difficulties if d != target_difficulty]
        
        for difficulty in fallback_difficulties:
            result = self._select_adaptive_question(subject_code, chapter_id, difficulty)
            if result['success']:
                logger.warning(f"⚠️ Using fallback difficulty {difficulty.value} instead of {target_difficulty.value}")
                return result
        
        # Final fallback: try any question from subject
        try:
            questions = AdaptiveQuestion.objects.filter(
                subject=subject_code,
                is_active=True
            ).order_by('?')
            
            if questions.exists():
                question = questions.first()
                logger.warning(f"⚠️ Using any available question from subject {subject_code}")
                return {
                    'success': True,
                    'question': {
                        'id': str(question.id),
                        'text': question.question_text,
                        'options': [question.option_a, question.option_b, question.option_c, question.option_d],
                        'correct_answer': question.answer,
                        'difficulty': question.difficulty_level,
                        'chapter': question.chapter.name if question.chapter else None,
                        'topic': question.topic,
                        'tags': question.tags
                    }
                }
        except Exception as e:
            logger.error(f"❌ Fallback question selection failed: {e}")
        
        return {'success': False, 'reason': 'No questions available'}
    
    def _update_performance_tracking(self, session_state: Dict, is_correct: bool, new_mastery: float):
        """Update performance tracking counters and history"""
        
        session_state['questions_attempted'] += 1
        session_state['mastery_progression'].append(new_mastery)
        
        # Update consecutive counters
        if is_correct:
            session_state['consecutive_correct'] += 1
            session_state['consecutive_incorrect'] = 0
        else:
            session_state['consecutive_correct'] = 0
            session_state['consecutive_incorrect'] += 1
        
        # Add to performance history
        session_state['performance_history'].append({
            'question_number': session_state['questions_attempted'],
            'is_correct': is_correct,
            'mastery': new_mastery,
            'difficulty': session_state['current_difficulty']
        })
    
    def _calculate_next_difficulty(self, session_state: Dict) -> DifficultyLevel:
        """Calculate next difficulty based on performance and industry rules"""
        
        current_difficulty = DifficultyLevel(session_state['current_difficulty'])
        consecutive_correct = session_state['consecutive_correct']
        consecutive_incorrect = session_state['consecutive_incorrect']
        current_mastery = session_state['mastery_progression'][-1]
        
        # Industry standard rules
        should_advance = (
            consecutive_correct >= self.progression_rules['consecutive_correct_to_advance'] and
            current_mastery > 0.7  # High confidence before advancing
        )
        
        should_regress = (
            consecutive_incorrect >= self.progression_rules['consecutive_incorrect_to_regress'] or
            current_mastery < 0.3  # Low mastery requires easier content
        )
        
        if should_advance and current_difficulty != DifficultyLevel.DIFFICULT:
            next_difficulty = self.difficulty_progression[current_difficulty]
            logger.info(f"📈 Advancing difficulty: {current_difficulty.value} → {next_difficulty.value}")
            return next_difficulty
        
        elif should_regress and current_difficulty != DifficultyLevel.VERY_EASY:
            next_difficulty = self.difficulty_regression[current_difficulty]
            logger.info(f"📉 Reducing difficulty: {current_difficulty.value} → {next_difficulty.value}")
            return next_difficulty
        
        # Stay at current difficulty
        return current_difficulty
    
    def _finalize_session(self, session: StudentSession) -> Dict[str, Any]:
        """Finalize session and save final mastery"""
        
        try:
            session_state = session.session_config
            final_mastery = session_state['mastery_progression'][-1] if session_state['mastery_progression'] else 0.5
            
            # Update session record
            session.status = 'COMPLETED'
            session.session_end_time = datetime.now()
            session.percentage_score = (session.questions_correct / session.questions_attempted * 100) if session.questions_attempted > 0 else 0
            session.save()
            
            # Save mastery to student profile
            profile = session.student.student_profile
            if not hasattr(profile, 'mastery_levels'):
                profile.mastery_levels = {}
            
            skill_id = session_state['skill_id']
            profile.mastery_levels[skill_id] = {
                'mastery_score': final_mastery,
                'mastery_level': self._get_mastery_level(final_mastery).value,
                'last_updated': datetime.now().isoformat(),
                'questions_attempted': session.questions_attempted,
                'session_id': str(session.id)
            }
            profile.save()
            
            logger.info(f"🏁 Session finalized - Final mastery: {final_mastery:.3f}, Level: {self._get_mastery_level(final_mastery).value}")
            
            return {
                'success': True,
                'session_complete': True,
                'final_mastery': round(final_mastery, 3),
                'mastery_level': self._get_mastery_level(final_mastery).value,
                'total_questions': session.questions_attempted,
                'accuracy': round(session.percentage_score, 1),
                'session_id': str(session.id)
            }
            
        except Exception as e:
            logger.error(f"❌ Session finalization failed: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def _analyze_difficulty_progression(self, difficulty_history: List[str]) -> Dict[str, Any]:
        """Analyze how difficulty changed throughout session"""
        
        if not difficulty_history:
            return {}
        
        difficulty_counts = {}
        for diff in difficulty_history:
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        return {
            'starting_difficulty': difficulty_history[0],
            'ending_difficulty': difficulty_history[-1],
            'difficulty_counts': difficulty_counts,
            'progression_changes': len(set(difficulty_history)) - 1,
            'highest_difficulty_reached': max(difficulty_history, key=lambda x: ['very_easy', 'easy', 'moderate', 'difficult'].index(x))
        }
    
    def _generate_recommendations(self, session_state: Dict, final_mastery: float) -> List[str]:
        """Generate personalized recommendations based on performance"""
        
        recommendations = []
        mastery_level = self._get_mastery_level(final_mastery)
        accuracy = session_state.get('questions_correct', 0) / max(session_state.get('questions_attempted', 1), 1) * 100
        
        if mastery_level == MasteryLevel.EXPERT:
            recommendations.append("Excellent mastery! Ready for advanced topics or next chapter.")
            recommendations.append("Consider taking practice tests to maintain proficiency.")
        
        elif mastery_level == MasteryLevel.ADVANCED:
            recommendations.append("Strong understanding demonstrated. Practice more difficult questions.")
            recommendations.append("Focus on speed and accuracy with challenging problems.")
        
        elif mastery_level == MasteryLevel.PROFICIENT:
            recommendations.append("Good progress! Continue practicing with mixed difficulties.")
            recommendations.append("Review topics where you had incorrect answers.")
        
        elif mastery_level == MasteryLevel.DEVELOPING:
            recommendations.append("Focus on fundamental concepts with easier questions.")
            recommendations.append("Spend more time on understanding before attempting harder problems.")
        
        else:  # NOVICE
            recommendations.append("Start with basic concepts and very easy questions.")
            recommendations.append("Consider reviewing prerequisite topics before continuing.")
        
        # Performance-based recommendations
        if accuracy < 50:
            recommendations.append("Review incorrect answers and understand the concepts.")
        elif accuracy > 80:
            recommendations.append("Great accuracy! You can handle more challenging questions.")
        
        return recommendations
    
    def _analyze_performance_trend(self, recent_performance: List[Dict]) -> str:
        """Analyze recent performance trend"""
        
        if len(recent_performance) < 3:
            return "insufficient_data"
        
        correct_count = sum(1 for p in recent_performance if p.get('is_correct', False))
        accuracy = correct_count / len(recent_performance)
        
        if accuracy >= 0.8:
            return "strong_performance"
        elif accuracy >= 0.6:
            return "steady_performance" 
        elif accuracy >= 0.4:
            return "inconsistent_performance"
        else:
            return "needs_support"
    
    def _calculate_session_duration(self, session: StudentSession) -> Dict[str, Any]:
        """Calculate session duration and timing statistics"""
        
        if session.session_end_time and session.session_start_time:
            duration = session.session_end_time - session.session_start_time
            return {
                'total_seconds': int(duration.total_seconds()),
                'total_minutes': round(duration.total_seconds() / 60, 1),
                'average_time_per_question': round(duration.total_seconds() / max(session.questions_attempted, 1), 1)
            }
        
        return {'total_seconds': 0, 'total_minutes': 0, 'average_time_per_question': 0}

# Global instance for easy import
adaptive_session_manager = AdaptiveSessionManager()