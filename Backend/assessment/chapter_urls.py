from django.urls import path
from . import chapter_views

app_name = 'chapters'

urlpatterns = [
    # Chapter-specific endpoints
    path('subjects-with-chapters/', chapter_views.list_subjects_with_chapters, name='subjects_with_chapters'),
    path('chapter-questions/', chapter_views.get_chapter_questions, name='chapter_questions'),
    path('chapter-stats/<str:subject>/<int:chapter_id>/', chapter_views.get_chapter_stats, name='chapter_stats'),
    path('submit-chapter-answer/', chapter_views.submit_chapter_answer, name='submit_chapter_answer'),
]