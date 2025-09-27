"""
Simplified Enhanced Adaptive System for Dynamic Question Selection

This is a streamlined version that focuses on core improvements:
1. Smarter difficulty adjustment based on recent performance
2. Better integration with existing BKT/DKT system  
3. Enhanced reasoning for question selection
4. Improved adaptation strategies

Author: AI Assistant
Date: 2024-12-26
"""

import logging
import random
from typing import Dict, Optional, List, Tuple
from django.contrib.auth.models import User
from assessment.models import AdaptiveQuestion, QuestionAttempt, StudentSession
from student_model.bkt import BKTService
from student_model.dkt import DKTService
from orchestration.orchestration_service import orchestration_service

logger = logging.getLogger(__name__)

class SimplifiedEnhancedAdaptive:
    """
    Simplified enhanced adaptive engine focusing on core improvements
    """
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
        logger.info("🚀 Simplified Enhanced Adaptive Engine initialized")
    
    def get_enhanced_question(self, session_id: str) -> Dict:
        """
        Enhanced question selection with improved adaptation logic
        """
        try:
            # Get session and basic info
            session = StudentSession.objects.get(id=session_id)
            student = session.student
            subject = session.session_config.get('subject', 'mathematics')
            
            # Count questions and get recent performance
            question_count = QuestionAttempt.objects.filter(session=session).count() + 1
            recent_attempts = list(QuestionAttempt.objects.filter(session=session).order_by('-created_at')[:5])
            
            # Check session completion
            if question_count > session.total_questions_planned:
                return {
                    'success': False,
                    'session_complete': True,
                    'message': f'Session complete! You have completed all {session.total_questions_planned} questions.'
                }
            
            # Get enhanced mastery assessment
            mastery_level, confidence = self._get_enhanced_mastery(student, subject, recent_attempts)
            
            # Determine optimal difficulty with enhanced logic
            difficulty, strategy = self._determine_enhanced_difficulty(mastery_level, recent_attempts, question_count)
            
            # Select question from database
            selected_question = self._select_optimal_question(subject, difficulty, session)
            
            # Build enhanced response
            if selected_question:
                return self._build_enhanced_response(
                    selected_question, session_id, question_count, subject,
                    difficulty, strategy, mastery_level, confidence
                )
            else:
                return self._build_fallback_response(
                    session_id, question_count, subject, difficulty, strategy, mastery_level
                )
                
        except Exception as e:
            logger.error(f"❌ Enhanced question selection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Enhanced system error, please try again'
            }
    
    def _get_enhanced_mastery(self, student: User, subject: str, recent_attempts: List) -> Tuple[float, float]:
        """
        Get enhanced mastery level combining multiple factors
        """
        try:
            # Base mastery from BKT/DKT orchestration
            skill_id = f"{subject}_adaptive"
            
            try:
                orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                    student_username=student.username,  # Use username, not User object
                    subject=subject
                )
                
                if orchestration_result and orchestration_result.get('success'):
                    base_mastery = orchestration_result.get('bkt_mastery', 0.5)
                    dkt_prediction = orchestration_result.get('dkt_prediction', 0.5)
                    confidence = orchestration_result.get('combined_confidence', 0.5)
                    
                    # Weighted combination
                    mastery_level = (base_mastery * 0.6) + (dkt_prediction * 0.4)
                else:
                    raise Exception("Orchestration failed")
                    
            except Exception as e:
                logger.warning(f"⚠️ Orchestration failed, using BKT fallback: {e}")
                # Fallback to direct BKT
                bkt_params = self.bkt_service.get_skill_bkt_params(student, skill_id)
                mastery_level = bkt_params.P_L if bkt_params else 0.5
                confidence = 0.5
            
            # Enhance with recent performance trend
            if recent_attempts and len(recent_attempts) >= 3:
                recent_accuracy = sum(1 for attempt in recent_attempts if attempt.is_correct) / len(recent_attempts)
                
                # Calculate overall accuracy for comparison
                all_attempts = QuestionAttempt.objects.filter(student=student)
                if all_attempts.exists():
                    overall_accuracy = all_attempts.filter(is_correct=True).count() / all_attempts.count()
                    trend_adjustment = (recent_accuracy - overall_accuracy) * 0.2
                    mastery_level = max(0.1, min(0.9, mastery_level + trend_adjustment))
                    
                    # Increase confidence if recent performance is consistent
                    if abs(recent_accuracy - overall_accuracy) < 0.2:
                        confidence = min(1.0, confidence + 0.1)
            
            return mastery_level, confidence
            
        except Exception as e:
            logger.error(f"❌ Enhanced mastery calculation failed: {e}")
            return 0.5, 0.3
    
    def _determine_enhanced_difficulty(self, mastery_level: float, recent_attempts: List, question_count: int) -> Tuple[str, str]:
        """
        Enhanced difficulty determination with adaptive strategies
        """
        try:
            # Analyze recent performance pattern
            if recent_attempts and len(recent_attempts) >= 3:
                recent_correct = sum(1 for attempt in recent_attempts if attempt.is_correct)
                recent_accuracy = recent_correct / len(recent_attempts)
                
                # Streak analysis
                streak_correct = 0
                streak_incorrect = 0
                
                for attempt in recent_attempts:
                    if attempt.is_correct:
                        streak_correct += 1
                        break
                    else:
                        streak_incorrect += 1
                
                # Enhanced strategy determination
                if streak_correct >= 3 and mastery_level > 0.6:
                    # Student on a roll - advance gradually
                    strategy = "advance"
                    difficulty = "hard" if mastery_level > 0.8 else "medium"
                    
                elif streak_incorrect >= 2 or recent_accuracy < 0.4:
                    # Student struggling - reinforce
                    strategy = "reinforce"
                    difficulty = "easy"
                    
                elif mastery_level > 0.8 and recent_accuracy > 0.7:
                    # High mastery, ready for challenge
                    strategy = "challenge"
                    difficulty = "hard"
                    
                elif question_count <= 3:
                    # Early questions - assess capability
                    strategy = "assess"
                    difficulty = "medium"
                    
                else:
                    # Maintain current level
                    strategy = "maintain"
                    difficulty = "medium" if mastery_level > 0.4 else "easy"
            
            else:
                # Not enough recent data - use mastery-based selection
                if mastery_level > 0.7:
                    difficulty, strategy = "medium", "maintain"
                elif mastery_level > 0.4:
                    difficulty, strategy = "medium", "maintain"  
                else:
                    difficulty, strategy = "easy", "build_foundation"
            
            return difficulty, strategy
            
        except Exception as e:
            logger.error(f"❌ Enhanced difficulty determination failed: {e}")
            return "medium", "maintain"
    
    def _select_optimal_question(self, subject: str, difficulty: str, session: StudentSession) -> Optional[AdaptiveQuestion]:
        """
        Enhanced question selection optimizing for variety and learning
        """
        try:
            # Map subject and difficulty
            subject_mapping = {
                'mathematics': 'quantitative_aptitude',
                'quantitative_aptitude': 'quantitative_aptitude',
                'logical_reasoning': 'logical_reasoning',
                'data_interpretation': 'data_interpretation',
                'verbal_ability': 'verbal_ability'
            }
            
            difficulty_mapping = {
                'easy': 'easy',
                'medium': 'moderate',
                'hard': 'difficult'
            }
            
            db_subject = subject_mapping.get(subject.lower(), 'quantitative_aptitude')
            db_difficulty = difficulty_mapping.get(difficulty, 'moderate')
            
            # Get attempted questions to avoid repetition
            attempted_question_ids = list(
                QuestionAttempt.objects.filter(session=session).values_list('question_id', flat=True)
            )
            
            # Build query
            questions = AdaptiveQuestion.objects.filter(
                subject=db_subject,  # Use subject field instead of subject_code
                difficulty_level=db_difficulty  # Use difficulty_level field
            ).exclude(id__in=attempted_question_ids)
            
            # Try to get variety by selecting from different chapters
            if questions.exists():
                # Group by chapter and pick from least used chapter
                attempted_chapters = list(
                    QuestionAttempt.objects.filter(
                        session=session, 
                        question__chapter__isnull=False
                    ).values_list('question__chapter__name', flat=True)
                )
                
                # Find chapters not yet attempted
                available_questions = list(questions.select_related('chapter'))
                
                for question in available_questions:
                    chapter_name = question.chapter.name if question.chapter else "Mixed"
                    if chapter_name not in attempted_chapters:
                        logger.info(f"📚 Selected from new chapter: {chapter_name}")
                        return question
                
                # If all chapters used, just return first available
                if available_questions:
                    selected = available_questions[0]
                    logger.info(f"🔄 Selected from existing chapter (variety exhausted)")
                    return selected
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Question selection failed: {e}")
            return None
    
    def _build_enhanced_response(self, question: AdaptiveQuestion, session_id: str, 
                               question_count: int, subject: str, difficulty: str, 
                               strategy: str, mastery_level: float, confidence: float) -> Dict:
        """
        Build enhanced response with detailed reasoning
        """
        # Generate reasoning
        reasoning_map = {
            "advance": f"🚀 Advancing to {difficulty} questions as you've shown good progress (mastery: {mastery_level:.1%})",
            "reinforce": f"💪 Reinforcing with {difficulty} questions to strengthen your foundation",
            "challenge": f"🎯 Challenging you with {difficulty} questions to accelerate learning",
            "assess": f"📊 Assessing your capabilities with {difficulty} questions",
            "maintain": f"📈 Maintaining {difficulty} level based on current performance",
            "build_foundation": f"🏗️ Building foundation with {difficulty} questions"
        }
        
        reasoning = reasoning_map.get(strategy, f"Selected {difficulty} question based on your performance")
        
        return {
            'success': True,
            'question_id': f"enhanced_{question.id}",
            'real_question_id': question.id,
            'session_id': session_id,
            'question_number': question_count,
            'subject': subject,
            'subject_display': question.subject.replace('_', ' ').title(),
            'difficulty': difficulty,
            'difficulty_display': f"🎯 {difficulty.upper()}",
            'question_text': question.question_text,
            'options': [
                {'id': 'A', 'text': question.option_a},
                {'id': 'B', 'text': question.option_b},
                {'id': 'C', 'text': question.option_c},
                {'id': 'D', 'text': question.option_d}
            ],
            'correct_answer': question.correct_answer.upper(),
            'explanation': reasoning,
            'topic': question.chapter.name if question.chapter else 'Mixed Topics',
            'enhanced_info': {
                'mastery_level': mastery_level,
                'confidence': confidence,
                'adaptation_strategy': strategy,
                'reasoning': reasoning,
                'expected_success': self._calculate_expected_success(mastery_level, difficulty),
                'enhanced_system': True
            }
        }
    
    def _build_fallback_response(self, session_id: str, question_count: int, subject: str,
                               difficulty: str, strategy: str, mastery_level: float) -> Dict:
        """
        Build fallback response when no database question found
        """
        return {
            'success': True,
            'question_id': f"enhanced_fallback_{session_id}_{question_count}",
            'session_id': session_id,
            'question_number': question_count,
            'subject': subject,
            'difficulty': difficulty,
            'question_text': f"Enhanced {difficulty} question for {subject} (No database questions available)",
            'options': [
                {'id': 'A', 'text': 'Option A'},
                {'id': 'B', 'text': 'Option B'},
                {'id': 'C', 'text': 'Option C'},
                {'id': 'D', 'text': 'Option D'}
            ],
            'correct_answer': 'A',
            'explanation': f"Enhanced adaptive selection: {strategy} strategy with {difficulty} difficulty based on mastery level {mastery_level:.1%}",
            'topic': 'Mock Topic',
            'enhanced_info': {
                'mastery_level': mastery_level,
                'adaptation_strategy': strategy,
                'fallback_used': True,
                'enhanced_system': True
            }
        }
    
    def _calculate_expected_success(self, mastery_level: float, difficulty: str) -> float:
        """
        Calculate expected success probability
        """
        base_success = mastery_level
        
        # Adjust for difficulty
        if difficulty == "easy":
            return min(0.95, base_success + 0.2)
        elif difficulty == "hard":
            return max(0.1, base_success - 0.15)
        else:  # medium
            return base_success

# Create simplified engine instance
simplified_enhanced_engine = SimplifiedEnhancedAdaptive()

def get_simplified_enhanced_question(session_id: str) -> Dict:
    """
    Main entry point for simplified enhanced adaptive question selection
    """
    return simplified_enhanced_engine.get_enhanced_question(session_id)