from ninja import Router
from ninja import Schema
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

router = Router()

class MetricType(str, Enum):
    ACCURACY = "accuracy"
    RESPONSE_TIME = "response_time"
    LEARNING_RATE = "learning_rate"
    ENGAGEMENT = "engagement"

class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

# Analytics schemas
class StudentPerformanceSchema(Schema):
    student_id: str  # Changed to str to support UUID
    total_questions: int
    correct_answers: int
    accuracy_rate: float
    average_response_time: float
    learning_progress: float
    last_activity: datetime

class LearningAnalyticsSchema(Schema):
    student_id: str  # Changed to str to support UUID
    knowledge_component_id: int
    mastery_level: float
    time_to_mastery: Optional[float] = None  # in hours
    attempts_count: int
    improvement_rate: float
    difficulty_preference: float

class SystemMetricsSchema(Schema):
    total_students: int
    total_questions: int
    total_responses: int
    average_session_duration: float
    most_difficult_topics: List[str]
    engagement_score: float
    generated_at: datetime

class ProgressTrackingSchema(Schema):
    student_id: str  # Changed to str to support UUID
    date: datetime
    knowledge_components_mastered: int
    questions_attempted: int
    time_spent: float  # in minutes
    accuracy_score: float

class RecommendationSchema(Schema):
    student_id: str  # Changed to str to support UUID
    recommended_topics: List[str]
    difficulty_adjustment: float
    study_time_suggestion: int  # in minutes
    reasoning: str
    confidence: float

# Student analytics endpoints
@router.get("/students/{student_id}/performance")
def get_student_performance(request, student_id: str, time_range: TimeRange = TimeRange.WEEK):
    """Get comprehensive performance analytics for a student"""
    from api_serializers import serialize_student_performance
    return serialize_student_performance(student_id)

@router.get("/students/{student_id}/learning-analytics")
def get_learning_analytics(request, student_id: str):
    """Get knowledge component learning analytics for a student"""
    from api_serializers import serialize_learning_analytics
    return serialize_learning_analytics(student_id)

@router.get("/students/{student_id}/progress-tracking")
def get_progress_tracking(request, student_id: str, days: int = 30):
    """Get daily progress tracking for a student"""
    from api_serializers import serialize_progress_tracking
    return serialize_progress_tracking(student_id, days)

@router.get("/students/{student_id}/recommendations")
def get_personalized_recommendations(request, student_id: str):
    """Get AI-powered learning recommendations for a student"""
    from api_serializers import serialize_recommendations
    return serialize_recommendations(student_id)

# System-wide analytics
@router.get("/system/metrics", response=SystemMetricsSchema)
def get_system_metrics(request):
    """Get overall system performance metrics"""
    # TODO: Implement actual system metrics calculation
    return {
        "total_students": 150,
        "total_questions": 500,
        "total_responses": 7500,
        "average_session_duration": 22.5,
        "most_difficult_topics": ["Calculus", "Advanced Algebra", "Trigonometry"],
        "engagement_score": 0.78,
        "generated_at": datetime.now()
    }

@router.get("/system/usage-patterns")
def get_usage_patterns(request, time_range: TimeRange = TimeRange.WEEK):
    """Get usage patterns and trends"""
    # TODO: Implement usage pattern analysis
    return {
        "peak_hours": ["14:00-16:00", "19:00-21:00"],
        "most_active_days": ["Monday", "Wednesday", "Thursday"],
        "average_questions_per_session": 8.5,
        "completion_rates": {
            "beginner": 0.92,
            "intermediate": 0.78,
            "advanced": 0.65
        },
        "knowledge_component_popularity": {
            "Algebra": 85,
            "Geometry": 62,
            "Statistics": 43
        }
    }

# Comparative analytics
@router.get("/compare/students")
def compare_students(request, student_ids: List[int]):
    """Compare performance between multiple students"""
    # TODO: Implement student comparison analytics
    return {
        "comparison_data": [
            {"student_id": sid, "accuracy": 0.75 + (sid * 0.01), "progress": 0.6 + (sid * 0.02)}
            for sid in student_ids[:5]  # Limit to 5 students
        ],
        "average_performance": 0.78,
        "top_performer": student_ids[0] if student_ids else None,
        "improvement_suggestions": [
            "Focus on response time improvement",
            "Increase practice frequency",
            "Review fundamental concepts"
        ]
    }

@router.get("/knowledge-components/{kc_id}/analytics")
def get_knowledge_component_analytics(request, kc_id: int):
    """Get analytics for a specific knowledge component"""
    # TODO: Implement knowledge component analytics
    return {
        "knowledge_component_id": kc_id,
        "total_attempts": 250,
        "average_accuracy": 0.72,
        "average_time_to_master": 3.2,
        "difficulty_rating": 0.65,
        "student_performance_distribution": {
            "struggling": 15,
            "progressing": 45,
            "mastered": 40
        },
        "common_misconceptions": [
            "Confusing variable isolation",
            "Sign errors in equations"
        ]
    }

# Real-time analytics
@router.get("/realtime/active-users")
def get_active_users(request):
    """Get current active users and their activities"""
    # TODO: Implement real-time user tracking
    return {
        "active_users_count": 23,
        "current_sessions": [
            {
                "student_id": 1,
                "current_activity": "Solving algebra problems",
                "session_duration": 15.5,
                "questions_completed": 7
            }
        ],
        "system_load": "normal",
        "response_time_avg": 1.2
    }

@router.get("/status")
def analytics_status(request):
    """Analytics app status endpoint"""
    return {
        "app": "analytics", 
        "status": "ready", 
        "description": "Learning analytics and performance tracking",
        "features": [
            "Student Performance Tracking", 
            "Learning Progress Analytics", 
            "Personalized Recommendations",
            "System Metrics",
            "Real-time Analytics"
        ]
    }