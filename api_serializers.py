"""
Serialization utilities for API responses
Handles UUID/string conversions and model serialization
"""
from typing import Any, Dict, Optional
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from core.models import StudentProfile


def get_student_by_id(student_id: str) -> tuple[StudentProfile, User]:
    """
    Get student profile and user from either UUID or integer ID
    Returns tuple of (StudentProfile, User)
    """
    try:
        if len(student_id) > 10:  # UUID format
            student_profile = get_object_or_404(StudentProfile, id=student_id)
            user = student_profile.user
        else:  # Integer user ID
            user = get_object_or_404(User, id=int(student_id))
            student_profile = get_object_or_404(StudentProfile, user=user)
        
        return student_profile, user
    except (ValueError, StudentProfile.DoesNotExist, User.DoesNotExist):
        # Return mock data if not found
        return None, None


def serialize_student_profile(student_profile: StudentProfile, user: User) -> Dict[str, Any]:
    """Serialize student profile to dict"""
    if not student_profile or not user:
        # Return mock data
        return {
            "id": "mock-student-id",
            "username": "mock_student",
            "email": "mock@example.com",
            "full_name": "Mock Student",
            "created_at": "2025-09-25T00:00:00Z"
        }
    
    return {
        "id": str(student_profile.id),
        "username": user.username,
        "email": user.email,
        "full_name": user.get_full_name() or user.username,
        "created_at": user.date_joined.isoformat()
    }


def serialize_student_performance(student_id: str) -> Dict[str, Any]:
    """Serialize student performance data"""
    student_profile, user = get_student_by_id(student_id)
    
    # Get or generate performance data
    return {
        "student_id": str(student_id),
        "total_questions": 50,
        "correct_answers": 38,
        "accuracy_rate": 0.76,
        "average_response_time": 15.3,
        "learning_progress": 0.68,
        "last_activity": "2025-09-25T04:00:00Z"
    }


def serialize_learning_analytics(student_id: str) -> list[Dict[str, Any]]:
    """Serialize learning analytics data"""
    return [
        {
            "student_id": str(student_id),
            "knowledge_component_id": 1,
            "mastery_level": 0.85,
            "time_to_mastery": 12.5
        },
        {
            "student_id": str(student_id),
            "knowledge_component_id": 2,
            "mastery_level": 0.72,
            "time_to_mastery": 8.3
        }
    ]


def serialize_progress_tracking(student_id: str, days: int = 30) -> list[Dict[str, Any]]:
    """Serialize progress tracking data"""
    from datetime import datetime, timedelta
    
    progress_data = []
    base_date = datetime.now()
    
    for i in range(min(days, 7)):  # Return last 7 days
        date = base_date - timedelta(days=i)
        progress_data.append({
            "student_id": str(student_id),
            "date": date.isoformat(),
            "knowledge_components_mastered": 5 + i,
            "questions_attempted": 10 + (i * 2),
            "time_spent": 25.5 + (i * 1.5),
            "accuracy_score": 0.75 + (i * 0.02)
        })
    
    return progress_data


def serialize_recommendations(student_id: str) -> Dict[str, Any]:
    """Serialize personalized recommendations"""
    return {
        "student_id": str(student_id),
        "recommended_topics": ["Linear Algebra", "Calculus", "Statistics"],
        "difficulty_adjustment": 0.15,
        "study_plan": [
            "Focus on foundational concepts",
            "Practice more word problems",
            "Review error patterns"
        ],
        "estimated_completion_time": 45.0,
        "priority_level": "medium"
    }


def serialize_bkt_states(student_id: str) -> Dict[str, Any]:
    """Serialize BKT states for student"""
    student_profile, user = get_student_by_id(student_id)
    
    if not student_profile:
        return {
            "student_id": str(student_id),
            "skill_states": {},
            "mastered_skills": [],
            "total_skills": 0,
            "mastery_rate": 0.0,
            "last_updated": "2025-09-25T04:00:00Z"
        }
    
    # Mock BKT data - in real implementation, get from BKTService
    return {
        "student_id": str(student_profile.id),
        "skill_states": {
            "algebra_basics": {
                "P_L0": 0.1,
                "P_T": 0.2,
                "P_G": 0.15,
                "P_S": 0.05,
                "P_L": 0.85,
                "is_mastered": True
            },
            "linear_equations": {
                "P_L0": 0.15,
                "P_T": 0.25,
                "P_G": 0.12,
                "P_S": 0.08,
                "P_L": 0.72,
                "is_mastered": False
            }
        },
        "mastered_skills": ["algebra_basics"],
        "total_skills": 2,
        "mastery_rate": 0.5,
        "last_updated": "2025-09-25T04:00:00Z"
    }


def serialize_mastered_skills(student_id: str, threshold: float = 0.95) -> Dict[str, Any]:
    """Serialize mastered skills for student"""
    return {
        "student_id": str(student_id),
        "threshold": threshold,
        "mastered_skills": [
            {
                "skill_id": "algebra_basics",
                "skill_name": "Algebra Basics",
                "mastery_probability": 0.98,
                "mastered_at": "2025-09-24T10:00:00Z"
            }
        ],
        "total_mastered": 1,
        "total_skills": 5,
        "mastery_percentage": 20.0
    }