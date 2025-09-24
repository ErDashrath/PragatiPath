"""
Frontend-Ready API Endpoints for React Integration
Complete API documentation and types for TypeScript frontend
"""

from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max, Min
from enum import Enum
import json
import logging

# Import all existing routers
from core.api import router as core_router
from student_model.api import router as student_model_router
from assessment.api import router as assessment_router
from assessment.competitive_api_v1 import router as competitive_v1_router
from assessment.enhanced_api_v2 import router as enhanced_v2_router
from analytics.api import router as analytics_router
from practice.api import router as practice_router

logger = logging.getLogger(__name__)

frontend_router = Router()

# ============================================================================
# Frontend-Specific Response Schemas
# ============================================================================

class APIResponse(Schema):
    """Standard API response format for frontend"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime

class StudentDashboardSchema(Schema):
    """Complete student dashboard data"""
    student_info: Dict[str, Any]
    current_level: int
    progress_stats: Dict[str, Any]
    active_subjects: List[str]
    mastery_scores: Dict[str, float]
    next_recommendations: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    srs_due_count: int
    algorithm_status: Dict[str, str]

class AdminDashboardSchema(Schema):
    """Complete admin dashboard data"""
    system_stats: Dict[str, Any]
    student_count: int
    question_bank_stats: Dict[str, Any]
    algorithm_performance: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    usage_analytics: Dict[str, Any]

class QuestionSetSchema(Schema):
    """Question set for frontend consumption"""
    questions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    total_count: int
    difficulty_distribution: Dict[str, int]
    estimated_time: int

class AssessmentSessionSchema(Schema):
    """Assessment session for frontend"""
    session_id: str
    student_id: str
    current_question: Optional[Dict[str, Any]]
    progress: Dict[str, Any]
    time_remaining: Optional[int]
    session_stats: Dict[str, Any]

# ============================================================================
# Frontend Dashboard Endpoints
# ============================================================================

@frontend_router.get("/dashboard/student/{student_id}", 
                    response=StudentDashboardSchema,
                    tags=["Frontend Dashboard"])
def get_student_dashboard(request, student_id: str):
    """
    Get complete student dashboard data for React frontend
    Combines data from all algorithms and systems
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, Interaction
        from practice.models import SRSCard
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            student = StudentProfile.objects.get(id=student_id)
        except StudentProfile.DoesNotExist:
            raise HttpError(404, f"Student {student_id} not found")
        
        # Get basic student info
        student_info = {
            "id": str(student.id),
            "name": student.user.username if hasattr(student, 'user') else f"Student {student_id}",
            "email": student.user.email if hasattr(student, 'user') else None,
            "created_at": student.created_at.isoformat() if hasattr(student, 'created_at') else None,
            "last_active": timezone.now().isoformat()
        }
        
        # Get current level and progress
        current_level = getattr(student, 'current_level', 1)
        if isinstance(current_level, dict):
            current_level = max(current_level.values()) if current_level else 1
        
        # Calculate progress stats
        total_interactions = Interaction.objects.filter(student=student.user).count()
        recent_interactions = Interaction.objects.filter(
            student=student.user,
            timestamp__gte=timezone.now() - timedelta(days=7)
        )
        
        correct_recent = recent_interactions.filter(is_correct=True).count()
        accuracy = (correct_recent / max(1, recent_interactions.count())) * 100
        
        progress_stats = {
            "total_questions_answered": total_interactions,
            "weekly_accuracy": round(accuracy, 1),
            "streak": _calculate_streak(student),
            "level_progress": _calculate_level_progress(student),
            "time_studied_this_week": _calculate_study_time(student)
        }
        
        # Get active subjects
        active_subjects = list(AdaptiveQuestion.objects.filter(
            is_active=True
        ).values_list('subject', flat=True).distinct())
        
        # Get mastery scores from BKT
        mastery_scores = {}
        bkt_params = getattr(student, 'bkt_parameters', {})
        for skill, params in bkt_params.items():
            if isinstance(params, dict) and 'P_L' in params:
                mastery_scores[skill] = params['P_L']
        
        # Get next recommendations
        next_recommendations = _generate_dashboard_recommendations(student)
        
        # Get recent activities
        recent_activities = _get_recent_activities(student)
        
        # Get SRS due count
        srs_due_count = SRSCard.objects.filter(
            student=student.user if hasattr(student, 'user') else student,
            due_date__lte=timezone.now()
        ).count()
        
        # Algorithm status
        algorithm_status = {
            "bkt": "active",
            "dkt": "active" if _check_dkt_service() else "fallback",
            "irt": "active",
            "sm2": "active"
        }
        
        return {
            "student_info": student_info,
            "current_level": current_level,
            "progress_stats": progress_stats,
            "active_subjects": active_subjects,
            "mastery_scores": mastery_scores,
            "next_recommendations": next_recommendations,
            "recent_activities": recent_activities,
            "srs_due_count": srs_due_count,
            "algorithm_status": algorithm_status
        }
        
    except Exception as e:
        logger.error(f"Error getting student dashboard: {e}")
        raise HttpError(500, f"Dashboard error: {str(e)}")


