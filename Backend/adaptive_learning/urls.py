"""
URL configuration for adaptive_learning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from django.conf import settings
from django.conf.urls.static import static

# Import simple frontend API - direct import since it's at Backend root
import simple_frontend_api

# Import enhanced history API
import enhanced_history_api_fixed as enhanced_history_api

# Import adaptive session API
from assessment import adaptive_session_api

# Import admin API
import admin_api

# Import app routers
from core.api import router as core_router
from student_model.api import router as student_model_router
from assessment.api import router as assessment_router
from assessment.competitive_api_v1 import router as competitive_v1_router
from assessment.enhanced_api_v2 import router as enhanced_v2_router
from assessment.user_session_api import user_session_router
from assessment.student_session_api import student_session_router
from assessment.student_management_api import student_router
from assessment.multi_student_api import multi_student_router
from assessment.assessment_api import assessment_router as full_assessment_router
from assessment.history_api import history_router
from assessment.adaptive_api import adaptive_router
from orchestration.api import orchestration_router
from orchestration.frontend_api import frontend_orchestration_router
from analytics.api import router as analytics_router
from practice.api import router as practice_router
from frontend_api import frontend_router
from assessment.reports_api import reports_router

# Import exam management API
from exam_management_api import exam_router

# Import enhanced exam management API (NEW)
from enhanced_exam_management_api import enhanced_exam_router

# Create the main API instance with enhanced configuration
api = NinjaAPI(
    title="Adaptive Learning System API",
    version="1.0.0",
    description="API for Adaptive Learning System with BKT/DKT algorithms, SRS, and analytics",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add all app routers - Fixed duplicate issue
api.add_router("/core/", core_router, tags=["Core"])
api.add_router("/admin/", admin_api.admin_router, tags=["Admin"])
api.add_router("/student-model/", student_model_router, tags=["Student Model"])
api.add_router("/assessment/", assessment_router, tags=["Assessment"])
api.add_router("/competitive/", competitive_v1_router, tags=["Competitive Exam v1"])  # Direct competitive route
api.add_router("/enhanced/", enhanced_v2_router, tags=["AI-Enhanced Assessment v2"])
api.add_router("/user-sessions/", user_session_router, tags=["User Sessions"])
api.add_router("/students/", student_session_router, tags=["Student Sessions"])
api.add_router("/student-management/", student_router, tags=["Student Management"])
api.add_router("/multi-student/", multi_student_router, tags=["Multi-Student System"])
api.add_router("/full-assessment/", full_assessment_router, tags=["Complete Assessment System"])
api.add_router("/history/", history_router, tags=["Assessment History"])
api.add_router("/adaptive/", adaptive_router, tags=["Adaptive BKT/DKT System"])
api.add_router("/orchestration/", orchestration_router, tags=["LangGraph Orchestration"])
api.add_router("/frontend-orchestration/", frontend_orchestration_router, tags=["Frontend-Compatible Orchestration"])
api.add_router("/analytics/", analytics_router, tags=["Analytics"])
api.add_router("/practice/", practice_router, tags=["Practice"])
api.add_router("/frontend/", frontend_router, tags=["Frontend API"])
api.add_router("/reports/", reports_router, tags=["Reports & Analytics"])
api.add_router("/exams/", exam_router, tags=["Exam Management"])
api.add_router("/enhanced-exam/", enhanced_exam_router, tags=["Enhanced Exam Management"])

@api.get("/health", tags=["System"])
def health_check(request):
    """Health check endpoint"""
    return {
        "status": "ok", 
        "message": "Adaptive Learning System is running",
        "version": "1.0.0"
    }

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    
    # Production Frontend API (Clean JSON Only)
    path('api/', include('api.urls')),
    
    # Enhanced Adaptive Learning API with Mastery Tracking
    path('api/v1/adaptive/', include('api.adaptive_urls')),
    
    # Simple Direct Frontend API Endpoints
    path('simple/start-session/', simple_frontend_api.start_simple_session, name='start_simple_session'),
    path('simple/get-question/<str:session_id>/', simple_frontend_api.get_simple_question, name='get_simple_question'),
    path('simple/submit-answer/', simple_frontend_api.submit_simple_answer, name='submit_simple_answer'),
    path('simple/complete-session/', simple_frontend_api.complete_session, name='complete_session'),
    path('simple/session-progress/<str:session_id>/', simple_frontend_api.get_session_progress, name='get_session_progress'),
    path('simple/session-history/<str:student_id>/', simple_frontend_api.get_session_history, name='get_session_history'),
    path('simple/practice-history/<str:student_id>/', simple_frontend_api.get_unified_practice_history, name='get_unified_practice_history'),
    path('simple/health/', simple_frontend_api.api_health, name='simple_api_health'),
    # Enhanced History API Endpoints
    path('history/student/<str:username>/', enhanced_history_api.get_student_session_history, name='student_session_history'),
    path('history/adaptive-analytics/<str:username>/', enhanced_history_api.get_adaptive_learning_analytics, name='adaptive_analytics'),
    path('history/session-details/<str:session_id>/', enhanced_history_api.get_session_details, name='session_details'),
    
    # Adaptive Session API Endpoints (Production-Ready BKT/DKT System)
    path('adaptive-session/start/', adaptive_session_api.start_adaptive_session, name='start_adaptive_session'),
    path('adaptive-session/next-question/<str:session_id>/', adaptive_session_api.get_next_question, name='get_next_question'),
    path('adaptive-session/submit-answer/', adaptive_session_api.submit_answer, name='submit_answer'),
    path('adaptive-session/session-summary/<str:session_id>/', adaptive_session_api.get_session_summary, name='get_session_summary'),
    path('adaptive-session/student-mastery/<int:student_id>/', adaptive_session_api.get_student_mastery, name='get_student_mastery'),
    path('adaptive-session/available-subjects/', adaptive_session_api.get_available_subjects, name='get_available_subjects'),
    path('adaptive-session/end-session/<str:session_id>/', adaptive_session_api.end_session, name='end_session'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)