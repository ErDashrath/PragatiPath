"""
Student Assessment History API
Provides endpoints for students to view their assessment history and detailed results
"""

from ninja import Router, Schema
from ninja.responses import Response
from typing import List, Optional, Dict, Any
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from django.utils import timezone

from .improved_models import StudentSession, QuestionAttempt, StudentProgress

# Router for student history
history_router = Router()

# Schema definitions
class AssessmentHistoryItem(Schema):
    session_id: str
    subject_name: str
    chapter_name: Optional[str]
    session_type: str
    session_name: str
    status: str
    questions_attempted: int
    questions_correct: int
    percentage_score: float
    total_score: float
    max_possible_score: float
    grade: str
    session_start_time: datetime
    session_end_time: Optional[datetime]
    session_duration_seconds: int
    time_limit_minutes: Optional[int]

class DetailedAssessmentResult(Schema):
    session_info: AssessmentHistoryItem
    question_attempts: List[Dict[str, Any]]
    performance_analysis: Dict[str, Any]
    recommendations: List[str]

class StudentHistoryStats(Schema):
    total_assessments: int
    completed_assessments: int
    total_questions_attempted: int
    total_questions_correct: int
    overall_accuracy: float
    average_session_time: int
    best_accuracy: float
    most_recent_session: Optional[datetime]
    subjects_attempted: List[str]
    favorite_subject: Optional[str]

@history_router.get("/students/{student_username}/history", response=List[AssessmentHistoryItem])
def get_student_assessment_history(request, student_username: str):
    """Get complete assessment history for a student"""
    try:
        student = get_object_or_404(User, username=student_username)
        
        sessions = StudentSession.objects.filter(
            student=student
        ).select_related('subject', 'chapter').order_by('-session_start_time')
        
        history_items = []
        for session in sessions:
            # Calculate grade based on percentage
            if session.percentage_score >= 90:
                grade = 'A+'
            elif session.percentage_score >= 80:
                grade = 'A'
            elif session.percentage_score >= 70:
                grade = 'B'
            elif session.percentage_score >= 60:
                grade = 'C'
            elif session.percentage_score >= 50:
                grade = 'D'
            else:
                grade = 'F'
            
            # Calculate max possible score
            attempts = QuestionAttempt.objects.filter(session=session)
            max_possible_score = sum(attempt.question_points for attempt in attempts)
            
            history_items.append(AssessmentHistoryItem(
                session_id=str(session.id),
                subject_name=session.subject.name,
                chapter_name=session.chapter.name if session.chapter else None,
                session_type=session.session_type,
                session_name=session.session_name,
                status=session.status,
                questions_attempted=session.questions_attempted,
                questions_correct=session.questions_correct,
                percentage_score=session.percentage_score,
                total_score=session.total_score,
                max_possible_score=max_possible_score,
                grade=grade,
                session_start_time=session.session_start_time,
                session_end_time=session.session_end_time,
                session_duration_seconds=session.session_duration_seconds,
                time_limit_minutes=session.time_limit_minutes
            ))
        
        return history_items
        
    except Exception as e:
        return Response({"error": f"Failed to get history: {str(e)}"}, status=400)

