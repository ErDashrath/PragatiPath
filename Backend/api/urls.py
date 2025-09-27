"""
Clean JSON API URLs for Frontend Integration

This module defines all API endpoints that serve pure JSON responses
without any HTML/doctype content. Perfect for frontend consumption.

URL Structure:
/api/v1/auth/          - Authentication endpoints
/api/v1/content/       - Subject and content endpoints  
/api/v1/adaptive/      - Adaptive learning endpoints
/api/v1/students/      - Student dashboard endpoints
/api/v1/health/        - Health check endpoints

Author: AI Assistant
Date: 2024-12-26
"""

from django.urls import path, include
from api import frontend_api

# Authentication URLs
auth_patterns = [
    path('login/', frontend_api.student_login, name='student_login'),
    path('register/', frontend_api.student_register, name='student_register'),
]

# Content Management URLs
content_patterns = [
    path('subjects/', frontend_api.get_subjects, name='get_subjects'),
]

# Adaptive Learning URLs
adaptive_patterns = [
    path('session/start/', frontend_api.start_adaptive_session, name='start_adaptive_session'),
    path('session/<str:session_id>/question/', frontend_api.get_next_question, name='get_next_question'),
    path('session/submit-answer/', frontend_api.submit_answer, name='submit_answer'),
    path('session/<str:session_id>/analytics/', frontend_api.get_session_analytics, name='get_session_analytics'),
]

# Student Dashboard URLs
student_patterns = [
    path('<int:student_id>/dashboard/', frontend_api.get_student_dashboard, name='get_student_dashboard'),
]

# Main API v1 URL patterns
urlpatterns = [
    # CORS preflight handler
    path('v1/options/', frontend_api.cors_preflight, name='cors_preflight'),
    
    # Authentication endpoints
    path('v1/auth/', include(auth_patterns)),
    
    # Content management endpoints
    path('v1/content/', include(content_patterns)),
    
    # Adaptive learning endpoints
    path('v1/adaptive/', include(adaptive_patterns)),
    
    # Student dashboard endpoints
    path('v1/students/', include(student_patterns)),
    
    # Health check endpoint
    path('v1/health/', frontend_api.api_health_check, name='api_health_check'),
]