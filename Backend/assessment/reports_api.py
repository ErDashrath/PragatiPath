#!/usr/bin/env python3
"""
Django API endpoints for reports and analytics
"""

from ninja import Router
from ninja.schema import Schema
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Max, Min
from django.contrib.auth.models import User
from assessment.models import StudentSession, QuestionAttempt, AdaptiveQuestion, Subject
from assessment.adaptive_submission_models import AdaptiveSubmission, AdaptiveSubmissionAnalyzer

reports_router = Router()

# ============================================================================
# Response Schemas
# ============================================================================

class SessionReportSchema(Schema):
    session_id: str
    student_name: str
    subject: str
    start_time: datetime
    end_time: Optional[datetime]
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    average_time_per_question: float
    mastery_progression: List[float]
    difficulty_distribution: Dict[str, int]
    session_duration_minutes: float

class QuestionAnalyticsSchema(Schema):
    question_id: str
    question_text: str
    subject: str
    difficulty_level: str
    total_attempts: int
    correct_attempts: int
    success_rate: float
    average_time_spent: float
    most_common_wrong_answer: Optional[str]

class StudentPerformanceSchema(Schema):
    student_id: int
    student_name: str
    total_sessions: int
    total_questions_attempted: int
    overall_accuracy: float
    mastery_growth: float
    subjects_studied: List[str]
    last_activity: datetime
    performance_trend: List[Dict[str, Any]]

class SubjectAnalyticsSchema(Schema):
    subject_name: str
    subject_code: str
    total_students: int
    total_questions_available: int
    total_attempts: int
    average_accuracy: float
    difficulty_breakdown: Dict[str, Dict[str, Any]]
    learning_progression: List[Dict[str, Any]]

class DashboardStatsSchema(Schema):
    total_students: int
    total_sessions: int
    total_submissions: int
    average_session_accuracy: float
    most_popular_subject: str
    recent_activity: List[Dict[str, Any]]
    performance_trends: Dict[str, List[float]]

# ============================================================================
# Session Reports API
# ============================================================================

@reports_router.get("/sessions", response=List[SessionReportSchema])
def get_all_session_reports(request, student_id: Optional[int] = None, days: int = 30):
    """Get session-wise reports for the dashboard"""
    
    # Filter sessions by date and student
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    sessions = StudentSession.objects.filter(
        session_start_time__gte=start_date,
        session_start_time__lte=end_date
    )
    
    if student_id:
        sessions = sessions.filter(student_id=student_id)
    
    session_reports = []
    
    for session in sessions:
        # Get attempts for this session
        attempts = QuestionAttempt.objects.filter(session=session)
        
        # Calculate session metrics
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Average time calculation
        avg_time = attempts.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time'] or 0
        
        # Mastery progression from AdaptiveSubmission
        adaptive_submissions = AdaptiveSubmission.objects.filter(session=session).order_by('created_at')
        mastery_progression = [sub.bkt_mastery_after for sub in adaptive_submissions]
        
        # Difficulty distribution
        difficulty_dist = attempts.values('difficulty_when_presented').annotate(
            count=Count('id')
        )
        difficulty_distribution = {item['difficulty_when_presented']: item['count'] for item in difficulty_dist}
        
        # Session duration
        duration_minutes = 0
        if session.session_end_time:
            duration = session.session_end_time - session.session_start_time
            duration_minutes = duration.total_seconds() / 60
        
        session_reports.append(SessionReportSchema(
            session_id=str(session.id),
            student_name=session.student.username,
            subject=session.subject.name if session.subject else "Unknown",
            start_time=session.session_start_time,
            end_time=session.session_end_time,
            total_questions=total_questions,
            correct_answers=correct_answers,
            accuracy_percentage=round(accuracy, 2),
            average_time_per_question=round(avg_time, 2),
            mastery_progression=mastery_progression,
            difficulty_distribution=difficulty_distribution,
            session_duration_minutes=round(duration_minutes, 2)
        ))
    
    return session_reports

