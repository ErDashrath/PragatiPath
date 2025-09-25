"""
Comprehensive Database Schema for Multi-Student Session Management
Proper primary keys, foreign keys, and relationships for scalable student management
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Define choices to avoid circular imports
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

SESSION_TYPE_CHOICES = [
    ('PRACTICE', 'Practice Session'),
    ('CHAPTER_TEST', 'Chapter Test'),
    ('MOCK_TEST', 'Mock Test'),
    ('FULL_TEST', 'Full Subject Test'),
    ('ASSESSMENT', 'Assessment Test'),
]

SESSION_STATUS_CHOICES = [
    ('ACTIVE', 'Active Session'),
    ('PAUSED', 'Paused Session'),
    ('COMPLETED', 'Completed Session'),
    ('ABANDONED', 'Abandoned Session'),
]

ANSWER_STATUS_CHOICES = [
    ('CORRECT', 'Correct Answer'),
    ('INCORRECT', 'Incorrect Answer'),
    ('SKIPPED', 'Question Skipped'),
    ('TIMEOUT', 'Timed Out'),
    ('NOT_ATTEMPTED', 'Not Attempted'),
]

class Subject(models.Model):
    """
    Master table for subjects - Reference data
    Primary Key: Auto-increment ID
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, choices=SUBJECT_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]


class Chapter(models.Model):
    """
    Master table for chapters within subjects
    Primary Key: Auto-increment ID
    Foreign Key: Subject
    """
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    chapter_number = models.IntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.name} - Chapter {self.chapter_number}: {self.name}"
    
    class Meta:
        db_table = 'chapters'
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
        unique_together = ['subject', 'chapter_number']
        indexes = [
            models.Index(fields=['subject', 'chapter_number']),
            models.Index(fields=['is_active']),
        ]


