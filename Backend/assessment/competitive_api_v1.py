"""
Competitive Exam API v1 - Level-locked progression system
Handles subject-specific assessments with BKT mastery requirements
"""

from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import logging
import uuid
from django.db import transaction
from django.utils import timezone
import json

logger = logging.getLogger(__name__)

router = Router()

# ============================================================================
# API v1 Schemas for Competitive Exam System
# ============================================================================

class SubjectSchema(Schema):
    """Subject information schema"""
    subject_code: str
    subject_name: str  
    total_questions: int
    difficulty_breakdown: Dict[str, int]
    
class SubjectListResponseSchema(Schema):
    """Response schema for subjects list"""
    success: bool
    total_subjects: int
    subjects: List[SubjectSchema]

class StartSubjectAssessmentSchema(Schema):
    """Schema for starting assessment in a specific subject"""
    student_id: str
    subject: str
    preferred_difficulty: Optional[str] = None

class StartAssessmentResponseSchema(Schema):
    """Response schema for starting subject assessment"""
    success: bool
    assessment_id: str
    subject: str
    current_difficulty: str
    student_level: int
    unlocked_levels: List[str]
    next_question: Optional[Dict[str, Any]]
    
class CompetitiveSubmitAnswerSchema(Schema):
    """Enhanced schema for competitive exam answer submission"""
    student_id: str
    assessment_id: str
    question_id: str
    answer: str
    response_time: float
    subject: str
    current_difficulty: str

class LevelProgressionSchema(Schema):
    """Level progression information"""
    level_unlocked: bool
    previous_level: str
    new_level: Optional[str]
    consecutive_correct: int
    mastery_score: float
    mastery_threshold: float
    congratulations_message: Optional[str]

class SubmitAnswerResponseSchema(Schema):
    """Enhanced response for competitive exam submission"""
    success: bool
    was_correct: bool
    correct_answer: str
    explanation: Optional[str]
    mastery_score: float
    consecutive_correct: int
    level_progression: LevelProgressionSchema
    next_question: Optional[Dict[str, Any]]
    recommendations: List[str]

class SubjectProgressSchema(Schema):
    """Progress in a specific subject"""
    subject: str
    current_difficulty: str
    level: int
    questions_attempted: int
    questions_correct: int
    accuracy_rate: float
    mastery_score: float
    unlocked_difficulties: List[str]
    time_spent_minutes: float

class StudentProgressResponseSchema(Schema):
    """Complete student progress across all subjects"""
    success: bool
    student_id: str
    overall_stats: Dict[str, Any]
    subject_progress: List[SubjectProgressSchema]
    achievements: List[str]

# ============================================================================
# API v1 Endpoints - Competitive Exam Flow
# ============================================================================

@router.get("/v1/subjects", response=SubjectListResponseSchema)
def get_subjects_v1(request):
    """
    Get all available subjects with question counts and difficulty breakdown.
    Returns structured data for competitive exam subject selection.
    """
    try:
        from assessment.models import AdaptiveQuestion
        from django.db.models import Count
        
        # Get subjects with detailed breakdown
        subjects_data = []
        subject_codes = ['quantitative_aptitude', 'logical_reasoning', 'data_interpretation', 'verbal_ability']
        
        for subject_code in subject_codes:
            questions = AdaptiveQuestion.objects.filter(subject=subject_code, is_active=True)
            
            if questions.exists():
                # Get difficulty breakdown
                difficulty_breakdown = {}
                for difficulty in ['very_easy', 'easy', 'moderate', 'difficult']:
                    count = questions.filter(difficulty_level=difficulty).count()
                    if count > 0:
                        difficulty_breakdown[difficulty] = count
                
                subjects_data.append(SubjectSchema(
                    subject_code=subject_code,
                    subject_name=subject_code.replace('_', ' ').title(),
                    total_questions=questions.count(),
                    difficulty_breakdown=difficulty_breakdown
                ))
        
        return SubjectListResponseSchema(
            success=True,
            total_subjects=len(subjects_data),
            subjects=subjects_data
        )
        
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        raise HttpError(500, f"Failed to retrieve subjects: {str(e)}")

