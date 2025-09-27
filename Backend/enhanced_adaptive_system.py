"""
Enhanced Adaptive Learning System for Dynamic Question Selection

This module enhances the existing BKT/DKT system with:
1. Intelligent difficulty progression
2. Multi-skill knowledge tracking
3. Dynamic question sequencing
4. Personalized learning paths
5. Advanced performance prediction

Author: AI Assistant
Date: 2024-12-26
"""

import logging
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import StudentProfile
from assessment.models import QuestionAttempt, StudentSession, AdaptiveQuestion
from student_model.bkt import BKTService, BKTParameters
from student_model.dkt import DKTService
from orchestration.orchestration_service import OrchestrationService

logger = logging.getLogger(__name__)

# ============================================================================
# Enhanced Data Classes
# ============================================================================

@dataclass
class StudentPerformanceProfile:
    """Comprehensive student performance profile"""
    student_id: str
    
    # Overall performance metrics
    overall_accuracy: float = 0.0
    total_questions_attempted: int = 0
    average_response_time: float = 0.0
    
    # Subject-specific performance
    subject_masteries: Dict[str, float] = field(default_factory=dict)
    subject_accuracies: Dict[str, float] = field(default_factory=dict)
    subject_response_times: Dict[str, float] = field(default_factory=dict)
    
    # Skill-level tracking
    skill_masteries: Dict[str, float] = field(default_factory=dict)
    skill_confidences: Dict[str, float] = field(default_factory=dict)
    
    # Learning patterns
    learning_velocity: float = 0.0  # How fast student improves
    difficulty_preference: str = "adaptive"  # easy, medium, hard, adaptive
    consistency_score: float = 0.0  # How consistent performance is
    
    # Recent performance trends
    recent_accuracy_trend: float = 0.0  # Positive = improving, negative = declining
    streak_correct: int = 0
    streak_incorrect: int = 0
    
    # Time-based patterns
    session_count: int = 0
    total_study_time: float = 0.0
    average_session_length: float = 0.0
    
    # Metadata
    last_updated: datetime = field(default_factory=timezone.now)
    profile_confidence: float = 0.5  # How confident we are in this profile

@dataclass
class QuestionSelectionContext:
    """Context for intelligent question selection"""
    student_profile: StudentPerformanceProfile
    current_session: StudentSession
    
    # Current session state
    questions_completed: int = 0
    session_accuracy: float = 0.0
    recent_performance: List[bool] = field(default_factory=list)  # Last 5 answers
    
    # Learning objectives
    target_skills: List[str] = field(default_factory=list)
    mastery_goals: Dict[str, float] = field(default_factory=dict)
    
    # Constraints
    remaining_questions: int = 0
    time_remaining: Optional[float] = None
    difficulty_limits: Tuple[str, str] = ("easy", "hard")  # min, max
    
    # Adaptive parameters
    exploration_rate: float = 0.2  # How often to try different difficulties
    challenge_rate: float = 0.1  # How often to push beyond comfort zone
    review_rate: float = 0.15  # How often to review easier concepts

@dataclass
class QuestionRecommendation:
    """Enhanced question recommendation with reasoning"""
    question: Optional[AdaptiveQuestion] = None
    difficulty: str = "medium"
    skill_id: str = ""
    subject: str = ""
    
    # Selection reasoning
    selection_reason: str = ""
    confidence: float = 0.5
    expected_success_probability: float = 0.5
    
    # Learning objectives
    learning_objective: str = ""
    skill_targeted: str = ""
    
    # Adaptation strategy
    adaptation_strategy: str = "maintain"  # advance, maintain, reinforce
    next_difficulty_hint: str = "similar"
    
    # Metadata
    selection_timestamp: datetime = field(default_factory=timezone.now)
    fallback_used: bool = False

# ============================================================================
# Enhanced Adaptive Question Selection Engine
# ============================================================================

