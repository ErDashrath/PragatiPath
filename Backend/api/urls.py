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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import enhanced_exam_session_api

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

# Enhanced Exam Management URLs
enhanced_exam_patterns = [
    path('admin/subjects/details/', frontend_api.enhanced_subjects_details, name='enhanced_subjects_details'),
    path('admin/subjects/<int:subject_id>/chapters/', frontend_api.enhanced_subject_chapters, name='enhanced_subject_chapters'),
    path('admin/exams/validate-question-pool/', frontend_api.validate_question_pool, name='validate_question_pool'),
    path('admin/exams/create-enhanced/', frontend_api.create_enhanced_exam, name='create_enhanced_exam'),
    path('admin/exams/enhanced/list/', frontend_api.list_enhanced_exams, name='list_enhanced_exams'),
    path('student/<str:student_id>/exams/enhanced/', frontend_api.get_student_enhanced_exams, name='get_student_enhanced_exams'),
    
    # NEW: Exam Broadcasting & Management Endpoints
    path('admin/exams/schedule/', frontend_api.schedule_enhanced_exam, name='schedule_enhanced_exam'),
    path('admin/exams/scheduled/', frontend_api.get_scheduled_exams, name='get_scheduled_exams'),
    path('admin/exams/<str:exam_id>/activate/', frontend_api.activate_exam_manual, name='activate_exam_manual'),
    path('admin/exams/<str:exam_id>/end/', frontend_api.end_exam_manual, name='end_exam_manual'),
    path('admin/subjects/with-ids/', frontend_api.get_subjects_with_ids, name='get_subjects_with_ids'),
    path('student/<str:student_id>/exams/scheduled/', frontend_api.get_student_scheduled_exams, name='get_student_scheduled_exams'),
    
    # NEW: Enhanced Exam Session Management (Student Exam Taking with Adaptive Learning)
    path('exams/<str:exam_id>/join/', enhanced_exam_session_api.join_enhanced_exam, name='join_enhanced_exam'),
    path('sessions/<str:session_id>/question/', enhanced_exam_session_api.get_exam_question, name='get_enhanced_exam_question'),
    path('sessions/<str:session_id>/submit-answer/', enhanced_exam_session_api.submit_exam_answer, name='submit_enhanced_exam_answer'),
    path('sessions/<str:session_id>/submit/', enhanced_exam_session_api.submit_exam, name='submit_enhanced_exam'),
    path('sessions/<str:session_id>/results/', enhanced_exam_session_api.get_exam_results, name='get_enhanced_exam_results'),
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
    
    # Enhanced exam management endpoints
    path('v1/enhanced-exam/', include(enhanced_exam_patterns)),
    
    # Health check endpoint
    path('v1/health/', frontend_api.api_health_check, name='api_health_check'),
]