@router.post("/v1/assessment/start-subject", response=StartAssessmentResponseSchema)
def start_subject_assessment(request, payload: StartSubjectAssessmentSchema):
    """
    Start assessment in a specific subject. Creates assessment session and 
    returns first question based on student's current level in that subject.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion
        
        # Get student profile - try both User ID and StudentProfile ID
        student_profile = None
        try:
            # First try as StudentProfile ID
            student_profile = StudentProfile.objects.get(id=payload.student_id)
        except StudentProfile.DoesNotExist:
            try:
                # Then try as User ID and get/create StudentProfile
                from django.contrib.auth.models import User
                user = User.objects.get(id=payload.student_id)
                student_profile, created = StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f'student_{user.id}',
                        'name': user.username or f'Student {user.id}',
                        'subject_progress': {}
                    }
                )
            except User.DoesNotExist:
                raise HttpError(404, f"Student {payload.student_id} not found")
        
        # Get or create subject-specific progress
        subject_progress = student_profile.subject_progress.get(payload.subject, {
            'current_difficulty': 'very_easy',
            'level': 1,
            'mastery_score': 0.0,
            'consecutive_correct': 0,
            'questions_attempted': 0,
            'questions_correct': 0,
            'unlocked_difficulties': ['very_easy']
        })
        
        # Update subject progress in student profile
        if payload.subject not in student_profile.subject_progress:
            student_profile.subject_progress[payload.subject] = subject_progress
            student_profile.save()
        
        # Determine current difficulty level
        current_difficulty = payload.preferred_difficulty or subject_progress['current_difficulty']
        
        # Validate difficulty is unlocked
        if current_difficulty not in subject_progress['unlocked_difficulties']:
            current_difficulty = subject_progress['current_difficulty']
        
        # Generate assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Use adaptive question selection based on BKT/DKT analysis
        from .adaptive_question_selector import adaptive_selector
        
        # Create a mock session for adaptive selection
        mock_session = type('MockSession', (), {
            'student': student_profile.user,
            'subject_code': payload.subject,
            'assessment_type': 'COMPETITIVE'
        })()
        
        # Get adaptive question selection
        selected_questions = adaptive_selector.select_questions(
            user=student_profile.user,
            subject_code=payload.subject,
            chapter_id=None,  # Competitive exams aren't chapter-specific
            question_count=1,
            assessment_type='COMPETITIVE',
            session=mock_session
        )
        
        next_question = None
        if selected_questions:
            question_data = selected_questions[0]
            next_question = {
                "id": question_data['id'],
                "question_text": question_data['question_text'],
                "options": question_data['options'],
                "difficulty": question_data.get('difficulty', current_difficulty),
                "estimated_time": question_data.get('estimated_time', 60),
                "question_number": subject_progress['questions_attempted'] + 1,
                "adaptive_info": {
                    "selection_algorithm": question_data.get('selection_algorithm', 'adaptive'),
                    "target_skills": question_data.get('target_skills', []),
                    "selection_confidence": question_data.get('adaptive_metadata', {}).get('recommendation_confidence', 0.5)
                }
            }
        else:
            # Fallback to difficulty-based selection if adaptive fails
            available_questions = AdaptiveQuestion.objects.filter(
                subject=payload.subject,
                difficulty_level=current_difficulty,
                is_active=True
            ).order_by('?')[:1]
            
            if available_questions:
                question = available_questions[0]
                next_question = {
                    "id": str(question.id),
                    "question_text": question.question_text,
                    "options": question.formatted_options,
                    "difficulty": current_difficulty,
                    "estimated_time": question.estimated_time_seconds,
                    "question_number": subject_progress['questions_attempted'] + 1,
                    "adaptive_info": {
                        "selection_algorithm": "fallback_random",
                        "reason": "adaptive_selection_failed"
                    }
                }
        
        return StartAssessmentResponseSchema(
            success=True,
            assessment_id=assessment_id,
            subject=payload.subject,
            current_difficulty=current_difficulty,
            student_level=subject_progress['level'],
            unlocked_levels=subject_progress['unlocked_difficulties'],
            next_question=next_question
        )
        
    except Exception as e:
        logger.error(f"Error starting subject assessment: {e}")
        raise HttpError(500, f"Failed to start assessment: {str(e)}")

@router.post("/v1/assessment/submit-answer", response=SubmitAnswerResponseSchema)
def submit_competitive_answer(request, payload: CompetitiveSubmitAnswerSchema):
    """
    Submit answer for competitive exam with level-locked progression.
    Handles BKT mastery checking and level unlocking logic.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, Interaction
        from student_model.bkt import BKTService
        
        with transaction.atomic():
            # Get student and question - handle both User ID and StudentProfile ID
            try:
                # First try as StudentProfile ID
                student_profile = StudentProfile.objects.get(id=payload.student_id)
            except StudentProfile.DoesNotExist:
                try:
                    # Then try as User ID
                    from django.contrib.auth.models import User
                    user = User.objects.get(id=payload.student_id)
                    student_profile, created = StudentProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'student_id': f'student_{user.id}',
                            'name': user.username or f'Student {user.id}',
                            'subject_progress': {}
                        }
                    )
                except User.DoesNotExist:
                    raise HttpError(404, f"Student {payload.student_id} not found")
            
            try:
                question = AdaptiveQuestion.objects.get(id=payload.question_id)
            except (StudentProfile.DoesNotExist, AdaptiveQuestion.DoesNotExist) as e:
                raise HttpError(404, str(e))
            
            # Check if answer is correct
            is_correct = payload.answer.lower() == question.answer.lower()
            correct_answer = f"{question.answer.upper()}: {question.formatted_options[question.answer]}"
            
            # Create interaction record
            interaction = Interaction.objects.create(
                student=student_profile.user,
                question=question,
                student_answer=payload.answer,
                is_correct=is_correct,
                response_time=payload.response_time,
                session_id=payload.assessment_id,  # Use assessment_id as session_id
                attempt_number=1
            )
            
            # Update BKT for this subject-difficulty combination
            skill_id = f"{payload.subject}_{payload.current_difficulty}"
            updated_bkt_params, bkt_progression = BKTService.update_skill_bkt_with_progression(
                user=student_profile.user,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={
                    'question_id': str(question.id),
                    'response_time': payload.response_time,
                    'subject': payload.subject,
                    'difficulty': payload.current_difficulty,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Update DKT knowledge state
            try:
                from student_model.api import dkt_client
                from .adaptive_question_selector import adaptive_selector
                
                # Map question to DKT skill ID
                dkt_skill_id = adaptive_selector._map_question_to_skill_id(question)
                
                # Update DKT asynchronously (non-blocking)
                dkt_update_data = {
                    'student_id': str(student_profile.id),
                    'skill_id': dkt_skill_id,
                    'is_correct': is_correct,
                    'response_time': payload.response_time
                }
                
                # Call DKT update in background
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Non-blocking DKT update
                loop.run_in_executor(
                    None,
                    lambda: dkt_client.infer_dkt_sync(
                        adaptive_selector._build_interaction_sequence(student_profile.user),
                        str(student_profile.id)
                    )
                )
                
                logger.info(f"DKT update initiated for student {student_profile.id}, skill {dkt_skill_id}")
                
            except Exception as dkt_error:
                logger.warning(f"DKT update failed (non-critical): {dkt_error}")
                # Continue execution - DKT failure shouldn't break the flow
            
            # Get/update subject progress
            subject_progress = student_profile.subject_progress.get(payload.subject, {
                'current_difficulty': 'very_easy',
                'level': 1,
                'mastery_score': 0.0,
                'consecutive_correct': 0,
                'questions_attempted': 0,
                'questions_correct': 0,
                'unlocked_difficulties': ['very_easy']
            })
            
            # Update subject statistics
            subject_progress['questions_attempted'] += 1
            if is_correct:
                subject_progress['questions_correct'] += 1
                subject_progress['consecutive_correct'] += 1
            else:
                subject_progress['consecutive_correct'] = 0
            
            # Update mastery score from BKT
            subject_progress['mastery_score'] = updated_bkt_params.P_L
            
            # Check for level progression
            level_progression = check_level_progression(
                subject_progress, 
                payload.current_difficulty,
                updated_bkt_params.P_L,
                is_correct
            )
            
            # Apply level progression if unlocked
            if level_progression['level_unlocked']:
                new_difficulty = level_progression['new_level']
                subject_progress['current_difficulty'] = new_difficulty
                subject_progress['level'] = get_level_from_difficulty(new_difficulty)
                
                # Ensure unlocked_difficulties is a list
                if 'unlocked_difficulties' not in subject_progress:
                    subject_progress['unlocked_difficulties'] = ['very_easy']
                elif not isinstance(subject_progress['unlocked_difficulties'], list):
                    subject_progress['unlocked_difficulties'] = ['very_easy']
                
                if new_difficulty not in subject_progress['unlocked_difficulties']:
                    subject_progress['unlocked_difficulties'].append(new_difficulty)
                subject_progress['consecutive_correct'] = 0  # Reset for new level
            
            # Save updated progress
            student_profile.subject_progress[payload.subject] = subject_progress
            student_profile.save()
            
            # Get next question
            next_question = get_next_competitive_question(
                payload.subject,
                subject_progress['current_difficulty'],
                student_profile
            )
            
            # Generate recommendations
            recommendations = generate_competitive_recommendations(
                subject_progress,
                level_progression,
                is_correct
            )
            
            return SubmitAnswerResponseSchema(
                success=True,
                was_correct=is_correct,
                correct_answer=correct_answer,
                explanation=f"The correct answer is {correct_answer}",
                mastery_score=subject_progress['mastery_score'],
                consecutive_correct=subject_progress['consecutive_correct'],
                level_progression=LevelProgressionSchema(
                    level_unlocked=level_progression['level_unlocked'],
                    previous_level=level_progression['previous_level'],
                    new_level=level_progression['new_level'],
                    consecutive_correct=subject_progress['consecutive_correct'],
                    mastery_score=subject_progress['mastery_score'],
                    mastery_threshold=level_progression['mastery_threshold'],
                    congratulations_message=level_progression['congratulations_message']
                ),
                next_question=next_question,
                recommendations=recommendations
            )
            
    except Exception as e:
        logger.error(f"Error submitting competitive answer: {e}")
        raise HttpError(500, f"Failed to submit answer: {str(e)}")

@router.get("/v1/student/{student_id}/progress", response=StudentProgressResponseSchema)
def get_student_progress(request, student_id: str):
    """
    Get comprehensive student progress across all subjects.
    Shows current level, mastery, and statistics for each subject.
    """
    try:
        from core.models import StudentProfile
        from assessment.models import Interaction
        from django.db.models import Count, Avg
        
        # Get student profile
        try:
            student_profile = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            raise HttpError(404, f"Student {student_id} not found")
        
        # Calculate overall statistics
        total_interactions = Interaction.objects.filter(student=student_profile.user).count()
        correct_interactions = Interaction.objects.filter(
            student=student_profile.user, 
            is_correct=True
        ).count()
        
        overall_accuracy = correct_interactions / total_interactions if total_interactions > 0 else 0
        avg_response_time = Interaction.objects.filter(
            student=student_profile.user
        ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
        
        overall_stats = {
            'total_questions_attempted': total_interactions,
            'total_correct': correct_interactions,
            'overall_accuracy': overall_accuracy,
            'average_response_time': avg_response_time,
            'subjects_started': len(student_profile.subject_progress or {})
        }
        
        # Get progress for each subject
        subject_progress_list = []
        subjects = ['quantitative_aptitude', 'logical_reasoning', 'data_interpretation', 'verbal_ability']
        
        for subject in subjects:
            progress_data = student_profile.subject_progress.get(subject, {
                'current_difficulty': 'very_easy',
                'level': 1,
                'mastery_score': 0.0,
                'consecutive_correct': 0,
                'questions_attempted': 0,
                'questions_correct': 0,
                'unlocked_difficulties': ['very_easy']
            })
            
            # Get time spent in this subject
            subject_interactions = Interaction.objects.filter(
                student=student_profile.user,
                question__subject=subject
            )
            
            total_time = sum(
                interaction.response_time for interaction in subject_interactions
                if interaction.response_time
            ) / 60  # Convert to minutes
            
            accuracy = (progress_data['questions_correct'] / progress_data['questions_attempted'] 
                       if progress_data['questions_attempted'] > 0 else 0)
            
            subject_progress_list.append(SubjectProgressSchema(
                subject=subject,
                current_difficulty=progress_data['current_difficulty'],
                level=progress_data['level'],
                questions_attempted=progress_data['questions_attempted'],
                questions_correct=progress_data['questions_correct'],
                accuracy_rate=accuracy,
                mastery_score=progress_data['mastery_score'],
                unlocked_difficulties=progress_data['unlocked_difficulties'],
                time_spent_minutes=total_time
            ))
        
        # Generate achievements
        achievements = generate_achievements(student_profile, subject_progress_list)
        
        return StudentProgressResponseSchema(
            success=True,
            student_id=student_id,
            overall_stats=overall_stats,
            subject_progress=subject_progress_list,
            achievements=achievements
        )
        
    except Exception as e:
        logger.error(f"Error getting student progress: {e}")
        raise HttpError(500, f"Failed to get progress: {str(e)}")

# ============================================================================
# Helper Functions
# ============================================================================

def check_level_progression(subject_progress, current_difficulty, mastery_score, is_correct):
    """
    Check if student should progress to next difficulty level.
    Requires: BKT mastery ≥ threshold + 3 consecutive correct answers
    """
    # Mastery thresholds by difficulty
    mastery_thresholds = {
        'very_easy': 0.7,
        'easy': 0.75,
        'moderate': 0.8,
        'difficult': 0.85
    }
    
    # Difficulty progression order
    difficulty_progression = {
        'very_easy': 'easy',
        'easy': 'moderate', 
        'moderate': 'difficult',
        'difficult': None  # Max level
    }
    
    current_threshold = mastery_thresholds.get(current_difficulty, 0.8)
    next_difficulty = difficulty_progression.get(current_difficulty)
    
    # Check progression criteria
    meets_mastery = mastery_score >= current_threshold
    meets_consecutive = subject_progress['consecutive_correct'] >= 3
    has_next_level = next_difficulty is not None
    
    level_unlocked = meets_mastery and meets_consecutive and has_next_level and is_correct
    
    congratulations_message = None
    if level_unlocked:
        congratulations_message = (
            f"🎉 Congratulations! You've unlocked {next_difficulty.replace('_', ' ').title()} level! "
            f"Mastery: {mastery_score:.1%}, Consecutive Correct: {subject_progress['consecutive_correct']}"
        )
    
    return {
        'level_unlocked': level_unlocked,
        'previous_level': current_difficulty,
        'new_level': next_difficulty if level_unlocked else None,
        'mastery_threshold': current_threshold,
        'congratulations_message': congratulations_message
    }

def get_level_from_difficulty(difficulty):
    """Map difficulty to numeric level"""
    level_map = {
        'very_easy': 1,
        'easy': 2,
        'moderate': 3,
        'difficult': 4
    }
    return level_map.get(difficulty, 1)

def get_next_competitive_question(subject, difficulty, student_profile):
    """Get next question for competitive exam"""
    from assessment.models import AdaptiveQuestion, Interaction
    
    # Get questions student hasn't answered recently
    recent_questions = Interaction.objects.filter(
        student=student_profile.user,
        question__subject=subject,
        question__difficulty_level=difficulty
    ).order_by('-timestamp')[:10].values_list('question_id', flat=True)
    
    available_questions = AdaptiveQuestion.objects.filter(
        subject=subject,
        difficulty_level=difficulty,
        is_active=True
    ).exclude(id__in=recent_questions).order_by('?')[:1]
    
    if available_questions:
        question = available_questions[0]
        return {
            "id": str(question.id),
            "question_text": question.question_text,
            "options": question.formatted_options,
            "difficulty": difficulty,
            "estimated_time": question.estimated_time_seconds
        }
    
    return None

def generate_competitive_recommendations(subject_progress, level_progression, is_correct):
    """Generate recommendations for competitive exam"""
    recommendations = []
    
    if level_progression['level_unlocked']:
        recommendations.append(f"Great job! You've unlocked the next difficulty level.")
    
    if not is_correct:
        if subject_progress['consecutive_correct'] == 0:
            recommendations.append("Take your time and read questions carefully.")
        else:
            recommendations.append("You're doing well! Keep practicing to maintain your streak.")
    
    mastery = subject_progress['mastery_score']
    if mastery < 0.6:
        recommendations.append("Focus on fundamentals. Review basic concepts for this topic.")
    elif mastery < 0.8:
        recommendations.append("You're making good progress. Keep practicing similar questions.")
    else:
        recommendations.append("Excellent mastery! Ready to tackle more challenging questions.")
    
    return recommendations

def generate_achievements(student_profile, subject_progress_list):
    """Generate achievement badges for student"""
    achievements = []
    
    # Subject-based achievements
    for progress in subject_progress_list:
        if progress.questions_attempted >= 10:
            achievements.append(f"Explorer: {progress.subject.replace('_', ' ').title()}")
        
        if progress.accuracy_rate >= 0.9:
            achievements.append(f"Accuracy Master: {progress.subject.replace('_', ' ').title()}")
        
        if progress.level >= 4:
            achievements.append(f"Subject Master: {progress.subject.replace('_', ' ').title()}")
    
    # Overall achievements
    total_attempted = sum(p.questions_attempted for p in subject_progress_list)
    if total_attempted >= 50:
        achievements.append("Question Marathoner")
    
    unlocked_subjects = sum(1 for p in subject_progress_list if len(p.unlocked_difficulties) > 1)
    if unlocked_subjects >= 2:
        achievements.append("Multi-Subject Learner")
    
    return achievements


@router.get("/leaderboard")
def get_leaderboard(request, limit: int = 10):
    """Get competitive exam leaderboard"""
    # Return mock leaderboard data
    return {
        "leaderboard": [
            {
                "rank": 1,
                "student_id": "student-001",
                "username": "TopLearner",
                "total_score": 2850,
                "subjects_mastered": 5,
                "accuracy_rate": 0.94,
                "achievements": ["Math Master", "Science Expert", "Question Marathoner"]
            },
            {
                "rank": 2,
                "student_id": "student-002", 
                "username": "StudyHero",
                "total_score": 2720,
                "subjects_mastered": 4,
                "accuracy_rate": 0.91,
                "achievements": ["Physics Pro", "Chemistry Champion"]
            },
            {
                "rank": 3,
                "student_id": "student-003",
                "username": "BrainAce",
                "total_score": 2580,
                "subjects_mastered": 3,
                "accuracy_rate": 0.89,
                "achievements": ["Biology Expert", "Multi-Subject Learner"]
            }
        ],
        "total_participants": 156,
        "generated_at": datetime.now().isoformat()
    }