@reports_router.get("/session/{session_id}", response=SessionReportSchema)
def get_session_detail(request, session_id: str):
    """Get detailed report for a specific session"""
    
    try:
        session = StudentSession.objects.get(id=session_id)
    except StudentSession.DoesNotExist:
        return {"error": "Session not found"}, 404
    
    # Get attempts for this session
    attempts = QuestionAttempt.objects.filter(session=session)
    
    # Calculate session metrics
    total_questions = attempts.count()
    correct_answers = attempts.filter(is_correct=True).count()
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Average time calculation
    avg_time = attempts.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time'] or 0
    
    # Mastery progression from AdaptiveSubmission
    adaptive_submissions = AdaptiveSubmission.objects.filter(session=session).order_by('created_at')
    mastery_progression = [sub.bkt_mastery_after for sub in adaptive_submissions]
    
    # Difficulty distribution
    difficulty_dist = attempts.values('difficulty_when_presented').annotate(
        count=Count('id')
    )
    difficulty_distribution = {item['difficulty_when_presented']: item['count'] for item in difficulty_dist}
    
    # Session duration
    duration_minutes = 0
    if session.session_end_time:
        duration = session.session_end_time - session.session_start_time
        duration_minutes = duration.total_seconds() / 60
    
    return SessionReportSchema(
        session_id=str(session.id),
        student_name=session.student.username,
        subject=session.subject.name if session.subject else "Unknown",
        start_time=session.session_start_time,
        end_time=session.session_end_time,
        total_questions=total_questions,
        correct_answers=correct_answers,
        accuracy_percentage=round(accuracy, 2),
        average_time_per_question=round(avg_time, 2),
        mastery_progression=mastery_progression,
        difficulty_distribution=difficulty_distribution,
        session_duration_minutes=round(duration_minutes, 2)
    )

# ============================================================================
# Student Performance Reports API
# ============================================================================