@history_router.get("/students/{student_username}/assessment/{session_id}", response=DetailedAssessmentResult)
def get_detailed_assessment_result(request, student_username: str, session_id: str):
    """Get detailed results for a specific assessment"""
    try:
        student = get_object_or_404(User, username=student_username)
        session = get_object_or_404(StudentSession, id=session_id, student=student)
        
        # Get basic session info
        if session.percentage_score >= 90:
            grade = 'A+'
        elif session.percentage_score >= 80:
            grade = 'A'
        elif session.percentage_score >= 70:
            grade = 'B'
        elif session.percentage_score >= 60:
            grade = 'C'
        elif session.percentage_score >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        attempts = QuestionAttempt.objects.filter(session=session).select_related('question')
        max_possible_score = sum(attempt.question_points for attempt in attempts)
        
        session_info = AssessmentHistoryItem(
            session_id=str(session.id),
            subject_name=session.subject.name,
            chapter_name=session.chapter.name if session.chapter else None,
            session_type=session.session_type,
            session_name=session.session_name,
            status=session.status,
            questions_attempted=session.questions_attempted,
            questions_correct=session.questions_correct,
            percentage_score=session.percentage_score,
            total_score=session.total_score,
            max_possible_score=max_possible_score,
            grade=grade,
            session_start_time=session.session_start_time,
            session_end_time=session.session_end_time,
            session_duration_seconds=session.session_duration_seconds,
            time_limit_minutes=session.time_limit_minutes
        )
        
        # Get question attempts with details
        question_attempts = []
        for attempt in attempts.order_by('question_number_in_session'):
            question_attempts.append({
                "question_number": attempt.question_number_in_session,
                "question_text": attempt.question.question_text,
                "question_type": attempt.question.question_type,
                "options": attempt.question.formatted_options,
                "student_answer": attempt.student_answer,
                "correct_answer": attempt.correct_answer,
                "is_correct": attempt.is_correct,
                "time_spent_seconds": attempt.time_spent_seconds,
                "points_earned": attempt.points_earned,
                "question_points": attempt.question_points,
                "difficulty_level": attempt.difficulty_when_presented,
                "topic": attempt.question.topic or '',
                "subtopic": attempt.question.subtopic or '',
                "explanation": getattr(attempt.question, 'explanation', ''),
                "confidence_level": attempt.confidence_level
            })
        
        # Performance analysis
        topics_performance = {}
        difficulty_performance = {}
        
        for attempt in attempts:
            topic = attempt.question.topic or 'General'
            difficulty = attempt.difficulty_when_presented
            
            # Topic analysis
            if topic not in topics_performance:
                topics_performance[topic] = {'correct': 0, 'total': 0}
            topics_performance[topic]['total'] += 1
            if attempt.is_correct:
                topics_performance[topic]['correct'] += 1
            
            # Difficulty analysis
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {'correct': 0, 'total': 0}
            difficulty_performance[difficulty]['total'] += 1
            if attempt.is_correct:
                difficulty_performance[difficulty]['correct'] += 1
        
        # Calculate topic percentages
        for topic in topics_performance:
            total = topics_performance[topic]['total']
            correct = topics_performance[topic]['correct']
            topics_performance[topic]['accuracy'] = (correct / total * 100) if total > 0 else 0
        
        # Calculate difficulty percentages
        for difficulty in difficulty_performance:
            total = difficulty_performance[difficulty]['total']
            correct = difficulty_performance[difficulty]['correct']
            difficulty_performance[difficulty]['accuracy'] = (correct / total * 100) if total > 0 else 0
        
        performance_analysis = {
            "topics_performance": topics_performance,
            "difficulty_performance": difficulty_performance,
            "average_time_per_question": session.session_duration_seconds / session.questions_attempted if session.questions_attempted > 0 else 0,
            "fastest_correct_answer": min([a.time_spent_seconds for a in attempts if a.is_correct], default=0),
            "slowest_correct_answer": max([a.time_spent_seconds for a in attempts if a.is_correct], default=0),
            "strengths": [],
            "improvement_areas": []
        }
        
        # Generate strengths and improvement areas
        strengths = []
        improvement_areas = []
        
        if session.percentage_score >= 80:
            strengths.append("Excellent overall performance")
        if session.session_duration_seconds / 60 <= (session.time_limit_minutes or 30) * 0.8:
            strengths.append("Good time management")
        
        for topic, perf in topics_performance.items():
            if perf['accuracy'] >= 80:
                strengths.append(f"Strong in {topic}")
            elif perf['accuracy'] < 60:
                improvement_areas.append(f"Practice more {topic} questions")
        
        if session.percentage_score < 70:
            improvement_areas.append("Focus on fundamental concepts")
        if not strengths:
            improvement_areas.append("Regular practice needed")
        
        performance_analysis["strengths"] = strengths
        performance_analysis["improvement_areas"] = improvement_areas
        
        # Generate recommendations
        recommendations = []
        if session.percentage_score < 60:
            recommendations.append("Review basic concepts and practice more questions")
        elif session.percentage_score < 80:
            recommendations.append("Focus on weak areas and practice timed assessments")
        else:
            recommendations.append("Maintain your performance with regular practice")
        
        for topic, perf in topics_performance.items():
            if perf['accuracy'] < 50:
                recommendations.append(f"Spend extra time studying {topic}")
        
        return DetailedAssessmentResult(
            session_info=session_info,
            question_attempts=question_attempts,
            performance_analysis=performance_analysis,
            recommendations=recommendations
        )
        
    except Exception as e:
        return Response({"error": f"Failed to get detailed results: {str(e)}"}, status=400)

