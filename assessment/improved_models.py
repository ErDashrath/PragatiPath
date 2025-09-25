"""
Improved Database Models for Multi-Student Adaptive Learning System
Production-ready with proper primary keys, foreign key relationships, and data isolation per student
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Subject(models.Model):
    """Master table for subjects - shared across all students"""
    SUBJECT_CHOICES = [
        ('quantitative_aptitude', 'Quantitative Aptitude'),
        ('logical_reasoning', 'Logical Reasoning'),
        ('data_interpretation', 'Data Interpretation'),
        ('verbal_ability', 'Verbal Ability'),
    ]
    
    id = models.AutoField(primary_key=True)  # Explicit primary key
    code = models.CharField(max_length=50, unique=True, choices=SUBJECT_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return self.name


class Chapter(models.Model):
    """Chapters within subjects - shared across all students"""
    id = models.AutoField(primary_key=True)  # Explicit primary key
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    chapter_number = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chapters'
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        constraints = [
            models.UniqueConstraint(fields=['subject', 'chapter_number'], name='unique_chapter_per_subject')
        ]
        indexes = [
            models.Index(fields=['subject', 'chapter_number']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - Chapter {self.chapter_number}: {self.name}"


class StudentSession(models.Model):
    """Individual study sessions for each student with proper isolation"""
    SESSION_TYPES = [
        ('PRACTICE', 'Practice Session'),
        ('CHAPTER_TEST', 'Chapter Test'),
        ('MOCK_TEST', 'Mock Test'),
        ('FULL_TEST', 'Full Subject Test'),
        ('ASSESSMENT', 'Assessment Test'),
    ]
    
    SESSION_STATUS = [
        ('ACTIVE', 'Active Session'),
        ('PAUSED', 'Paused Session'),
        ('COMPLETED', 'Completed Session'),
        ('ABANDONED', 'Abandoned Session'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('very_easy', 'Very Easy'),
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ]
    
    # Primary key and relationships
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sessions', 
                               null=True, blank=True)
    
    # Session configuration
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='PRACTICE')
    session_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='ACTIVE')
    
    # Session progress
    current_question_number = models.IntegerField(default=0)
    total_questions_planned = models.IntegerField(default=10)
    
    # Session timing
    session_start_time = models.DateTimeField(auto_now_add=True)
    session_end_time = models.DateTimeField(null=True, blank=True)
    session_duration_seconds = models.IntegerField(default=0)
    time_limit_minutes = models.IntegerField(null=True, blank=True)
    
    # Session statistics
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    questions_incorrect = models.IntegerField(default=0)
    questions_skipped = models.IntegerField(default=0)
    questions_timeout = models.IntegerField(default=0)
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    max_possible_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    
    # Adaptive features
    current_difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='easy')
    difficulty_adjustments = models.JSONField(default=list)
    
    # Session metadata
    session_config = models.JSONField(default=dict)
    question_sequence = models.JSONField(default=list)  # IDs of questions in order
    
    # Technical metadata
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_sessions'
        verbose_name = 'Student Session'
        verbose_name_plural = 'Student Sessions'
        ordering = ['-session_start_time']
        indexes = [
            models.Index(fields=['student', 'status'], name='idx_student_status'),
            models.Index(fields=['subject', 'session_type'], name='idx_subject_type'),
            models.Index(fields=['student', 'subject', 'status'], name='idx_student_subject_status'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.session_type}"


class QuestionAttempt(models.Model):
    """Individual question attempts within sessions - proper isolation per student"""
    ANSWER_STATUS_CHOICES = [
        ('CORRECT', 'Correct Answer'),
        ('INCORRECT', 'Incorrect Answer'),
        ('SKIPPED', 'Question Skipped'),
        ('TIMEOUT', 'Timed Out'),
        ('NOT_ATTEMPTED', 'Not Attempted'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('very_easy', 'Very Easy'),
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ]
    
    CONFIDENCE_CHOICES = [
        (1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')
    ]
    
    # Primary key (auto-incrementing for performance)
    id = models.BigAutoField(primary_key=True)
    
    # Foreign key relationships - proper isolation
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, 
                               related_name='question_attempts')
    question = models.ForeignKey('AdaptiveQuestion', on_delete=models.CASCADE, 
                                related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='question_attempts')
    
    # Question sequencing
    question_number_in_session = models.IntegerField()
    attempt_number = models.IntegerField(default=1)
    
    # Answer tracking
    student_answer = models.CharField(max_length=10, blank=True)
    correct_answer = models.CharField(max_length=10)
    answer_status = models.CharField(max_length=15, choices=ANSWER_STATUS_CHOICES, 
                                    default='NOT_ATTEMPTED')
    is_correct = models.BooleanField(default=False)
    
    # Timing information
    question_displayed_at = models.DateTimeField(auto_now_add=True)
    answer_submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.FloatField(default=0.0)
    time_limit_seconds = models.IntegerField(null=True, blank=True)
    
    # Question difficulty and scoring
    difficulty_when_presented = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES)
    question_points = models.FloatField(default=1.0)
    points_earned = models.FloatField(default=0.0)
    
    # Learning features
    hints_requested = models.IntegerField(default=0)
    hints_used = models.JSONField(default=list)
    explanation_viewed = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    confidence_level = models.IntegerField(
        null=True, blank=True,
        choices=CONFIDENCE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Feedback and metadata
    student_feedback = models.TextField(blank=True)
    interaction_data = models.JSONField(default=dict)  # Mouse movements, focus changes, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_attempts'
        verbose_name = 'Question Attempt'
        verbose_name_plural = 'Question Attempts'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['session', 'question', 'attempt_number'], 
                                   name='unique_question_attempt')
        ]
        indexes = [
            models.Index(fields=['session', 'question_number_in_session'], name='idx_session_question_num'),
            models.Index(fields=['student', 'is_correct'], name='idx_student_correct'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - Q{self.question_number_in_session} - {self.answer_status}"


class StudentProgress(models.Model):
    """Track student progress per subject with proper isolation"""
    DIFFICULTY_CHOICES = [
        ('very_easy', 'Very Easy'),
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ]
    
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Foreign key relationships - proper isolation
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='progress_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, 
                               related_name='student_progress')
    last_active_chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, 
                                          null=True, blank=True)
    
    # Overall statistics
    total_sessions = models.IntegerField(default=0)
    total_questions_attempted = models.IntegerField(default=0)
    total_questions_correct = models.IntegerField(default=0)
    total_study_time_seconds = models.BigIntegerField(default=0)
    
    # Accuracy tracking
    current_accuracy_percentage = models.FloatField(default=0.0)
    best_accuracy_percentage = models.FloatField(default=0.0)
    
    # Mastery levels
    current_mastery_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='easy')
    mastery_score = models.FloatField(default=0.0)
    
    # Chapter-wise progress
    chapter_progress = models.JSONField(default=dict)  # {chapter_id: progress_percentage}
    chapter_mastery_scores = models.JSONField(default=dict)  # {chapter_id: mastery_score}
    unlocked_chapters = models.JSONField(default=list)  # [chapter_id, ...]
    
    # Streaks and engagement
    current_correct_streak = models.IntegerField(default=0)
    longest_correct_streak = models.IntegerField(default=0)
    current_study_streak_days = models.IntegerField(default=0)
    longest_study_streak_days = models.IntegerField(default=0)
    
    # Learning analytics
    learning_velocity = models.FloatField(default=0.0)  # Questions mastered per hour
    difficulty_progression = models.JSONField(default=list)  # Historical difficulty levels
    performance_trend = models.JSONField(default=list)  # Recent performance data
    
    # Last activity tracking
    last_session_date = models.DateTimeField(null=True, blank=True)
    last_question_answered_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_progress'
        verbose_name = 'Student Progress'
        verbose_name_plural = 'Student Progress Records'
        constraints = [
            models.UniqueConstraint(fields=['student', 'subject'], name='unique_student_subject_progress')
        ]
        indexes = [
            models.Index(fields=['student', 'subject'], name='idx_progress_lookup'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.subject.name} Progress"


class DailyStudyStats(models.Model):
    """Daily activity statistics per student with proper isolation"""
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Foreign key relationships - proper isolation
    student = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='daily_stats')
    
    # Date tracking
    study_date = models.DateField()
    
    # Daily statistics
    total_sessions = models.IntegerField(default=0)
    total_study_time_seconds = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    sessions_completed = models.IntegerField(default=0)
    
    # Subject-wise breakdown
    subject_time_distribution = models.JSONField(default=dict)  # {subject_id: seconds}
    subject_question_counts = models.JSONField(default=dict)   # {subject_id: count}
    subject_accuracy_rates = models.JSONField(default=dict)    # {subject_id: percentage}
    
    # Achievement tracking
    new_chapters_unlocked = models.IntegerField(default=0)
    difficulty_levels_progressed = models.JSONField(default=list)
    personal_bests = models.JSONField(default=list)  # List of achievements today
    streaks_maintained = models.JSONField(default=dict)
    
    # Performance metrics
    daily_accuracy_percentage = models.FloatField(default=0.0)
    peak_performance_time = models.TimeField(null=True, blank=True)
    focus_duration_minutes = models.IntegerField(default=0)  # Total focused study time
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_study_stats'
        verbose_name = 'Daily Study Stats'
        verbose_name_plural = 'Daily Study Stats'
        ordering = ['-study_date']
        constraints = [
            models.UniqueConstraint(fields=['student', 'study_date'], name='unique_daily_stats')
        ]
        indexes = [
            models.Index(fields=['student', 'study_date'], name='idx_daily_lookup'),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.study_date}"