@reports_router.get("/students", response=List[StudentPerformanceSchema])
def get_student_performance_reports(request, days: int = 30):
    """Get performance reports for all students"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get students who have activity in the specified period
    active_students = User.objects.filter(
        question_attempts__created_at__gte=start_date
    ).distinct()
    
    student_reports = []
    
    for student in active_students:
        # Get student sessions
        sessions = StudentSession.objects.filter(
            student=student,
            session_start_time__gte=start_date
        )
        
        # Get all attempts
        attempts = QuestionAttempt.objects.filter(
            student=student,
            created_at__gte=start_date
        )
        
        total_sessions = sessions.count()
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        overall_accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Mastery growth calculation
        adaptive_submissions = AdaptiveSubmission.objects.filter(
            student=student,
            created_at__gte=start_date
        ).order_by('created_at')
        
        mastery_growth = 0
        if adaptive_submissions.count() >= 2:
            first_mastery = adaptive_submissions.first().bkt_mastery_before
            last_mastery = adaptive_submissions.last().bkt_mastery_after
            mastery_growth = last_mastery - first_mastery
        
        # Subjects studied
        subjects_studied = list(
            sessions.values_list('subject__name', flat=True).distinct()
        )
        
        # Last activity
        last_activity = attempts.aggregate(
            last=Max('created_at')
        )['last'] or datetime.now()
        
        # Performance trend (daily accuracy over the period)
        performance_trend = []
        for i in range(7):  # Last 7 days
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_attempts = attempts.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            )
            
            if day_attempts.exists():
                day_accuracy = (
                    day_attempts.filter(is_correct=True).count() / 
                    day_attempts.count() * 100
                )
                performance_trend.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "accuracy": round(day_accuracy, 2),
                    "questions": day_attempts.count()
                })
        
        student_reports.append(StudentPerformanceSchema(
            student_id=student.id,
            student_name=student.username,
            total_sessions=total_sessions,
            total_questions_attempted=total_questions,
            overall_accuracy=round(overall_accuracy, 2),
            mastery_growth=round(mastery_growth, 4),
            subjects_studied=subjects_studied,
            last_activity=last_activity,
            performance_trend=performance_trend
        ))
    
    return student_reports

# ============================================================================
# Question Analytics API
# ============================================================================

@reports_router.get("/questions", response=List[QuestionAnalyticsSchema])
def get_question_analytics(request, subject_code: Optional[str] = None):
    """Get analytics for questions"""
    
    questions = AdaptiveQuestion.objects.all()
    
    if subject_code:
        questions = questions.filter(subject__code=subject_code)
    
    question_analytics = []
    
    for question in questions[:50]:  # Limit to 50 for performance
        # Get attempts for this question
        attempts = QuestionAttempt.objects.filter(question=question)
        
        total_attempts = attempts.count()
        correct_attempts = attempts.filter(is_correct=True).count()
        success_rate = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Average time spent
        avg_time = attempts.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time'] or 0
        
        # Most common wrong answer
        wrong_answers = attempts.filter(is_correct=False).values('student_answer').annotate(
            count=Count('id')
        ).order_by('-count')
        
        most_common_wrong = wrong_answers.first()['student_answer'] if wrong_answers else None
        
        question_analytics.append(QuestionAnalyticsSchema(
            question_id=str(question.id),
            question_text=question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
            subject=question.subject if question.subject else "Unknown",
            difficulty_level=question.difficulty_level,
            total_attempts=total_attempts,
            correct_attempts=correct_attempts,
            success_rate=round(success_rate, 2),
            average_time_spent=round(avg_time, 2),
            most_common_wrong_answer=most_common_wrong
        ))
    
    return question_analytics

# ============================================================================
# Dashboard Stats API
# ============================================================================

@reports_router.get("/dashboard", response=DashboardStatsSchema)
def get_dashboard_stats(request):
    """Get overview statistics for the dashboard"""
    
    # Get counts
    total_students = User.objects.filter(question_attempts__isnull=False).distinct().count()
    total_sessions = StudentSession.objects.count()
    total_submissions = AdaptiveSubmission.objects.count()
    
    # Average session accuracy
    all_attempts = QuestionAttempt.objects.all()
    if all_attempts.exists():
        correct_attempts = all_attempts.filter(is_correct=True).count()
        average_session_accuracy = (correct_attempts / all_attempts.count() * 100)
    else:
        average_session_accuracy = 0
    
    # Most popular subject
    popular_subject_data = StudentSession.objects.values('subject__name').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    most_popular_subject = popular_subject_data['subject__name'] if popular_subject_data else "None"
    
    # Recent activity (last 10 submissions)
    recent_submissions = AdaptiveSubmission.objects.order_by('-created_at')[:10]
    recent_activity = []
    
    for submission in recent_submissions:
        recent_activity.append({
            "student": submission.student.username,
            "subject": submission.subject.name if submission.subject else "Unknown",
            "correct": submission.is_correct,
            "time": submission.created_at.isoformat(),
            "mastery": round(submission.bkt_mastery_after, 3)
        })
    
    # Performance trends (last 7 days accuracy)
    performance_trends = {"daily_accuracy": []}
    
    for i in range(7):
        day_start = datetime.now() - timedelta(days=6-i)
        day_end = day_start + timedelta(days=1)
        
        day_attempts = QuestionAttempt.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        )
        
        if day_attempts.exists():
            day_accuracy = (
                day_attempts.filter(is_correct=True).count() / 
                day_attempts.count() * 100
            )
        else:
            day_accuracy = 0
        
        performance_trends["daily_accuracy"].append(round(day_accuracy, 2))
    
    return DashboardStatsSchema(
        total_students=total_students,
        total_sessions=total_sessions,
        total_submissions=total_submissions,
        average_session_accuracy=round(average_session_accuracy, 2),
        most_popular_subject=most_popular_subject,
        recent_activity=recent_activity,
        performance_trends=performance_trends
    )