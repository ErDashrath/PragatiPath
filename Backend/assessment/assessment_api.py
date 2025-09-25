"""
Complete Assessment API for Multi-Student System
Handles assessment creation, question delivery, answer submission, and result generation
"""

from ninja import NinjaAPI, Schema, Router
from ninja.responses import Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.db import transaction
import uuid
import json

from .models import AdaptiveQuestion
from .improved_models import (
    Subject, Chapter, StudentSession, QuestionAttempt, 
    StudentProgress, DailyStudyStats
)

# Router for assessment endpoints
assessment_router = Router()

# ============================================================================
# SCHEMAS FOR API REQUEST/RESPONSE
# ============================================================================

class AssessmentStartRequest(Schema):
    student_username: str
    subject_code: str
    chapter_id: Optional[int] = None
    assessment_type: str = "PRACTICE"  # PRACTICE, TEST, EXAM
    question_count: int = 10
    time_limit_minutes: Optional[int] = None

class AssessmentStartResponse(Schema):
    assessment_id: str
    student_username: str
    subject_name: str
    chapter_name: Optional[str]
    question_count: int
    time_limit_minutes: Optional[int]
    status: str
    created_at: datetime

class QuestionResponse(Schema):
    question_id: str
    question_number: int
    question_text: str
    question_type: str
    options: Dict[str, str]
    estimated_time_seconds: int
    topic: str
    subtopic: str
    difficulty_level: str

class AssessmentQuestionsResponse(Schema):
    assessment_id: str
    questions: List[QuestionResponse]
    current_question_number: int
    total_questions: int
    time_remaining_minutes: Optional[float]

class AnswerSubmissionRequest(Schema):
    assessment_id: str
    question_id: str
    selected_answer: str  # a, b, c, d
    time_taken_seconds: int
    confidence_level: Optional[int] = 3  # 1-5 scale

class AnswerSubmissionResponse(Schema):
    success: bool
    question_number: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    points_earned: int
    next_question_available: bool

class AssessmentResultRequest(Schema):
    assessment_id: str

class QuestionResult(Schema):
    question_id: str
    question_text: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    time_taken_seconds: int
    points_earned: int
    topic: str
    difficulty_level: str

class AssessmentResultResponse(Schema):
    assessment_id: str
    student_username: str
    subject_name: str
    chapter_name: Optional[str]
    total_questions: int
    questions_attempted: int
    questions_correct: int
    accuracy_percentage: float
    total_time_seconds: int
    total_points_earned: int
    max_possible_points: int
    grade: str
    performance_analysis: Dict[str, Any]
    question_results: List[QuestionResult]
    completion_time: datetime

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_or_create_student(username: str) -> User:
    """Get or create a student user"""
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': username.replace('_', ' ').title(),
            'email': f"{username}@example.com"
        }
    )
    return user

def calculate_question_points(difficulty_level: str, is_correct: bool) -> int:
    """Calculate points based on difficulty and correctness"""
    base_points = {
        'very_easy': 1,
        'easy': 2,
        'moderate': 3,
        'difficult': 5
    }
    return base_points.get(difficulty_level, 2) if is_correct else 0

def calculate_grade(accuracy_percentage: float) -> str:
    """Calculate letter grade based on accuracy"""
    if accuracy_percentage >= 90:
        return 'A+'
    elif accuracy_percentage >= 80:
        return 'A'
    elif accuracy_percentage >= 70:
        return 'B+'
    elif accuracy_percentage >= 60:
        return 'B'
    elif accuracy_percentage >= 50:
        return 'C'
    else:
        return 'F'

