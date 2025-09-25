"""
User Session Management Models for Adaptive Learning System
Tracks user sessions, answered questions, subject progress, and timing information
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Define choices locally to avoid circular imports
SUBJECT_CHOICES = [
    ('quantitative_aptitude', 'Quantitative Aptitude'),
    ('logical_reasoning', 'Logical Reasoning'),
    ('data_interpretation', 'Data Interpretation'),
    ('verbal_ability', 'Verbal Ability'),
]

DIFFICULTY_CHOICES = [
    ('very_easy', 'Very Easy'),
    ('easy', 'Easy'),
    ('moderate', 'Moderate'),
    ('difficult', 'Difficult'),
]

class UserSession(models.Model):
    """
    Main session model tracking individual user study sessions
    """
    SESSION_TYPES = [
        ('PRACTICE', 'Practice Session'),
        ('MOCK_TEST', 'Mock Test'),
        ('CHAPTER_TEST', 'Chapter Test'),
        ('FULL_TEST', 'Full Subject Test'),
    ]
    
    SESSION_STATUS = [
        ('ACTIVE', 'Active Session'),
        ('PAUSED', 'Paused Session'),
        ('COMPLETED', 'Completed Session'),
        ('ABANDONED', 'Abandoned Session'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    
    # Session Configuration
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='PRACTICE')
    subject = models.CharField(max_length=25, choices=SUBJECT_CHOICES)
    chapter_number = models.IntegerField(null=True, blank=True, help_text="Specific chapter for chapter tests")
    
    # Session State
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='ACTIVE')
    current_question_index = models.IntegerField(default=0)
    
    # Timing Information
    session_start_time = models.DateTimeField(auto_now_add=True)
    session_end_time = models.DateTimeField(null=True, blank=True)
    total_duration_seconds = models.IntegerField(default=0)
    time_per_question = models.JSONField(default=list, help_text="List of time spent on each question")
    
    # Performance Tracking
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    current_score = models.FloatField(default=0.0)
    
    # Question Set Management
    question_ids_sequence = models.JSONField(default=list, help_text="Ordered list of question UUIDs for this session")
    answered_question_ids = models.JSONField(default=list, help_text="List of already answered question UUIDs")
    
    # Adaptive Learning State
    current_difficulty_level = models.CharField(
        max_length=15, 
        choices=DIFFICULTY_CHOICES, 
        default='easy'
    )
    mastery_scores_by_topic = models.JSONField(default=dict, help_text="Topic-wise mastery progression")
    
    # Metadata
    device_info = models.JSONField(default=dict, blank=True)
    browser_info = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session: {self.user.username} - {self.subject} ({self.session_type})"
    
    @property
    def accuracy_percentage(self):
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    @property
    def average_time_per_question(self):
        if not self.time_per_question:
            return 0.0
        return sum(self.time_per_question) / len(self.time_per_question)
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    def complete_session(self):
        """Mark session as completed and calculate final metrics"""
        self.status = 'COMPLETED'
        self.session_end_time = timezone.now()
        if self.session_start_time:
            duration = self.session_end_time - self.session_start_time
            self.total_duration_seconds = int(duration.total_seconds())
        self.save()
    
    def add_question_time(self, time_seconds):
        """Add time spent on current question"""
        if not isinstance(self.time_per_question, list):
            self.time_per_question = []
        self.time_per_question.append(time_seconds)
        self.save()
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['subject', 'session_type']),
            models.Index(fields=['session_start_time']),
            models.Index(fields=['status', 'updated_at']),
        ]
        ordering = ['-session_start_time']


class UserQuestionHistory(models.Model):
    """
    Detailed history of user interactions with specific questions
    """
    ANSWER_STATUS = [
        ('CORRECT', 'Correct Answer'),
        ('INCORRECT', 'Incorrect Answer'),
        ('SKIPPED', 'Question Skipped'),
        ('TIMEOUT', 'Timed Out'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_history')
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='question_interactions')
    question = models.ForeignKey('AdaptiveQuestion', on_delete=models.CASCADE, related_name='user_interactions')
    
    # Answer Details
    user_answer = models.CharField(max_length=5, blank=True, help_text="User's selected option (a/b/c/d)")
    correct_answer = models.CharField(max_length=5, help_text="Correct option (a/b/c/d)")
    answer_status = models.CharField(max_length=15, choices=ANSWER_STATUS)
    
    # Timing
    question_start_time = models.DateTimeField(auto_now_add=True)
    question_end_time = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.FloatField(default=0.0)
    
    # Context Information
    question_order_in_session = models.IntegerField(help_text="Order of this question in the session")
    difficulty_when_presented = models.CharField(
        max_length=15, 
        choices=DIFFICULTY_CHOICES,
        help_text="Difficulty level when question was presented to user"
    )
    
    # AI Features (for practice mode)
    hints_requested = models.IntegerField(default=0)
    explanation_viewed = models.BooleanField(default=False)
    confidence_level = models.IntegerField(
        choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')],
        null=True, blank=True
    )
    
    # Learning Analytics
    attempt_number = models.IntegerField(default=1, help_text="How many times user has seen this question")
    previous_attempts = models.JSONField(default=list, help_text="History of previous attempts on this question")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.question.question_text[:30]}... ({self.answer_status})"
    
    @property
    def is_correct(self):
        return self.answer_status == 'CORRECT'
    
    def save(self, *args, **kwargs):
        # Auto-calculate time spent if end time is set
        if self.question_end_time and not self.time_spent_seconds:
            duration = self.question_end_time - self.question_start_time
            self.time_spent_seconds = duration.total_seconds()
        
        # Auto-determine answer status based on correctness
        if self.user_answer and self.correct_answer and not self.answer_status:
            if self.user_answer.lower() == self.correct_answer.lower():
                self.answer_status = 'CORRECT'
            else:
                self.answer_status = 'INCORRECT'
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'user_question_history'
        verbose_name = 'User Question History'
        verbose_name_plural = 'User Question Histories'
        indexes = [
            models.Index(fields=['user', 'question']),
            models.Index(fields=['session', 'question_order_in_session']),
            models.Index(fields=['answer_status', 'created_at']),
            models.Index(fields=['user', 'answer_status']),
        ]
        ordering = ['-created_at']


class UserSubjectProgress(models.Model):
    """
    Tracks user's overall progress in each subject across all sessions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_progress')
    subject = models.CharField(max_length=25, choices=SUBJECT_CHOICES)
    
    # Progress Metrics
    total_questions_attempted = models.IntegerField(default=0)
    total_questions_correct = models.IntegerField(default=0)
    current_mastery_level = models.CharField(
        max_length=15, 
        choices=DIFFICULTY_CHOICES, 
        default='easy'
    )
    
    # Chapter-wise Progress
    chapter_progress = models.JSONField(default=dict, help_text="Progress per chapter {chapter_num: {attempted, correct, mastery_score}}")
    topic_mastery_scores = models.JSONField(default=dict, help_text="Mastery scores per topic")
    
    # Timing Statistics
    total_study_time_seconds = models.IntegerField(default=0)
    average_time_per_question = models.FloatField(default=0.0)
    total_sessions = models.IntegerField(default=0)
    
    # Performance Trends
    weekly_accuracy_trend = models.JSONField(default=list, help_text="Weekly accuracy percentages")
    difficulty_progression = models.JSONField(default=list, help_text="Historical difficulty level progression")
    
    # Streaks and Achievements
    current_correct_streak = models.IntegerField(default=0)
    longest_correct_streak = models.IntegerField(default=0)
    current_study_streak_days = models.IntegerField(default=0)
    longest_study_streak_days = models.IntegerField(default=0)
    
    # Last Activity
    last_session_date = models.DateTimeField(null=True, blank=True)
    last_question_answered = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} Progress"
    
    @property
    def overall_accuracy_percentage(self):
        if self.total_questions_attempted == 0:
            return 0.0
        return (self.total_questions_correct / self.total_questions_attempted) * 100
    
    @property
    def average_session_duration_minutes(self):
        if self.total_sessions == 0:
            return 0.0
        return (self.total_study_time_seconds / self.total_sessions) / 60
    
    def update_progress_from_session(self, session):
        """Update progress metrics after a session completion"""
        self.total_questions_attempted += session.questions_attempted
        self.total_questions_correct += session.questions_correct
        self.total_study_time_seconds += session.total_duration_seconds
        self.total_sessions += 1
        self.last_session_date = session.session_end_time or timezone.now()
        
        # Update average time per question
        if self.total_questions_attempted > 0:
            self.average_time_per_question = self.total_study_time_seconds / self.total_questions_attempted
        
        self.save()
    
    class Meta:
        db_table = 'user_subject_progress'
        verbose_name = 'User Subject Progress'
        verbose_name_plural = 'User Subject Progress'
        unique_together = ['user', 'subject']
        indexes = [
            models.Index(fields=['user', 'subject']),
            models.Index(fields=['subject', 'current_mastery_level']),
            models.Index(fields=['last_session_date']),
        ]


class UserDailyStats(models.Model):
    """
    Daily statistics for user activity and performance tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField(help_text="Date for these statistics")
    
    # Daily Metrics
    total_study_time_seconds = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    sessions_completed = models.IntegerField(default=0)
    
    # Subject-wise breakdown
    subject_time_distribution = models.JSONField(default=dict, help_text="Time spent per subject")
    subject_question_counts = models.JSONField(default=dict, help_text="Questions attempted per subject")
    
    # Achievement tracking
    new_topics_attempted = models.IntegerField(default=0)
    difficulty_levels_unlocked = models.JSONField(default=list)
    personal_bests = models.JSONField(default=list, help_text="Any personal bests achieved today")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} Stats"
    
    @property
    def accuracy_percentage(self):
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    @property
    def study_time_hours(self):
        return self.total_study_time_seconds / 3600
    
    class Meta:
        db_table = 'user_daily_stats'
        verbose_name = 'User Daily Stats'
        verbose_name_plural = 'User Daily Stats'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
        ordering = ['-date']