class StudentSession(models.Model):
    """
    Central table for student study sessions
    Primary Key: UUID
    Foreign Keys: User (Student), Subject, Chapter (optional)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Key Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='improved_study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True, 
                               related_name='sessions', help_text="Specific chapter for chapter tests")
    
    # Session Configuration
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='PRACTICE')
    session_name = models.CharField(max_length=200, blank=True, help_text="Custom session name")
    
    # Session State Management
    status = models.CharField(max_length=15, choices=SESSION_STATUS_CHOICES, default='ACTIVE')
    current_question_number = models.IntegerField(default=0, help_text="Current question position in session")
    total_questions_planned = models.IntegerField(default=10, help_text="Total questions planned for this session")
    
    # Timing Information
    session_start_time = models.DateTimeField(auto_now_add=True)
    session_end_time = models.DateTimeField(null=True, blank=True)
    session_duration_seconds = models.IntegerField(default=0)
    time_limit_minutes = models.IntegerField(null=True, blank=True, help_text="Session time limit")
    
    # Performance Tracking
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    questions_incorrect = models.IntegerField(default=0)
    questions_skipped = models.IntegerField(default=0)
    questions_timeout = models.IntegerField(default=0)
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    max_possible_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    
    # Adaptive Learning State
    current_difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='easy')
    difficulty_adjustments = models.JSONField(default=list, help_text="History of difficulty adjustments")
    
    # Session Configuration Data
    session_config = models.JSONField(default=dict, help_text="Session-specific configuration")
    question_sequence = models.JSONField(default=list, help_text="Ordered list of question IDs")
    
    # Metadata
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.student.username} - {self.subject.name} ({self.session_type})"
    
    @property
    def accuracy_percentage(self):
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    @property
    def duration_minutes(self):
        return self.session_duration_seconds / 60 if self.session_duration_seconds else 0
    
    def calculate_final_score(self):
        """Calculate and update final session score"""
        self.percentage_score = self.accuracy_percentage
        if self.max_possible_score > 0:
            self.total_score = (self.questions_correct / self.total_questions_planned) * self.max_possible_score
        self.save()
    
    def complete_session(self):
        """Mark session as completed and finalize metrics"""
        self.status = 'COMPLETED'
        self.session_end_time = timezone.now()
        if self.session_start_time:
            duration = self.session_end_time - self.session_start_time
            self.session_duration_seconds = int(duration.total_seconds())
        self.calculate_final_score()
        self.save()
    
    class Meta:
        db_table = 'student_sessions'
        verbose_name = 'Student Session'
        verbose_name_plural = 'Student Sessions'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['subject', 'session_type']),
            models.Index(fields=['session_start_time']),
            models.Index(fields=['status', 'updated_at']),
            models.Index(fields=['student', 'subject', 'status']),
        ]
        ordering = ['-session_start_time']


class QuestionAttempt(models.Model):
    """
    Detailed record of each question attempt within a session
    Primary Key: Auto-increment ID
    Foreign Keys: StudentSession, AdaptiveQuestion, User (for direct access)
    """
    id = models.BigAutoField(primary_key=True)  # Use BigAutoField for high volume
    
    # Foreign Key Relationships
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey('AdaptiveQuestion', on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_attempts')
    
    # Question Position in Session
    question_number_in_session = models.IntegerField(help_text="Position of this question in the session")
    attempt_number = models.IntegerField(default=1, help_text="Attempt number if question repeated")
    
    # Answer Details
    student_answer = models.CharField(max_length=10, blank=True, help_text="Student's answer (a/b/c/d or text)")
    correct_answer = models.CharField(max_length=10, help_text="Correct answer for reference")
    answer_status = models.CharField(max_length=15, choices=ANSWER_STATUS_CHOICES, default='NOT_ATTEMPTED')
    is_correct = models.BooleanField(default=False)
    
    # Timing Information
    question_displayed_at = models.DateTimeField(auto_now_add=True)
    answer_submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.FloatField(default=0.0)
    time_limit_seconds = models.IntegerField(null=True, blank=True)
    
    # Question Context When Attempted
    difficulty_when_presented = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES)
    question_points = models.FloatField(default=1.0, help_text="Points assigned to this question")
    points_earned = models.FloatField(default=0.0, help_text="Points earned by student")
    
    # Learning Support Features
    hints_requested = models.IntegerField(default=0)
    hints_used = models.JSONField(default=list, help_text="List of hints used")
    explanation_viewed = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False, help_text="Student bookmarked for review")
    
    # Student Confidence and Feedback
    confidence_level = models.IntegerField(
        null=True, blank=True,
        choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')],
        help_text="Student's confidence level (1-5)"
    )
    student_feedback = models.TextField(blank=True, help_text="Optional student feedback on question")
    
    # Analytics Data
    interaction_data = models.JSONField(default=dict, help_text="Detailed interaction analytics")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Attempt {self.id} - {self.student.username} - Q{self.question_number_in_session} ({self.answer_status})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate fields
        if self.answer_submitted_at and not self.time_spent_seconds:
            duration = self.answer_submitted_at - self.question_displayed_at
            self.time_spent_seconds = duration.total_seconds()
        
        # Determine correctness
        if self.student_answer and self.correct_answer:
            self.is_correct = self.student_answer.lower().strip() == self.correct_answer.lower().strip()
            if self.answer_status == 'NOT_ATTEMPTED':
                self.answer_status = 'CORRECT' if self.is_correct else 'INCORRECT'
        
        # Calculate points earned
        if self.is_correct:
            self.points_earned = self.question_points
        else:
            self.points_earned = 0.0
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'question_attempts'
        verbose_name = 'Question Attempt'
        verbose_name_plural = 'Question Attempts'
        unique_together = ['session', 'question', 'attempt_number']
        indexes = [
            models.Index(fields=['session', 'question_number_in_session']),
            models.Index(fields=['student', 'question']),
            models.Index(fields=['answer_status', 'created_at']),
            models.Index(fields=['student', 'is_correct']),
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['question', 'is_correct']),
        ]
        ordering = ['-created_at']


class StudentProgress(models.Model):
    """
    Aggregate progress tracking per student per subject
    Primary Key: Auto-increment ID
    Foreign Keys: User (Student), Subject
    Unique Together: Student + Subject
    """
    id = models.AutoField(primary_key=True)
    
    # Foreign Key Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_progress')
    
    # Aggregate Statistics
    total_sessions = models.IntegerField(default=0)
    total_questions_attempted = models.IntegerField(default=0)
    total_questions_correct = models.IntegerField(default=0)
    total_study_time_seconds = models.BigIntegerField(default=0)
    
    # Performance Metrics
    current_accuracy_percentage = models.FloatField(default=0.0)
    best_accuracy_percentage = models.FloatField(default=0.0)
    current_mastery_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='easy')
    mastery_score = models.FloatField(default=0.0, help_text="Overall mastery score (0-100)")
    
    # Chapter-wise Progress
    chapter_progress = models.JSONField(default=dict, help_text="Progress per chapter")
    chapter_mastery_scores = models.JSONField(default=dict, help_text="Mastery scores per chapter")
    unlocked_chapters = models.JSONField(default=list, help_text="List of unlocked chapter IDs")
    
    # Streaks and Achievements
    current_correct_streak = models.IntegerField(default=0)
    longest_correct_streak = models.IntegerField(default=0)
    current_study_streak_days = models.IntegerField(default=0)
    longest_study_streak_days = models.IntegerField(default=0)
    
    # Learning Analytics
    learning_velocity = models.FloatField(default=0.0, help_text="Questions per hour")
    difficulty_progression = models.JSONField(default=list, help_text="Historical difficulty progression")
    performance_trend = models.JSONField(default=list, help_text="Performance trend over time")
    
    # Last Activity Tracking
    last_session_date = models.DateTimeField(null=True, blank=True)
    last_question_answered_at = models.DateTimeField(null=True, blank=True)
    last_active_chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.subject.name} Progress"
    
    @property
    def average_session_duration_minutes(self):
        if self.total_sessions == 0:
            return 0.0
        return (self.total_study_time_seconds / self.total_sessions) / 60
    
    @property
    def questions_per_session(self):
        if self.total_sessions == 0:
            return 0.0
        return self.total_questions_attempted / self.total_sessions
    
    def update_from_session(self, session):
        """Update progress from completed session"""
        self.total_sessions += 1
        self.total_questions_attempted += session.questions_attempted
        self.total_questions_correct += session.questions_correct
        self.total_study_time_seconds += session.session_duration_seconds
        
        # Update accuracy
        if self.total_questions_attempted > 0:
            self.current_accuracy_percentage = (self.total_questions_correct / self.total_questions_attempted) * 100
            self.best_accuracy_percentage = max(self.best_accuracy_percentage, self.current_accuracy_percentage)
        
        # Update last activity
        self.last_session_date = session.session_end_time or timezone.now()
        if session.chapter:
            self.last_active_chapter = session.chapter
        
        # Update learning velocity
        if self.total_study_time_seconds > 0:
            hours = self.total_study_time_seconds / 3600
            self.learning_velocity = self.total_questions_attempted / hours
        
        self.save()
    
    class Meta:
        db_table = 'student_progress'
        verbose_name = 'Student Progress'
        verbose_name_plural = 'Student Progress Records'
        unique_together = ['student', 'subject']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['subject', 'mastery_score']),
            models.Index(fields=['last_session_date']),
            models.Index(fields=['current_mastery_level']),
        ]


class DailyStudyStats(models.Model):
    """
    Daily aggregated statistics per student
    Primary Key: Auto-increment ID
    Foreign Keys: User (Student)
    Unique Together: Student + Date
    """
    id = models.AutoField(primary_key=True)
    
    # Foreign Key Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='improved_daily_stats')
    study_date = models.DateField(help_text="Date for these statistics")
    
    # Daily Metrics
    total_sessions = models.IntegerField(default=0)
    total_study_time_seconds = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    sessions_completed = models.IntegerField(default=0)
    
    # Subject-wise Breakdown
    subject_time_distribution = models.JSONField(default=dict, help_text="Time spent per subject")
    subject_question_counts = models.JSONField(default=dict, help_text="Questions per subject")
    subject_accuracy_rates = models.JSONField(default=dict, help_text="Accuracy per subject")
    
    # Achievement Tracking
    new_chapters_unlocked = models.IntegerField(default=0)
    difficulty_levels_progressed = models.JSONField(default=list, help_text="Difficulty progressions today")
    personal_bests = models.JSONField(default=list, help_text="Personal bests achieved")
    streaks_maintained = models.JSONField(default=dict, help_text="Streaks maintained")
    
    # Performance Summary
    daily_accuracy_percentage = models.FloatField(default=0.0)
    peak_performance_time = models.TimeField(null=True, blank=True, help_text="Time of best performance")
    focus_duration_minutes = models.IntegerField(default=0, help_text="Continuous focused study time")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.study_date}"
    
    @property
    def study_time_hours(self):
        return self.total_study_time_seconds / 3600
    
    @property
    def questions_per_minute(self):
        if self.total_study_time_seconds == 0:
            return 0.0
        return (self.questions_attempted * 60) / self.total_study_time_seconds
    
    class Meta:
        db_table = 'daily_study_stats'
        verbose_name = 'Daily Study Stats'
        verbose_name_plural = 'Daily Study Stats'
        unique_together = ['student', 'study_date']
        indexes = [
            models.Index(fields=['student', 'study_date']),
            models.Index(fields=['study_date']),
            models.Index(fields=['daily_accuracy_percentage']),
        ]
        ordering = ['-study_date']


# Database Constraints and Triggers (to be implemented)
class DatabaseConstraints:
    """
    Documentation of database-level constraints and business rules
    """
    
    CONSTRAINTS = {
        'session_integrity': [
            "questions_attempted >= questions_correct + questions_incorrect + questions_skipped",
            "percentage_score BETWEEN 0 AND 100",
            "session_duration_seconds >= 0",
            "current_question_number <= total_questions_planned"
        ],
        
        'question_attempt_integrity': [
            "time_spent_seconds >= 0",
            "question_points >= 0",
            "points_earned BETWEEN 0 AND question_points",
            "confidence_level BETWEEN 1 AND 5 OR confidence_level IS NULL"
        ],
        
        'progress_integrity': [
            "total_questions_attempted >= total_questions_correct",
            "current_accuracy_percentage BETWEEN 0 AND 100",
            "mastery_score BETWEEN 0 AND 100",
            "current_correct_streak >= 0",
            "learning_velocity >= 0"
        ],
        
        'daily_stats_integrity': [
            "total_study_time_seconds >= 0",
            "questions_attempted >= questions_correct",
            "daily_accuracy_percentage BETWEEN 0 AND 100",
            "focus_duration_minutes >= 0"
        ]
    }
    
    INDEXES = {
        'performance_indexes': [
            "CREATE INDEX idx_student_session_perf ON student_sessions (student_id, status, session_start_time)",
            "CREATE INDEX idx_question_attempt_perf ON question_attempts (student_id, created_at, is_correct)",
            "CREATE INDEX idx_progress_lookup ON student_progress (student_id, subject_id, mastery_score)",
            "CREATE INDEX idx_daily_stats_range ON daily_study_stats (student_id, study_date, daily_accuracy_percentage)"
        ]
    }
    
    FOREIGN_KEY_CASCADE_RULES = {
        'student_deletion': 'CASCADE - All student data deleted',
        'session_deletion': 'CASCADE - All attempts in session deleted',
        'subject_deletion': 'PROTECT - Cannot delete if students have progress',
        'chapter_deletion': 'PROTECT - Cannot delete if referenced in sessions',
        'question_deletion': 'PROTECT - Cannot delete if attempted by students'
    }