def generate_performance_analysis(question_attempts: List[QuestionAttempt]) -> Dict[str, Any]:
    """Generate detailed performance analysis"""
    if not question_attempts:
        return {}
    
    # Group by difficulty
    difficulty_stats = {}
    topic_stats = {}
    time_analysis = {'fast_answers': 0, 'slow_answers': 0, 'average_time': 0}
    
    total_time = 0
    for attempt in question_attempts:
        question = attempt.question
        
        # Difficulty analysis
        if question.difficulty_level not in difficulty_stats:
            difficulty_stats[question.difficulty_level] = {'correct': 0, 'total': 0}
        difficulty_stats[question.difficulty_level]['total'] += 1
        if attempt.is_correct:
            difficulty_stats[question.difficulty_level]['correct'] += 1
        
        # Topic analysis
        if question.topic not in topic_stats:
            topic_stats[question.topic] = {'correct': 0, 'total': 0}
        topic_stats[question.topic]['total'] += 1
        if attempt.is_correct:
            topic_stats[question.topic]['correct'] += 1
        
        # Time analysis
        total_time += attempt.time_spent_seconds
        if attempt.time_spent_seconds < question.estimated_time_seconds * 0.8:
            time_analysis['fast_answers'] += 1
        elif attempt.time_spent_seconds > question.estimated_time_seconds * 1.2:
            time_analysis['slow_answers'] += 1
    
    time_analysis['average_time'] = total_time / len(question_attempts)
    
    # Calculate accuracy percentages
    for diff in difficulty_stats:
        stats = difficulty_stats[diff]
        stats['accuracy'] = (stats['correct'] / stats['total']) * 100
    
    for topic in topic_stats:
        stats = topic_stats[topic]
        stats['accuracy'] = (stats['correct'] / stats['total']) * 100
    
    return {
        'difficulty_breakdown': difficulty_stats,
        'topic_breakdown': topic_stats,
        'time_analysis': time_analysis,
        'strengths': [topic for topic, stats in topic_stats.items() if stats['accuracy'] >= 80],
        'improvement_areas': [topic for topic, stats in topic_stats.items() if stats['accuracy'] < 60]
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@assessment_router.post("/start", response=AssessmentStartResponse)
def start_assessment(request, data: AssessmentStartRequest):
    """Start a new assessment session for a student"""
    try:
        # Get or create student
        student = get_or_create_student(data.student_username)
        
        # Get subject
        subject = get_object_or_404(Subject, code=data.subject_code)
        
        # Get chapter if specified
        chapter = None
        if data.chapter_id:
            chapter = get_object_or_404(Chapter, id=data.chapter_id, subject=subject)
        
        # Create assessment session
        with transaction.atomic():
            session = StudentSession.objects.create(
                student=student,
                subject=subject,
                chapter=chapter,
                session_type=data.assessment_type,
                session_name=f"{data.assessment_type} - {subject.name}",
                total_questions_planned=data.question_count,
                time_limit_minutes=data.time_limit_minutes,
                status='ACTIVE',
                session_config={
                    'assessment_type': data.assessment_type,
                    'question_count': data.question_count,
                    'chapter_specific': data.chapter_id is not None
                }
            )
            
            # Use adaptive question selection based on BKT/DKT
            from .adaptive_question_selector import adaptive_selector
            
            selected_questions = adaptive_selector.select_questions(
                user=student,
                subject_code=subject.code,
                chapter_id=str(chapter.id) if chapter else None,
                question_count=data.question_count,
                assessment_type=data.assessment_type or 'ADAPTIVE',
                session=session
            )
            
            # Extract question IDs and store in session
            question_ids = [q['id'] for q in selected_questions]
            session.question_sequence = question_ids
            
            # Store adaptive metadata for analysis
            session.adaptive_metadata = {
                'selection_algorithm': selected_questions[0].get('selection_algorithm', 'adaptive') if selected_questions else 'fallback',
                'knowledge_state_snapshot': selected_questions[0].get('adaptive_metadata', {}) if selected_questions else {},
                'total_questions_selected': len(selected_questions)
            }
            session.save()
            
            questions = selected_questions
        
        return AssessmentStartResponse(
            assessment_id=str(session.id),
            student_username=student.username,
            subject_name=subject.name,
            chapter_name=chapter.name if chapter else None,
            question_count=len(questions),
            time_limit_minutes=data.time_limit_minutes,
            status=session.status,
            created_at=session.session_start_time
        )
        
    except Exception as e:
        return Response({"error": f"Failed to start assessment: {str(e)}"}, status=400)

@assessment_router.get("/questions/{assessment_id}", response=AssessmentQuestionsResponse)
def get_assessment_questions(request, assessment_id: str):
    """Get all questions for an assessment"""
    try:
        session = get_object_or_404(StudentSession, id=assessment_id)
        
        if session.status != 'ACTIVE':
            return Response({"error": "Assessment is not active"}, status=400)
        
        # Get questions based on stored sequence
        question_ids = session.question_sequence or []
        questions = []
        
        for i, q_id in enumerate(question_ids):
            try:
                question = AdaptiveQuestion.objects.get(id=q_id)
                questions.append(QuestionResponse(
                    question_id=str(question.id),
                    question_number=i + 1,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    options=question.formatted_options,
                    estimated_time_seconds=question.estimated_time_seconds,
                    topic=question.topic or '',
                    subtopic=question.subtopic or '',
                    difficulty_level=question.difficulty_level
                ))
            except AdaptiveQuestion.DoesNotExist:
                continue
        
        # Calculate time remaining
        time_remaining = None
        if session.time_limit_minutes:
            elapsed = timezone.now() - session.session_start_time
            time_remaining = session.time_limit_minutes - (elapsed.total_seconds() / 60)
            time_remaining = max(0.0, round(time_remaining, 2))
        
        return AssessmentQuestionsResponse(
            assessment_id=assessment_id,
            questions=questions,
            current_question_number=session.current_question_number or 1,
            total_questions=len(questions),
            time_remaining_minutes=time_remaining
        )
        
    except Exception as e:
        return Response({"error": f"Failed to get questions: {str(e)}"}, status=400)

@assessment_router.post("/submit-answer", response=AnswerSubmissionResponse)
def submit_answer(request, data: AnswerSubmissionRequest):
    """Submit an answer for a question in the assessment"""
    try:
        session = get_object_or_404(StudentSession, id=data.assessment_id)
        
        if session.status != 'ACTIVE':
            return Response({"error": "Assessment is not active"}, status=400)
        
        # Get the question
        question = get_object_or_404(AdaptiveQuestion, id=data.question_id)
        
        # Check if already answered
        existing_attempt = QuestionAttempt.objects.filter(
            session=session,
            question=question
        ).first()
        
        if existing_attempt:
            return Response({"error": "Question already answered"}, status=400)
        
        # Validate answer format
        if data.selected_answer not in ['a', 'b', 'c', 'd']:
            return Response({"error": "Invalid answer format"}, status=400)
        
        # Create question attempt
        is_correct = data.selected_answer.lower() == question.answer.lower()
        points_earned = calculate_question_points(question.difficulty_level, is_correct)
        
        with transaction.atomic():
            attempt = QuestionAttempt.objects.create(
                session=session,
                student=session.student,
                question=question,
                student_answer=data.selected_answer,
                correct_answer=question.answer,
                is_correct=is_correct,
                time_spent_seconds=data.time_taken_seconds,
                points_earned=points_earned,
                confidence_level=data.confidence_level,
                question_number_in_session=session.current_question_number or 1,
                answer_status='SUBMITTED',
                difficulty_when_presented=question.difficulty_level,
                question_points=calculate_question_points(question.difficulty_level, True),
                answer_submitted_at=timezone.now()
            )
            
            # Update session progress
            session.questions_attempted = (session.questions_attempted or 0) + 1
            session.current_question_number = (session.current_question_number or 0) + 1
            session.save()
            
            # Update question statistics
            question.times_attempted += 1
            if is_correct:
                question.times_correct += 1
            question.save()
        
        # Check if more questions available
        next_question_available = session.current_question_number <= len(session.question_sequence or [])
        
        return AnswerSubmissionResponse(
            success=True,
            question_number=attempt.question_number_in_session,
            is_correct=is_correct,
            correct_answer=question.answer,
            explanation=f"Correct answer is {question.answer}: {question.correct_option_text}",
            points_earned=points_earned,
            next_question_available=next_question_available
        )
        
    except Exception as e:
        return Response({"error": f"Failed to submit answer: {str(e)}"}, status=400)

@assessment_router.post("/complete", response=AssessmentResultResponse)
def complete_assessment(request, data: AssessmentResultRequest):
    """Complete the assessment and generate results"""
    try:
        session = get_object_or_404(StudentSession, id=data.assessment_id)
        
        # Get all question attempts for this session
        attempts = QuestionAttempt.objects.filter(session=session).select_related('question')
        
        # Calculate results
        total_questions = len(session.question_sequence or [])
        questions_attempted = attempts.count()
        questions_correct = attempts.filter(is_correct=True).count()
        accuracy_percentage = (questions_correct / questions_attempted * 100) if questions_attempted > 0 else 0
        total_time_seconds = sum(attempt.time_spent_seconds for attempt in attempts)
        total_points_earned = sum(attempt.points_earned for attempt in attempts)
        
        # Calculate max possible points
        max_possible_points = 0
        for q_id in session.question_sequence or []:
            try:
                question = AdaptiveQuestion.objects.get(id=q_id)
                max_possible_points += calculate_question_points(question.difficulty_level, True)
            except AdaptiveQuestion.DoesNotExist:
                continue
        
        # Update session status
        with transaction.atomic():
            session.status = 'COMPLETED'
            session.session_end_time = timezone.now()
            session.percentage_score = accuracy_percentage
            session.session_duration_seconds = total_time_seconds
            session.questions_attempted = questions_attempted
            session.questions_correct = questions_correct
            session.questions_incorrect = questions_attempted - questions_correct
            session.save()
            
            # Update student progress
            progress, created = StudentProgress.objects.get_or_create(
                student=session.student,
                subject=session.subject,
                defaults={
                    'mastery_score': accuracy_percentage,
                    'total_sessions': 1,
                    'total_study_time_seconds': total_time_seconds,
                    'total_questions_attempted': questions_attempted,
                    'total_questions_correct': questions_correct,
                    'current_accuracy_percentage': accuracy_percentage
                }
            )
            
            if not created:
                # Update existing progress using the proper method
                progress.update_from_session(session)
        
        # Generate detailed results
        question_results = []
        for attempt in attempts:
            question_results.append(QuestionResult(
                question_id=str(attempt.question.id),
                question_text=attempt.question.question_text,
                selected_answer=attempt.student_answer,
                correct_answer=attempt.correct_answer,
                is_correct=attempt.is_correct,
                time_taken_seconds=int(attempt.time_spent_seconds),
                points_earned=attempt.points_earned,
                topic=attempt.question.topic or '',
                difficulty_level=attempt.question.difficulty_level
            ))
        
        # Generate performance analysis
        performance_analysis = generate_performance_analysis(list(attempts))
        
        return AssessmentResultResponse(
            assessment_id=str(session.id),
            student_username=session.student.username,
            subject_name=session.subject.name,
            chapter_name=session.chapter.name if session.chapter else None,
            total_questions=total_questions,
            questions_attempted=questions_attempted,
            questions_correct=questions_correct,
            accuracy_percentage=round(accuracy_percentage, 1),
            total_time_seconds=total_time_seconds,
            total_points_earned=total_points_earned,
            max_possible_points=max_possible_points,
            grade=calculate_grade(accuracy_percentage),
            performance_analysis=performance_analysis,
            question_results=question_results,
            completion_time=session.session_end_time or timezone.now()
        )
        
    except Exception as e:
        return Response({"error": f"Failed to complete assessment: {str(e)}"}, status=400)

@assessment_router.get("/student-results/{username}", response=List[AssessmentResultResponse])
def get_student_results(request, username: str, limit: int = 10):
    """Get assessment results for a specific student"""
    try:
        student = get_object_or_404(User, username=username)
        
        sessions = StudentSession.objects.filter(
            student=student,
            status='COMPLETED'
        ).order_by('-session_end_time')[:limit]
        
        results = []
        for session in sessions:
            # Get attempts for this session
            attempts = QuestionAttempt.objects.filter(session=session).select_related('question')
            
            # Calculate basic stats
            questions_attempted = attempts.count()
            questions_correct = attempts.filter(is_correct=True).count()
            accuracy_percentage = (questions_correct / questions_attempted * 100) if questions_attempted > 0 else 0
            total_time_seconds = sum(attempt.time_spent_seconds for attempt in attempts)
            total_points_earned = sum(attempt.points_earned for attempt in attempts)
            
            # Generate question results
            question_results = []
            for attempt in attempts:
                question_results.append(QuestionResult(
                    question_id=str(attempt.question.id),
                    question_text=attempt.question.question_text,
                    selected_answer=attempt.student_answer,
                    correct_answer=attempt.correct_answer,
                    is_correct=attempt.is_correct,
                    time_taken_seconds=int(attempt.time_spent_seconds),
                    points_earned=attempt.points_earned,
                    topic=attempt.question.topic or '',
                    difficulty_level=attempt.question.difficulty_level
                ))
            
            results.append(AssessmentResultResponse(
                assessment_id=str(session.id),
                student_username=session.student.username,
                subject_name=session.subject.name,
                chapter_name=session.chapter.name if session.chapter else None,
                total_questions=len(session.question_sequence or []),
                questions_attempted=questions_attempted,
                questions_correct=questions_correct,
                accuracy_percentage=round(accuracy_percentage, 1),
                total_time_seconds=total_time_seconds,
                total_points_earned=total_points_earned,
                max_possible_points=0,  # Calculate if needed
                grade=calculate_grade(accuracy_percentage),
                performance_analysis=generate_performance_analysis(list(attempts)),
                question_results=question_results,
                completion_time=session.session_end_time
            ))
        
        return results
        
    except Exception as e:
        return Response({"error": f"Failed to get student results: {str(e)}"}, status=400)

# ============================================================================
# FRONTEND SUPPORT ENDPOINTS
# ============================================================================

class SubjectSchema(Schema):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    
class ChapterSchema(Schema):
    id: int
    title: str
    description: Optional[str] = None
    subject_id: int
    order: int
    is_unlocked: bool = True

@assessment_router.get("/subjects", response=List[SubjectSchema])
def get_subjects(request):
    """Get all available subjects for assessment"""
    try:
        subjects = Subject.objects.filter(is_active=True).order_by('name')
        return [
            {
                "id": subject.id,
                "code": subject.code,
                "name": subject.name,
                "description": subject.description,
                "icon": "BookOpen",  # Default icon
                "color": "blue"  # Default color
            }
            for subject in subjects
        ]
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@assessment_router.get("/subjects/{subject_id}/chapters", response=List[ChapterSchema]) 
def get_chapters(request, subject_id: int):
    """Get chapters for a specific subject"""
    try:
        subject = get_object_or_404(Subject, id=subject_id, is_active=True)
        chapters = Chapter.objects.filter(subject=subject, is_active=True).order_by('chapter_number', 'name')
        
        return [
            {
                "id": chapter.id,
                "title": chapter.name,
                "description": chapter.description,
                "subject_id": subject_id,
                "order": chapter.chapter_number,
                "is_unlocked": True  # For now, all chapters are unlocked
            }
            for chapter in chapters
        ]
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@assessment_router.get("/health")
def assessment_health_check(request):
    """Health check for assessment API"""
    return {
        "status": "ok",
        "message": "Assessment API is running",
        "timestamp": timezone.now(),
        "endpoints": [
            "GET /subjects - Get all subjects",
            "GET /subjects/{subject_id}/chapters - Get chapters for subject",
            "POST /start - Start new assessment",
            "GET /questions/{assessment_id} - Get assessment questions", 
            "POST /submit-answer - Submit answer",
            "POST /complete - Complete assessment and get results",
            "GET /student-results/{username} - Get student's past results"
        ]
    }