@history_router.get("/students/{student_username}/stats", response=StudentHistoryStats)
def get_student_history_stats(request, student_username: str):
    """Get overall statistics for a student's assessment history"""
    try:
        student = get_object_or_404(User, username=student_username)
        
        sessions = StudentSession.objects.filter(student=student)
        completed_sessions = sessions.filter(status='COMPLETED')
        
        if not sessions.exists():
            return StudentHistoryStats(
                total_assessments=0,
                completed_assessments=0,
                total_questions_attempted=0,
                total_questions_correct=0,
                overall_accuracy=0.0,
                average_session_time=0,
                best_accuracy=0.0,
                most_recent_session=None,
                subjects_attempted=[],
                favorite_subject=None
            )
        
        # Calculate statistics
        total_questions_attempted = sum(s.questions_attempted for s in completed_sessions)
        total_questions_correct = sum(s.questions_correct for s in completed_sessions)
        overall_accuracy = (total_questions_correct / total_questions_attempted * 100) if total_questions_attempted > 0 else 0
        
        average_session_time = int(completed_sessions.aggregate(
            avg_time=Avg('session_duration_seconds')
        )['avg_time'] or 0)
        
        best_accuracy = max([s.percentage_score for s in completed_sessions], default=0.0)
        
        most_recent_session = sessions.order_by('-session_start_time').first()
        most_recent_time = most_recent_session.session_start_time if most_recent_session else None
        
        # Get subjects attempted
        subjects_attempted = list(sessions.values_list('subject__name', flat=True).distinct())
        
        # Find favorite subject (most sessions)
        subject_counts = sessions.values('subject__name').annotate(
            count=Count('id')
        ).order_by('-count')
        favorite_subject = subject_counts.first()['subject__name'] if subject_counts else None
        
        return StudentHistoryStats(
            total_assessments=sessions.count(),
            completed_assessments=completed_sessions.count(),
            total_questions_attempted=total_questions_attempted,
            total_questions_correct=total_questions_correct,
            overall_accuracy=overall_accuracy,
            average_session_time=average_session_time,
            best_accuracy=best_accuracy,
            most_recent_session=most_recent_time,
            subjects_attempted=subjects_attempted,
            favorite_subject=favorite_subject
        )
        
    except Exception as e:
        return Response({"error": f"Failed to get stats: {str(e)}"}, status=400)

@history_router.get("/students/{student_username}/subjects/{subject_name}/history", response=List[AssessmentHistoryItem])
def get_student_subject_history(request, student_username: str, subject_name: str):
    """Get assessment history for a specific subject"""
    try:
        student = get_object_or_404(User, username=student_username)
        
        sessions = StudentSession.objects.filter(
            student=student,
            subject__name=subject_name
        ).select_related('subject', 'chapter').order_by('-session_start_time')
        
        history_items = []
        for session in sessions:
            # Calculate grade
            if session.percentage_score >= 90:
                grade = 'A+'
            elif session.percentage_score >= 80:
                grade = 'A'
            elif session.percentage_score >= 70:
                grade = 'B'
            elif session.percentage_score >= 60:
                grade = 'C'
            elif session.percentage_score >= 50:
                grade = 'D'
            else:
                grade = 'F'
            
            attempts = QuestionAttempt.objects.filter(session=session)
            max_possible_score = sum(attempt.question_points for attempt in attempts)
            
            history_items.append(AssessmentHistoryItem(
                session_id=str(session.id),
                subject_name=session.subject.name,
                chapter_name=session.chapter.name if session.chapter else None,
                session_type=session.session_type,
                session_name=session.session_name,
                status=session.status,
                questions_attempted=session.questions_attempted,
                questions_correct=session.questions_correct,
                percentage_score=session.percentage_score,
                total_score=session.total_score,
                max_possible_score=max_possible_score,
                grade=grade,
                session_start_time=session.session_start_time,
                session_end_time=session.session_end_time,
                session_duration_seconds=session.session_duration_seconds,
                time_limit_minutes=session.time_limit_minutes
            ))
        
        return history_items
        
    except Exception as e:
        return Response({"error": f"Failed to get subject history: {str(e)}"}, status=400)