@frontend_router.get("/dashboard/admin", 
                    response=AdminDashboardSchema,
                    tags=["Frontend Dashboard"])
def get_admin_dashboard(request):
    """
    Get complete admin dashboard data for React frontend
    """
    try:
        from core.models import StudentProfile
        from assessment.models import AdaptiveQuestion, Interaction
        from practice.models import SRSCard
        from django.db.models import Count, Avg
        
        # System stats
        total_students = StudentProfile.objects.count()
        total_questions = AdaptiveQuestion.objects.filter(is_active=True).count()
        total_interactions = Interaction.objects.count()
        
        system_stats = {
            "total_students": total_students,
            "total_questions": total_questions,
            "total_interactions": total_interactions,
            "active_sessions": _get_active_sessions_count(),
            "system_uptime": _get_system_uptime()
        }
        
        # Question bank stats
        question_bank_stats = {}
        subjects = AdaptiveQuestion.objects.filter(is_active=True).values('subject').annotate(
            count=Count('id')
        )
        for subject_info in subjects:
            question_bank_stats[subject_info['subject']] = subject_info['count']
        
        # Algorithm performance
        algorithm_performance = {
            "bkt_accuracy": _calculate_bkt_accuracy(),
            "dkt_accuracy": _calculate_dkt_accuracy(),
            "irt_effectiveness": _calculate_irt_effectiveness(),
            "sm2_retention": _calculate_sm2_retention()
        }
        
        # Recent activities (system-wide)
        recent_activities = _get_system_recent_activities()
        
        # Usage analytics
        usage_analytics = _get_usage_analytics()
        
        return {
            "system_stats": system_stats,
            "student_count": total_students,
            "question_bank_stats": question_bank_stats,
            "algorithm_performance": algorithm_performance,
            "recent_activities": recent_activities,
            "usage_analytics": usage_analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {e}")
        raise HttpError(500, f"Admin dashboard error: {str(e)}")


# ============================================================================
# Frontend Assessment Endpoints
# ============================================================================

@frontend_router.post("/assessment/start-session",
                     response=AssessmentSessionSchema,
                     tags=["Frontend Assessment"])
def start_assessment_session(request, student_id: str, subject: str, question_count: int = 10):
    """
    Start a new assessment session for React frontend
    """
    try:
        from assessment.models import AdaptiveQuestion
        from uuid import uuid4
        
        # Create session ID
        session_id = str(uuid4())
        
        # Get questions for the session
        questions = AdaptiveQuestion.objects.filter(
            subject=subject,
            is_active=True
        ).order_by('?')[:question_count]
        
        if not questions.exists():
            raise HttpError(404, f"No questions available for subject: {subject}")
        
        # Store session in cache/database (implement as needed)
        session_data = {
            "session_id": session_id,
            "student_id": student_id,
            "subject": subject,
            "questions": [q.id for q in questions],
            "current_index": 0,
            "started_at": timezone.now().isoformat()
        }
        
        # Get first question
        first_question = questions.first()
        current_question = {
            "id": str(first_question.id),
            "text": first_question.question_text,
            "type": first_question.question_type,
            "options": first_question.formatted_options,
            "difficulty": first_question.difficulty,
            "estimated_time": first_question.estimated_time_seconds
        }
        
        return {
            "session_id": session_id,
            "student_id": student_id,
            "current_question": current_question,
            "progress": {
                "current": 1,
                "total": len(questions),
                "percentage": round((1 / len(questions)) * 100, 1)
            },
            "time_remaining": question_count * 60,  # Estimate 1 minute per question
            "session_stats": {
                "started_at": timezone.now().isoformat(),
                "questions_answered": 0,
                "correct_answers": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting assessment session: {e}")
        raise HttpError(500, f"Session start error: {str(e)}")


@frontend_router.get("/subjects/available",
                    tags=["Frontend Assessment"])
def get_available_subjects_for_frontend(request):
    """
    Get all available subjects with metadata for React frontend
    """
    try:
        from assessment.models import AdaptiveQuestion
        from django.db.models import Count, Avg
        
        subjects_data = []
        subjects = AdaptiveQuestion.objects.filter(is_active=True).values('subject').annotate(
            question_count=Count('id'),
            avg_difficulty=Avg('difficulty')
        ).order_by('subject')
        
        for subject_info in subjects:
            subject_code = subject_info['subject']
            subject_data = {
                "code": subject_code,
                "name": subject_code.replace('_', ' ').title(),
                "question_count": subject_info['question_count'],
                "avg_difficulty": round(subject_info['avg_difficulty'] or 0, 2),
                "description": _get_subject_description(subject_code),
                "icon": _get_subject_icon(subject_code),
                "color": _get_subject_color(subject_code)
            }
            subjects_data.append(subject_data)
        
        return {
            "success": True,
            "subjects": subjects_data,
            "total_count": len(subjects_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting subjects: {e}")
        raise HttpError(500, f"Subjects error: {str(e)}")


# ============================================================================
# Frontend Analytics Endpoints
# ============================================================================

@frontend_router.get("/analytics/student/{student_id}/charts",
                    tags=["Frontend Analytics"])
def get_student_analytics_for_charts(request, student_id: str, days: int = 30):
    """
    Get student analytics data formatted for React charts
    """
    try:
        from core.models import StudentProfile
        from assessment.models import Interaction
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        student = StudentProfile.objects.get(id=student_id)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Daily progress data for line chart
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            day_interactions = Interaction.objects.filter(
                student=student.user,
                timestamp__date=current_date.date()
            )
            
            daily_stats = {
                "date": current_date.strftime('%Y-%m-%d'),
                "questions_answered": day_interactions.count(),
                "correct_answers": day_interactions.filter(is_correct=True).count(),
                "accuracy": 0
            }
            
            if daily_stats["questions_answered"] > 0:
                daily_stats["accuracy"] = round(
                    (daily_stats["correct_answers"] / daily_stats["questions_answered"]) * 100, 1
                )
            
            daily_data.append(daily_stats)
            current_date += timedelta(days=1)
        
        # Subject performance data for bar chart
        subject_data = []
        interactions_by_subject = Interaction.objects.filter(
            student=student.user,
            timestamp__gte=start_date
        ).values('question__subject').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        )
        
        for subject_stats in interactions_by_subject:
            if subject_stats['question__subject']:
                accuracy = (subject_stats['correct'] / subject_stats['total']) * 100
                subject_data.append({
                    "subject": subject_stats['question__subject'],
                    "total_questions": subject_stats['total'],
                    "correct_answers": subject_stats['correct'],
                    "accuracy": round(accuracy, 1)
                })
        
        # Mastery progress data for radar chart
        mastery_data = []
        bkt_params = getattr(student, 'bkt_parameters', {})
        for skill, params in bkt_params.items():
            if isinstance(params, dict) and 'P_L' in params:
                mastery_data.append({
                    "skill": skill.replace('_', ' ').title(),
                    "mastery": round(params['P_L'] * 100, 1)
                })
        
        return {
            "success": True,
            "daily_progress": daily_data,
            "subject_performance": subject_data,
            "mastery_progress": mastery_data,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HttpError(500, f"Analytics error: {str(e)}")


# ============================================================================
# Helper Functions
# ============================================================================

def _calculate_streak(student) -> int:
    """Calculate current correct answer streak"""
    try:
        from assessment.models import Interaction
        recent = Interaction.objects.filter(
            student=student.user if hasattr(student, 'user') else student
        ).order_by('-timestamp')[:10]
        
        streak = 0
        for interaction in recent:
            if interaction.is_correct:
                streak += 1
            else:
                break
        return streak
    except:
        return 0

def _calculate_level_progress(student) -> Dict[str, Any]:
    """Calculate level progression data"""
    try:
        current_level = getattr(student, 'current_level', 1)
        if isinstance(current_level, dict):
            current_level = max(current_level.values()) if current_level else 1
        
        return {
            "current_level": current_level,
            "progress_to_next": 75,  # Mock data - implement actual calculation
            "unlocked_levels": list(range(1, current_level + 1)),
            "total_levels": 10
        }
    except:
        return {"current_level": 1, "progress_to_next": 0, "unlocked_levels": [1], "total_levels": 10}

def _calculate_study_time(student) -> int:
    """Calculate study time this week in minutes"""
    try:
        from assessment.models import Interaction
        from django.utils import timezone
        from datetime import timedelta
        
        week_start = timezone.now() - timedelta(days=7)
        interactions = Interaction.objects.filter(
            student=student.user if hasattr(student, 'user') else student,
            timestamp__gte=week_start
        )
        
        total_time = sum(i.response_time or 30 for i in interactions)  # Default 30 seconds
        return int(total_time / 60)  # Convert to minutes
    except:
        return 0

def _generate_dashboard_recommendations(student) -> List[Dict[str, Any]]:
    """Generate personalized recommendations"""
    recommendations = []
    
    try:
        # Get BKT-based recommendations
        bkt_params = getattr(student, 'bkt_parameters', {})
        for skill, params in bkt_params.items():
            if isinstance(params, dict) and 'P_L' in params:
                if params['P_L'] < 0.3:
                    recommendations.append({
                        "type": "practice",
                        "title": f"Practice {skill.replace('_', ' ').title()}",
                        "description": "This skill needs more attention",
                        "priority": "high",
                        "action": f"/practice/{skill}"
                    })
                elif params['P_L'] > 0.8:
                    recommendations.append({
                        "type": "advance",
                        "title": f"Advance in {skill.replace('_', ' ').title()}",
                        "description": "You've mastered this skill!",
                        "priority": "medium",
                        "action": f"/advance/{skill}"
                    })
        
        # Add SRS recommendations
        from practice.models import SRSCard
        from django.utils import timezone
        
        due_cards = SRSCard.objects.filter(
            student=student.user if hasattr(student, 'user') else student,
            due_date__lte=timezone.now()
        ).count()
        
        if due_cards > 0:
            recommendations.append({
                "type": "review",
                "title": "Review Spaced Repetition Cards",
                "description": f"{due_cards} cards are due for review",
                "priority": "high",
                "action": "/practice/srs"
            })
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
    
    return recommendations[:5]  # Limit to 5 recommendations

def _get_recent_activities(student) -> List[Dict[str, Any]]:
    """Get recent student activities"""
    activities = []
    
    try:
        from assessment.models import Interaction
        recent_interactions = Interaction.objects.filter(
            student=student.user if hasattr(student, 'user') else student
        ).order_by('-timestamp')[:10]
        
        for interaction in recent_interactions:
            activities.append({
                "type": "question_answered",
                "description": f"Answered question in {interaction.question.subject if hasattr(interaction, 'question') else 'Unknown'}",
                "result": "correct" if interaction.is_correct else "incorrect",
                "timestamp": interaction.timestamp.isoformat(),
                "details": {
                    "response_time": interaction.response_time,
                    "question_difficulty": getattr(interaction.question, 'difficulty', 0) if hasattr(interaction, 'question') else 0
                }
            })
    
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
    
    return activities

def _check_dkt_service() -> bool:
    """Check if DKT microservice is available"""
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def _get_active_sessions_count() -> int:
    """Get count of active assessment sessions"""
    # Implement session tracking
    return 0

def _get_system_uptime() -> str:
    """Get system uptime"""
    return "24h 30m"  # Mock data

def _calculate_bkt_accuracy() -> float:
    """Calculate BKT algorithm accuracy"""
    return 85.5  # Mock data

def _calculate_dkt_accuracy() -> float:
    """Calculate DKT algorithm accuracy"""
    return 78.2  # Mock data

def _calculate_irt_effectiveness() -> float:
    """Calculate IRT effectiveness"""
    return 92.1  # Mock data

def _calculate_sm2_retention() -> float:
    """Calculate SM-2 retention rate"""
    return 88.7  # Mock data

def _get_system_recent_activities() -> List[Dict[str, Any]]:
    """Get system-wide recent activities"""
    return [
        {
            "type": "student_registered",
            "description": "New student registered",
            "timestamp": timezone.now().isoformat()
        }
    ]

def _get_usage_analytics() -> Dict[str, Any]:
    """Get usage analytics"""
    return {
        "daily_active_users": 25,
        "weekly_active_users": 150,
        "avg_session_duration": "15m 30s",
        "popular_subjects": ["mathematics", "physics", "chemistry"]
    }

def _get_subject_description(subject_code: str) -> str:
    """Get subject description"""
    descriptions = {
        "mathematics": "Advanced mathematical concepts and problem solving",
        "physics": "Physics principles and applications",
        "chemistry": "Chemical reactions and molecular structures",
        "biology": "Life sciences and biological systems"
    }
    return descriptions.get(subject_code, f"Study {subject_code.replace('_', ' ').title()}")

def _get_subject_icon(subject_code: str) -> str:
    """Get subject icon name for frontend"""
    icons = {
        "mathematics": "calculator",
        "physics": "atom",
        "chemistry": "flask",
        "biology": "dna"
    }
    return icons.get(subject_code, "book")

def _get_subject_color(subject_code: str) -> str:
    """Get subject color for frontend"""
    colors = {
        "mathematics": "blue",
        "physics": "purple",
        "chemistry": "green",
        "biology": "orange"
    }
    return colors.get(subject_code, "gray")

# ============================================================================
# Status Endpoints
# ============================================================================

@frontend_router.get("/status/all", tags=["Frontend Status"])
def get_all_system_status(request):
    """
    Get comprehensive system status for frontend monitoring
    """
    return {
        "success": True,
        "system_status": "operational",
        "services": {
            "django_backend": "online",
            "dkt_microservice": "online" if _check_dkt_service() else "offline",
            "database": "online",
            "redis_cache": "online"
        },
        "algorithms": {
            "bkt": "active",
            "dkt": "active" if _check_dkt_service() else "fallback",
            "irt": "active",
            "sm2": "active"
        },
        "api_version": "1.0.0",
        "last_updated": timezone.now().isoformat()
    }


@frontend_router.get("/config/frontend", tags=["Frontend Config"])
def get_frontend_config(request):
    """
    Get configuration data needed by React frontend
    """
    return {
        "success": True,
        "config": {
            "api_base_url": "http://localhost:8000/api",
            "dkt_service_url": "http://localhost:8001",
            "features": {
                "real_time_updates": True,
                "ai_recommendations": True,
                "spaced_repetition": True,
                "adaptive_testing": True,
                "progress_analytics": True
            },
            "limits": {
                "max_questions_per_session": 50,
                "max_study_time_hours": 8,
                "max_concurrent_sessions": 3
            },
            "ui_config": {
                "theme": "adaptive",
                "animations": True,
                "sound_effects": False,
                "difficulty_colors": {
                    "very_easy": "#22c55e",
                    "easy": "#84cc16", 
                    "moderate": "#eab308",
                    "difficult": "#f97316",
                    "very_difficult": "#ef4444"
                }
            }
        }
    }