class EnhancedAdaptiveEngine:
    """
    Advanced adaptive learning engine that provides intelligent question selection
    based on comprehensive student modeling and learning science principles.
    """
    
    def __init__(self):
        self.bkt_service = BKTService()
        self.dkt_service = DKTService()
        self.orchestration_service = OrchestrationService()
        
        # Advanced parameters
        self.mastery_threshold_low = 0.3
        self.mastery_threshold_medium = 0.6
        self.mastery_threshold_high = 0.8
        
        # Learning velocity parameters
        self.fast_learner_threshold = 0.15  # Mastery improvement per question
        self.slow_learner_threshold = 0.05
        
        # Difficulty progression parameters
        self.optimal_success_rate_min = 0.6  # Sweet spot for learning
        self.optimal_success_rate_max = 0.8
        
        logger.info("🚀 Enhanced Adaptive Engine initialized")
    
    # ========================================================================
    # Student Profile Analysis
    # ========================================================================
    
    def build_student_performance_profile(self, student: User) -> StudentPerformanceProfile:
        """
        Build comprehensive student performance profile from historical data
        """
        try:
            logger.info(f"📊 Building performance profile for student: {student.username}")
            
            # Get all question attempts for this student
            attempts = QuestionAttempt.objects.filter(student=student).order_by('-created_at')
            
            if not attempts.exists():
                logger.info(f"ℹ️ No attempts found, returning default profile")
                return StudentPerformanceProfile(student_id=str(student.id))
            
            # Calculate overall metrics
            total_attempts = attempts.count()
            correct_attempts = attempts.filter(is_correct=True).count()
            overall_accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0.0
            
            # Calculate average response time (filter out outliers)
            response_times = [a.time_spent_seconds for a in attempts if a.time_spent_seconds and 1 <= a.time_spent_seconds <= 300]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 30.0
            
            # Subject-specific performance
            subject_masteries = {}
            subject_accuracies = {}
            subject_response_times = {}
            
            for session in StudentSession.objects.filter(student=student):
                subject = session.session_config.get('subject', 'unknown')
                subject_attempts = attempts.filter(session=session)
                
                if subject_attempts.exists():
                    subj_total = subject_attempts.count()
                    subj_correct = subject_attempts.filter(is_correct=True).count()
                    subject_accuracies[subject] = subj_correct / subj_total
                    
                    # Use BKT to get current mastery
                    try:
                        bkt_params = self.bkt_service.get_skill_bkt_params(student, f"{subject}_overall")
                        subject_masteries[subject] = bkt_params.P_L if bkt_params else subject_accuracies[subject]
                    except:
                        subject_masteries[subject] = subject_accuracies[subject]
                    
                    subj_times = [a.time_spent_seconds for a in subject_attempts if a.time_spent_seconds and 1 <= a.time_spent_seconds <= 300]
                    subject_response_times[subject] = sum(subj_times) / len(subj_times) if subj_times else avg_response_time
            
            # Learning velocity calculation
            recent_attempts = attempts[:20]  # Last 20 attempts
            if recent_attempts.count() >= 10:
                older_half = recent_attempts[10:20]
                newer_half = recent_attempts[:10]
                
                older_accuracy = sum(1 for a in older_half if a.is_correct) / len(older_half)
                newer_accuracy = sum(1 for a in newer_half if a.is_correct) / len(newer_half)
                
                learning_velocity = newer_accuracy - older_accuracy
            else:
                learning_velocity = 0.0
            
            # Consistency score (lower variance = higher consistency)
            if total_attempts >= 5:
                recent_results = [1 if a.is_correct else 0 for a in attempts[:10]]
                variance = sum((x - overall_accuracy) ** 2 for x in recent_results) / len(recent_results)
                consistency_score = max(0, 1 - variance)
            else:
                consistency_score = 0.5
            
            # Recent performance trend
            if total_attempts >= 5:
                recent_5 = [1 if a.is_correct else 0 for a in attempts[:5]]
                recent_accuracy = sum(recent_5) / len(recent_5)
                recent_accuracy_trend = recent_accuracy - overall_accuracy
            else:
                recent_accuracy_trend = 0.0
            
            # Streaks
            streak_correct = 0
            streak_incorrect = 0
            
            for attempt in attempts:
                if attempt.is_correct:
                    streak_correct += 1
                    streak_incorrect = 0
                    break
                else:
                    streak_incorrect += 1
                    streak_correct = 0
                    break
            
            # Session statistics
            sessions = StudentSession.objects.filter(student=student)
            session_count = sessions.count()
            total_study_time = sum(s.total_time_spent or 0 for s in sessions)
            avg_session_length = total_study_time / session_count if session_count > 0 else 0.0
            
            profile = StudentPerformanceProfile(
                student_id=str(student.id),
                overall_accuracy=overall_accuracy,
                total_questions_attempted=total_attempts,
                average_response_time=avg_response_time,
                subject_masteries=subject_masteries,
                subject_accuracies=subject_accuracies,
                subject_response_times=subject_response_times,
                learning_velocity=learning_velocity,
                consistency_score=consistency_score,
                recent_accuracy_trend=recent_accuracy_trend,
                streak_correct=streak_correct,
                streak_incorrect=streak_incorrect,
                session_count=session_count,
                total_study_time=total_study_time,
                average_session_length=avg_session_length,
                profile_confidence=min(1.0, total_attempts / 50.0),  # More attempts = higher confidence
                last_updated=timezone.now()
            )
            
            logger.info(f"✅ Profile built: accuracy={overall_accuracy:.3f}, velocity={learning_velocity:.3f}, consistency={consistency_score:.3f}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Failed to build student profile: {e}")
            return StudentPerformanceProfile(student_id=str(student.id))
    
    # ========================================================================
    # Advanced Question Selection Algorithm
    # ========================================================================
    
    def select_optimal_question(self, context: QuestionSelectionContext) -> QuestionRecommendation:
        """
        Select optimal question using advanced adaptive algorithms
        """
        try:
            logger.info(f"🎯 Selecting optimal question for student profile")
            
            student = User.objects.get(id=context.student_profile.student_id)
            subject = context.current_session.session_config.get('subject', 'mathematics')
            
            # Determine optimal difficulty using multiple factors
            optimal_difficulty, strategy = self._determine_optimal_difficulty(context)
            
            # Get comprehensive knowledge state
            current_mastery = self._get_current_mastery(student, subject, context)
            
            # Calculate expected success probability for this difficulty
            expected_success = self._calculate_expected_success(current_mastery, optimal_difficulty, context)
            
            # Select question from database
            selected_question = self._select_question_from_pool(
                subject=subject,
                difficulty=optimal_difficulty,
                context=context,
                exclude_attempted=self._get_attempted_questions(context.current_session)
            )
            
            # Build recommendation with reasoning
            recommendation = QuestionRecommendation(
                question=selected_question,
                difficulty=optimal_difficulty,
                skill_id=f"{subject}_{optimal_difficulty}",
                subject=subject,
                selection_reason=self._generate_selection_reasoning(
                    optimal_difficulty, strategy, current_mastery, expected_success
                ),
                confidence=self._calculate_selection_confidence(context, selected_question),
                expected_success_probability=expected_success,
                learning_objective=self._determine_learning_objective(strategy, current_mastery),
                skill_targeted=f"{subject}_{optimal_difficulty}",
                adaptation_strategy=strategy,
                next_difficulty_hint=self._predict_next_difficulty(context, expected_success),
                fallback_used=selected_question is None
            )
            
            logger.info(f"✅ Question selected: {optimal_difficulty} difficulty, {expected_success:.3f} success prob, strategy={strategy}")
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Question selection failed: {e}")
            return self._fallback_question_selection(context)
    
    def _determine_optimal_difficulty(self, context: QuestionSelectionContext) -> Tuple[str, str]:
        """
        Determine optimal difficulty using advanced adaptive logic
        """
        profile = context.student_profile
        recent_performance = context.recent_performance[-5:] if context.recent_performance else []
        
        # Base mastery from current subject
        subject = context.current_session.session_config.get('subject', 'mathematics')
        base_mastery = profile.subject_masteries.get(subject, 0.5)
        
        # Adjust based on recent performance trend
        if len(recent_performance) >= 3:
            recent_accuracy = sum(recent_performance) / len(recent_performance)
            trend_adjustment = (recent_accuracy - profile.overall_accuracy) * 0.2
            adjusted_mastery = base_mastery + trend_adjustment
        else:
            adjusted_mastery = base_mastery
        
        # Factor in learning velocity
        velocity_factor = min(0.2, max(-0.2, profile.learning_velocity))
        final_mastery = adjusted_mastery + velocity_factor
        
        # Determine strategy based on multiple factors
        strategy = self._determine_adaptation_strategy(profile, context, final_mastery)
        
        # Map strategy to difficulty
        if strategy == "advance":
            if final_mastery > 0.8:
                return "hard", strategy
            elif final_mastery > 0.6:
                return "medium", strategy
            else:
                return "medium", strategy
        elif strategy == "reinforce":
            if final_mastery < 0.3:
                return "easy", strategy
            elif final_mastery < 0.6:
                return "easy", strategy
            else:
                return "medium", strategy
        elif strategy == "challenge":
            # Deliberate challenge beyond comfort zone
            if final_mastery > 0.7:
                return "hard", strategy
            elif final_mastery > 0.4:
                return "medium", strategy
            else:
                return "medium", strategy
        elif strategy == "explore":
            # Try different difficulty for exploration
            difficulties = ["easy", "medium", "hard"]
            # Remove current comfort zone
            if final_mastery > 0.7:
                difficulties.remove("easy")
            elif final_mastery < 0.3:
                difficulties.remove("hard")
            
            return random.choice(difficulties), strategy
        else:
            # Maintain current level
            if final_mastery > 0.7:
                return "medium", strategy
            elif final_mastery > 0.3:
                return "medium", strategy
            else:
                return "easy", strategy
    
    def _determine_adaptation_strategy(self, profile: StudentPerformanceProfile, 
                                     context: QuestionSelectionContext, mastery: float) -> str:
        """
        Determine the best adaptation strategy based on student state
        """
        recent_performance = context.recent_performance[-5:] if context.recent_performance else []
        
        # Fast learner advancing quickly
        if profile.learning_velocity > self.fast_learner_threshold and mastery > 0.6:
            return "advance"
        
        # Student struggling, needs reinforcement
        if (mastery < 0.4 or 
            profile.streak_incorrect > 2 or 
            (len(recent_performance) >= 3 and sum(recent_performance) / len(recent_performance) < 0.4)):
            return "reinforce"
        
        # High mastery, ready for challenge
        if mastery > 0.8 and profile.consistency_score > 0.7:
            if random.random() < context.challenge_rate:
                return "challenge"
            else:
                return "advance"
        
        # Exploration for variety
        if (profile.total_questions_attempted > 20 and 
            profile.consistency_score > 0.6 and 
            random.random() < context.exploration_rate):
            return "explore"
        
        # Review easier concepts occasionally
        if (mastery > 0.6 and 
            random.random() < context.review_rate and 
            context.questions_completed > 3):
            return "reinforce"
        
        # Default: maintain current level
        return "maintain"
    
    def _get_current_mastery(self, student: User, subject: str, context: QuestionSelectionContext) -> float:
        """
        Get comprehensive current mastery using BKT/DKT orchestration
        """
        try:
            # Try orchestrated approach first
            skill_id = f"{subject}_adaptive"
            
            orchestrated_state = self.orchestration_service.get_comprehensive_knowledge_state(
                student=student,
                subject=subject,
                skill_id=skill_id
            )
            
            if orchestrated_state and 'bkt_mastery' in orchestrated_state:
                bkt_mastery = orchestrated_state['bkt_mastery']
                dkt_prediction = orchestrated_state.get('dkt_prediction', 0.5)
                combined_confidence = orchestrated_state.get('combined_confidence', 0.5)
                
                # Weighted combination favoring more reliable prediction
                if combined_confidence > 0.7:
                    return (bkt_mastery * 0.7) + (dkt_prediction * 0.3)
                else:
                    return (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
            # Fallback to individual services
            bkt_params = self.bkt_service.get_skill_bkt_params(student, skill_id)
            bkt_mastery = bkt_params.P_L if bkt_params else 0.5
            
            dkt_prediction = self.dkt_service.get_skill_prediction(student, skill_id)
            
            return (bkt_mastery * 0.6) + (dkt_prediction * 0.4)
            
        except Exception as e:
            logger.warning(f"⚠️ Mastery calculation failed, using profile data: {e}")
            subject_mastery = context.student_profile.subject_masteries.get(subject, 0.5)
            return subject_mastery
    
    def _calculate_expected_success(self, mastery: float, difficulty: str, 
                                  context: QuestionSelectionContext) -> float:
        """
        Calculate expected success probability for given mastery and difficulty
        """
        # Base success probability from mastery
        base_success = mastery
        
        # Adjust based on difficulty
        difficulty_adjustments = {
            "easy": 0.3,      # Easier questions boost success rate
            "medium": 0.0,    # No adjustment
            "hard": -0.2      # Harder questions reduce success rate
        }
        
        difficulty_adjustment = difficulty_adjustments.get(difficulty, 0.0)
        adjusted_success = base_success + difficulty_adjustment
        
        # Factor in student's response time (faster = more confident)
        avg_response_time = context.student_profile.average_response_time
        if avg_response_time > 0:
            # Normalize response time (30s as baseline)
            time_factor = min(0.1, max(-0.1, (30 - avg_response_time) / 300))
            adjusted_success += time_factor
        
        # Factor in consistency
        consistency_bonus = (context.student_profile.consistency_score - 0.5) * 0.1
        adjusted_success += consistency_bonus
        
        # Factor in recent trend
        trend_factor = context.student_profile.recent_accuracy_trend * 0.15
        adjusted_success += trend_factor
        
        # Clamp to reasonable bounds
        return max(0.1, min(0.95, adjusted_success))
    
    def _select_question_from_pool(self, subject: str, difficulty: str, 
                                 context: QuestionSelectionContext,
                                 exclude_attempted: List[int]) -> Optional[AdaptiveQuestion]:
        """
        Select best question from available pool
        """
        try:
            # Map difficulty to database values
            db_difficulty_mapping = {
                "easy": "easy",
                "medium": "moderate", 
                "hard": "difficult"
            }
            
            db_difficulty = db_difficulty_mapping.get(difficulty, "moderate")
            
            # Get subject mapping
            subject_mapping = {
                'mathematics': 'quantitative_aptitude',
                'quantitative_aptitude': 'quantitative_aptitude',
                'logical_reasoning': 'logical_reasoning',
                'data_interpretation': 'data_interpretation', 
                'verbal_ability': 'verbal_ability'
            }
            
            db_subject = subject_mapping.get(subject.lower(), 'quantitative_aptitude')
            
            # Build query
            questions = AdaptiveQuestion.objects.filter(
                subject_code=db_subject,
                difficulty=db_difficulty
            )
            
            # Exclude already attempted questions
            if exclude_attempted:
                questions = questions.exclude(id__in=exclude_attempted)
            
            # Prioritize questions from different chapters for variety
            attempted_chapters = self._get_attempted_chapters(context.current_session)
            available_questions = list(questions.order_by('?'))  # Random order
            
            # First try to find question from unvisited chapter
            for question in available_questions:
                chapter_name = question.chapter.name if question.chapter else "Unknown"
                if chapter_name not in attempted_chapters:
                    logger.info(f"📚 Selected question from new chapter: {chapter_name}")
                    return question
            
            # If all chapters visited, just return first available
            if available_questions:
                selected = available_questions[0]
                chapter_name = selected.chapter.name if selected.chapter else "Unknown"
                logger.info(f"🔄 Selected question from visited chapter: {chapter_name}")
                return selected
            
            logger.warning(f"⚠️ No questions found for {db_subject} at {db_difficulty} difficulty")
            return None
            
        except Exception as e:
            logger.error(f"❌ Question selection from pool failed: {e}")
            return None
    
    def _get_attempted_questions(self, session: StudentSession) -> List[int]:
        """Get list of already attempted question IDs"""
        return list(QuestionAttempt.objects.filter(
            session=session
        ).values_list('question_id', flat=True))
    
    def _get_attempted_chapters(self, session: StudentSession) -> List[str]:
        """Get list of chapters already attempted in this session"""
        attempts = QuestionAttempt.objects.filter(session=session).select_related('question__chapter')
        chapters = set()
        for attempt in attempts:
            if attempt.question and attempt.question.chapter:
                chapters.add(attempt.question.chapter.name)
        return list(chapters)
    
    def _generate_selection_reasoning(self, difficulty: str, strategy: str, 
                                    mastery: float, expected_success: float) -> str:
        """Generate human-readable reasoning for question selection"""
        
        reasoning_templates = {
            "advance": f"🚀 Advancing to {difficulty} questions as you've shown good mastery ({mastery:.1%}). Expected success: {expected_success:.1%}",
            "reinforce": f"💪 Reinforcing with {difficulty} questions to build confidence. Current mastery: {mastery:.1%}",
            "challenge": f"🎯 Challenging you with {difficulty} questions to accelerate learning. Ready for the challenge!",
            "explore": f"🔍 Exploring {difficulty} questions to assess your capabilities across different areas",
            "maintain": f"📊 Maintaining {difficulty} level based on current performance ({mastery:.1%})",
        }
        
        return reasoning_templates.get(strategy, f"Selected {difficulty} question based on current knowledge state")
    
    def _calculate_selection_confidence(self, context: QuestionSelectionContext, 
                                      question: Optional[AdaptiveQuestion]) -> float:
        """Calculate confidence in the selection decision"""
        confidence = 0.5
        
        # Higher confidence with more data
        if context.student_profile.total_questions_attempted > 50:
            confidence += 0.2
        elif context.student_profile.total_questions_attempted > 20:
            confidence += 0.1
        
        # Higher confidence with consistent performance
        confidence += context.student_profile.consistency_score * 0.2
        
        # Higher confidence if we found a good question
        if question is not None:
            confidence += 0.2
        
        # Higher confidence if profile is recent
        if (timezone.now() - context.student_profile.last_updated).days < 1:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _determine_learning_objective(self, strategy: str, mastery: float) -> str:
        """Determine learning objective based on strategy"""
        objectives = {
            "advance": "Advance to more challenging concepts",
            "reinforce": "Strengthen foundational understanding",
            "challenge": "Push beyond comfort zone",
            "explore": "Assess capabilities across different areas",
            "maintain": "Continue building proficiency at current level"
        }
        return objectives.get(strategy, "Improve overall understanding")
    
    def _predict_next_difficulty(self, context: QuestionSelectionContext, 
                               expected_success: float) -> str:
        """Predict what difficulty should come next based on expected success"""
        if expected_success > 0.8:
            return "harder"
        elif expected_success < 0.5:
            return "easier"
        else:
            return "similar"
    
    def _fallback_question_selection(self, context: QuestionSelectionContext) -> QuestionRecommendation:
        """Fallback question selection when main algorithm fails"""
        logger.warning("⚠️ Using fallback question selection")
        
        # Simple fallback based on overall accuracy
        if context.student_profile.overall_accuracy > 0.7:
            difficulty = "medium"
        elif context.student_profile.overall_accuracy > 0.4:
            difficulty = "medium"
        else:
            difficulty = "easy"
        
        return QuestionRecommendation(
            question=None,
            difficulty=difficulty,
            selection_reason="Fallback selection due to system error",
            confidence=0.3,
            expected_success_probability=0.5,
            learning_objective="Continue learning",
            adaptation_strategy="maintain",
            fallback_used=True
        )
    
    # ========================================================================
    # Integration Methods
    # ========================================================================
    
    def get_enhanced_question_for_session(self, session_id: str) -> Dict[str, Any]:
        """
        Main integration method for getting enhanced adaptive question
        """
        try:
            # Get session
            session = StudentSession.objects.get(id=session_id)
            student = session.student
            
            # Build student profile
            student_profile = self.build_student_performance_profile(student)
            
            # Build selection context
            questions_completed = QuestionAttempt.objects.filter(session=session).count()
            recent_attempts = QuestionAttempt.objects.filter(session=session).order_by('-created_at')[:5]
            recent_performance = [attempt.is_correct for attempt in recent_attempts]
            
            context = QuestionSelectionContext(
                student_profile=student_profile,
                current_session=session,
                questions_completed=questions_completed,
                recent_performance=recent_performance,
                remaining_questions=max(0, session.total_questions_planned - questions_completed)
            )
            
            # Select optimal question
            recommendation = self.select_optimal_question(context)
            
            # Format response
            if recommendation.question:
                # Real question from database
                question_data = {
                    'success': True,
                    'question_id': f"enhanced_{recommendation.question.id}",
                    'real_question_id': recommendation.question.id,
                    'session_id': session_id,
                    'question_number': questions_completed + 1,
                    'subject': recommendation.subject,
                    'difficulty': recommendation.difficulty,
                    'question_text': recommendation.question.question_text,
                    'options': [
                        {'id': 'A', 'text': recommendation.question.option_a},
                        {'id': 'B', 'text': recommendation.question.option_b},
                        {'id': 'C', 'text': recommendation.question.option_c},
                        {'id': 'D', 'text': recommendation.question.option_d}
                    ],
                    'correct_answer': recommendation.question.correct_answer.upper(),
                    'explanation': recommendation.selection_reason,
                    'chapter': recommendation.question.chapter.name if recommendation.question.chapter else 'General',
                    'enhanced_adaptive_info': {
                        'selection_confidence': recommendation.confidence,
                        'expected_success_probability': recommendation.expected_success_probability,
                        'learning_objective': recommendation.learning_objective,
                        'adaptation_strategy': recommendation.adaptation_strategy,
                        'next_difficulty_hint': recommendation.next_difficulty_hint,
                        'student_mastery': student_profile.subject_masteries.get(recommendation.subject, 0.5),
                        'learning_velocity': student_profile.learning_velocity,
                        'consistency_score': student_profile.consistency_score
                    }
                }
            else:
                # Fallback mock question
                question_data = {
                    'success': True,
                    'question_id': f"enhanced_mock_{session_id}_{questions_completed + 1}",
                    'session_id': session_id,
                    'question_number': questions_completed + 1,
                    'subject': recommendation.subject,
                    'difficulty': recommendation.difficulty,
                    'question_text': f"Enhanced adaptive {recommendation.difficulty} question for {recommendation.subject}",
                    'options': [
                        {'id': 'A', 'text': 'Option A'},
                        {'id': 'B', 'text': 'Option B'},
                        {'id': 'C', 'text': 'Option C'},
                        {'id': 'D', 'text': 'Option D'}
                    ],
                    'correct_answer': 'A',
                    'explanation': recommendation.selection_reason,
                    'chapter': 'Mock Chapter',
                    'enhanced_adaptive_info': {
                        'fallback_used': True,
                        'selection_confidence': recommendation.confidence,
                        'learning_objective': recommendation.learning_objective,
                        'adaptation_strategy': recommendation.adaptation_strategy
                    }
                }
            
            logger.info(f"✅ Enhanced question delivered: {recommendation.difficulty} difficulty, {recommendation.adaptation_strategy} strategy")
            return question_data
            
        except Exception as e:
            logger.error(f"❌ Enhanced question selection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Enhanced adaptive system failed, please try again'
            }

# ============================================================================
# Singleton Instance
# ============================================================================

# Create enhanced adaptive engine instance
enhanced_adaptive_engine = EnhancedAdaptiveEngine()

# ============================================================================
# Integration Function for simple_frontend_api.py
# ============================================================================

def get_enhanced_adaptive_question(session_id: str) -> Dict[str, Any]:
    """
    Drop-in replacement function for enhanced adaptive question selection
    
    This can be used in simple_frontend_api.py as an enhanced alternative
    to the current get_simple_question logic.
    """
    return enhanced_adaptive_engine.get_enhanced_question_for_session(session_id)