"""
URL Configuration for Enhanced Exam Management System
Provides comprehensive routing for exam scheduling, monitoring, and administration
"""

from django.urls import path, include
from django.views.generic import TemplateView

# Import API views (adjust imports based on your project structure)
from .enhanced_exam_api import (
    schedule_exam, get_scheduled_exams, activate_exam, end_exam,
    get_exam_notifications, mark_notification_read,
    get_student_exams, start_exam_attempt, submit_exam_answer,
    finish_exam_attempt, get_exam_results
)

from .enhanced_admin_monitoring_api import (
    exam_monitoring_view, exam_live_stats_view, exam_student_progress_view,
    activate_exam_view, end_exam_view, exam_analytics_view
)

# API URL patterns
api_patterns = [
    # Admin Exam Management
    path('admin/exams/schedule/', schedule_exam, name='schedule_exam'),
    path('admin/exams/scheduled/', get_scheduled_exams, name='get_scheduled_exams'),
    path('admin/exams/<int:exam_id>/activate/', activate_exam, name='activate_exam'),
    path('admin/exams/<int:exam_id>/end/', end_exam, name='end_exam'),
    
    # Admin Monitoring Dashboard
    path('admin/exams/monitoring/', exam_monitoring_view, name='exam_monitoring'),
    path('admin/exams/<int:exam_id>/live-stats/', exam_live_stats_view, name='exam_live_stats'),
    path('admin/exams/<int:exam_id>/student-progress/', exam_student_progress_view, name='exam_student_progress'),
    path('admin/exams/<int:exam_id>/analytics/', exam_analytics_view, name='exam_analytics'),
    
    # Manual Control Endpoints
    path('admin/exams/<int:exam_id>/activate/', activate_exam_view, name='manual_activate_exam'),
    path('admin/exams/<int:exam_id>/end/', end_exam_view, name='manual_end_exam'),
    
    # Notification Management
    path('admin/exams/notifications/', get_exam_notifications, name='get_exam_notifications'),
    path('admin/exams/notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    
    # Student Exam Access
    path('student/exams/', get_student_exams, name='get_student_exams'),
    path('student/exams/<int:exam_id>/start/', start_exam_attempt, name='start_exam_attempt'),
    path('student/exams/<int:exam_id>/submit/', submit_exam_answer, name='submit_exam_answer'),
    path('student/exams/<int:exam_id>/finish/', finish_exam_attempt, name='finish_exam_attempt'),
    path('student/exams/<int:exam_id>/results/', get_exam_results, name='get_exam_results'),
]

# WebSocket URL patterns (if using Django Channels)
websocket_patterns = [
    path('ws/exam-monitoring/<int:exam_id>/', 'enhanced_admin_monitoring_api.ExamMonitoringConsumer.as_asgi()', name='exam_monitoring_ws'),
    path('ws/exam-notifications/', 'exam_broadcasting_service.ExamNotificationConsumer.as_asgi()', name='exam_notifications_ws'),
]

# Main URL patterns
urlpatterns = [
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Frontend routes (if serving from Django)
    path('admin/dashboard/', TemplateView.as_view(template_name='admin/dashboard.html'), name='admin_dashboard'),
    path('admin/exam-management/', TemplateView.as_view(template_name='admin/exam_management.html'), name='admin_exam_management'),
    path('admin/exam-monitoring/', TemplateView.as_view(template_name='admin/exam_monitoring.html'), name='admin_exam_monitoring'),
    
    path('student/dashboard/', TemplateView.as_view(template_name='student/dashboard.html'), name='student_dashboard'),
    path('student/exams/', TemplateView.as_view(template_name='student/exams.html'), name='student_exams'),
    path('student/exam/<int:exam_id>/', TemplateView.as_view(template_name='student/exam_interface.html'), name='student_exam_interface'),
]

# Additional URL patterns for development/testing
if __name__ == '__main__':
    print("🔗 Enhanced Exam Management URL Configuration")
    print("📋 Available API Endpoints:")
    print("\n📊 Admin Management:")
    for pattern in api_patterns:
        if 'admin' in str(pattern.pattern):
            print(f"   {pattern.pattern} -> {pattern.name}")
    
    print("\n👨‍🎓 Student Access:")
    for pattern in api_patterns:
        if 'student' in str(pattern.pattern):
            print(f"   {pattern.pattern} -> {pattern.name}")
    
    print("\n🔌 WebSocket Endpoints:")
    for pattern in websocket_patterns:
        print(f"   {pattern.pattern} -> {pattern.name}")

# Export for use in main urls.py
__all__ = ['urlpatterns', 'api_patterns', 'websocket_patterns']