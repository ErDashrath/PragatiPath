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
from django.urls import path
from ninja import NinjaAPI
from django.conf import settings
from django.conf.urls.static import static

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
from analytics.api import router as analytics_router
from practice.api import router as practice_router
from frontend_api import frontend_router

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
api.add_router("/student-model/", student_model_router, tags=["Student Model"])
api.add_router("/assessment/", assessment_router, tags=["Assessment"])
api.add_router("/competitive/", competitive_v1_router, tags=["Competitive Exam v1"])  # Direct competitive route
api.add_router("/enhanced/", enhanced_v2_router, tags=["AI-Enhanced Assessment v2"])
api.add_router("/user-sessions/", user_session_router, tags=["User Sessions"])
api.add_router("/students/", student_session_router, tags=["Student Sessions"])
api.add_router("/student-management/", student_router, tags=["Student Management"])
api.add_router("/multi-student/", multi_student_router, tags=["Multi-Student System"])
api.add_router("/analytics/", analytics_router, tags=["Analytics"])
api.add_router("/practice/", practice_router, tags=["Practice"])
api.add_router("/frontend/", frontend_router, tags=["Frontend API"])

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
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)