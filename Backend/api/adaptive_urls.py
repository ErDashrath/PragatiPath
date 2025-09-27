"""
URL configuration for enhanced adaptive frontend API
"""
from django.urls import path
from . import adaptive_frontend_api
from . import test_views
from . import minimal_adaptive

app_name = 'adaptive_api'

urlpatterns = [
    # Core adaptive learning endpoints
    path('next-question/', adaptive_frontend_api.get_next_adaptive_question, name='next-question'),
    path('submit-answer/', adaptive_frontend_api.submit_answer_with_mastery_update, name='submit-answer'),
    
    # Real-time mastery tracking
    path('mastery/status/', adaptive_frontend_api.get_real_time_mastery, name='mastery-status'),
    path('mastery/dashboard/', adaptive_frontend_api.get_mastery_dashboard, name='mastery-dashboard'),
    
    # Debug endpoints
    path('test-imports/', test_views.test_imports, name='test-imports'),
    path('test-adaptive/', test_views.test_simple_adaptive, name='test-adaptive'),
    path('minimal-question/', minimal_adaptive.minimal_next_question, name='minimal-question'),
]