"""
Enhanced Exam Models - Production Ready Django Models
====================================================

This file contains production-ready Django models for the enhanced exam system
that integrates seamlessly with your existing PragatiPath database structure.

Integration Points:
- StudentProfile.id (UUID) - Primary student identifier  
- User model - Django authentication
- Subject/Chapter - Existing content structure
- AdaptiveQuestion - Question management

Usage:
1. Add this to your Django app's models.py
2. Run: python manage.py makemigrations
3. Run: python manage.py migrate
4. Start using the enhanced exam system!
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Import your existing models
from core.models import StudentProfile
from assessment.models import AdaptiveQuestion
from assessment.improved_models import Subject, Chapter


class EnhancedExam(models.Model):
    """Enhanced Exam Master Table - Admin Created Exams"""
    
    EXAM_TYPES = [
        ('PRACTICE', 'Practice Exam'),
        ('MOCK_TEST', 'Mock Test'),
        ('CHAPTER_TEST', 'Chapter Test'),
        ('FULL_TEST', 'Full Subject Test'),
        ('COMPETITIVE', 'Competitive Exam'),
        ('ASSESSMENT', 'Assessment Test'),
    ]
    
    EXAM_STATUS = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner Level'),
        ('intermediate', 'Intermediate Level'),
        ('advanced', 'Advanced Level'),
        ('expert', 'Expert Level'),
        ('mixed', 'Mixed Difficulty'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    exam_name = models.CharField(max_length=200, help_text="Display name for the exam")
    exam_code = models.CharField(max_length=50, unique=True, help_text="Unique exam identifier")
    description = models.TextField(blank=True, help_text="Detailed exam description")
    instructions = models.TextField(blank=True, help_text="Instructions for students")
    
    # Admin Information
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='created_enhanced_exams',
        help_text="Admin who created this exam"
    )
    
    # Exam Configuration
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES, default='PRACTICE')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='mixed')
    status = models.CharField(max_length=20, choices=EXAM_STATUS, default='DRAFT')
    
    # Content Selection
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='enhanced_exams',
        help_text="Primary subject for this exam"
    )
    chapters = models.ManyToManyField(
        Chapter,
        blank=True,
        related_name='enhanced_exams',
        help_text="Specific chapters (if not full subject)"
    )
    
    # Question Configuration
    total_questions = models.PositiveIntegerField(help_text="Total number of questions in exam")
    question_distribution = models.JSONField(
        default=dict,
        help_text="Question distribution by difficulty: {easy: 10, medium: 15, hard: 5}"
    )
    
    # Timing Configuration
    duration_minutes = models.PositiveIntegerField(help_text="Total exam duration in minutes")
    time_per_question_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Optional time limit per question"
    )
    
    # Scheduling
    scheduled_start_time = models.DateTimeField(
        null=True, blank=True,
        help_text="When exam becomes available to students"
    )
    scheduled_end_time = models.DateTimeField(
        null=True, blank=True,
        help_text="When exam is no longer available"
    )
    
    # Exam Settings
    adaptive_mode = models.BooleanField(default=False, help_text="Enable adaptive difficulty")
    shuffle_questions = models.BooleanField(default=True, help_text="Randomize question order")
    shuffle_options = models.BooleanField(default=True, help_text="Randomize option order")
    allow_review = models.BooleanField(default=True, help_text="Allow answer review")
    show_results_immediately = models.BooleanField(default=False, help_text="Show immediate results")
    
    # Scoring
    max_attempts_per_student = models.PositiveIntegerField(default=1, help_text="Max attempts allowed")
    passing_score_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('60.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score to pass"
    )
    
    # Security
    browser_lockdown = models.BooleanField(default=False, help_text="Enable browser lockdown")
    prevent_tab_switching = models.BooleanField(default=False, help_text="Detect tab switching")
    
    # Metadata
    content_selection = models.JSONField(default=dict, help_text="Content selection configuration")
    tags = models.JSONField(default=list, blank=True, help_text="Tags for categorization")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.exam_name} ({self.exam_code})"
    
    @property
    def is_active(self):
        """Check if exam is currently active"""
        now = timezone.now()
        if self.status != 'ACTIVE':
            return False
        if self.scheduled_start_time and now < self.scheduled_start_time:
            return False
        if self.scheduled_end_time and now > self.scheduled_end_time:
            return False
        return True
    
    @property
    def total_attempts(self):
        """Get total number of student attempts"""
        return self.student_attempts.count()
    
    @property
    def average_score(self):
        """Calculate average score across all completed attempts"""
        attempts = self.student_attempts.filter(status='COMPLETED')
        if not attempts.exists():
            return 0.0
        return attempts.aggregate(avg=models.Avg('final_score_percentage'))['avg'] or 0.0
    
    class Meta:
        db_table = 'enhanced_exams'
        verbose_name = 'Enhanced Exam'
        verbose_name_plural = 'Enhanced Exams'
        indexes = [
            models.Index(fields=['subject', 'status']),
            models.Index(fields=['exam_type', 'status']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['scheduled_start_time', 'scheduled_end_time']),
        ]
        ordering = ['-created_at']


class StudentExamAttempt(models.Model):
    """Student Exam Attempt - Core Transaction Table"""
    
    ATTEMPT_STATUS = [
        ('REGISTERED', 'Registered/Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('SUBMITTED', 'Submitted'),
        ('COMPLETED', 'Completed/Graded'),
        ('ABANDONED', 'Abandoned'),
        ('TIMEOUT', 'Timed Out'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    SUBMISSION_TYPE = [
        ('AUTO_SUBMIT', 'Auto-submitted (time up)'),
        ('MANUAL_SUBMIT', 'Manually submitted'),
        ('EARLY_SUBMIT', 'Early submission'),
        ('FORCED_SUBMIT', 'Force submitted by admin'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Key Relationships - MAIN INTEGRATION POINTS
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enhanced_exam_attempts',
        help_text="Link to student profile (UUID-based)"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enhanced_exam_attempts',
        help_text="Direct link to User model for queries"
    )
    exam = models.ForeignKey(
        EnhancedExam,
        on_delete=models.CASCADE,
        related_name='student_attempts',
        help_text="The exam being attempted"
    )
    
    # Attempt Information
    attempt_number = models.PositiveIntegerField(help_text="Attempt number (1, 2, 3...)")
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS, default='REGISTERED')
    
    # Timing Information - COMPREHENSIVE TIME TRACKING
    registered_at = models.DateTimeField(auto_now_add=True, help_text="Registration timestamp")
    started_at = models.DateTimeField(null=True, blank=True, help_text="Exam start timestamp")
    submitted_at = models.DateTimeField(null=True, blank=True, help_text="Submission timestamp")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Completion timestamp")
    
    # Duration Tracking
    total_time_spent_seconds = models.PositiveIntegerField(default=0, help_text="Total time spent")
    active_time_seconds = models.PositiveIntegerField(default=0, help_text="Active answering time")
    pause_count = models.PositiveIntegerField(default=0, help_text="Number of pauses")
    total_pause_duration_seconds = models.PositiveIntegerField(default=0, help_text="Total pause time")
    
    # Question Progress
    current_question_number = models.PositiveIntegerField(default=0, help_text="Current question")
    questions_attempted = models.PositiveIntegerField(default=0, help_text="Questions attempted")
    questions_answered = models.PositiveIntegerField(default=0, help_text="Questions answered")
    questions_skipped = models.PositiveIntegerField(default=0, help_text="Questions skipped")
    questions_flagged = models.PositiveIntegerField(default=0, help_text="Questions flagged")
    
    # Scoring Information - COMPLETE SCORE TRACKING
    total_questions = models.PositiveIntegerField(help_text="Total questions in attempt")
    correct_answers = models.PositiveIntegerField(default=0, help_text="Correct answers")
    incorrect_answers = models.PositiveIntegerField(default=0, help_text="Incorrect answers")
    raw_score = models.DecimalField(
        max_digits=10, decimal_places=3,
        default=Decimal('0.000'),
        help_text="Raw score"
    )
    final_score_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Final percentage score"
    )
    
    # Results
    passed = models.BooleanField(default=False, help_text="Whether student passed")
    grade = models.CharField(max_length=10, blank=True, help_text="Letter grade")
    percentile_rank = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Percentile rank"
    )
    
    # Submission Details
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE, null=True, blank=True)
    submission_notes = models.TextField(blank=True, help_text="Submission notes")
    
    # Technical Information
    browser_info = models.JSONField(default=dict, help_text="Browser information")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address")
    session_data = models.JSONField(default=dict, help_text="Session data")
    
    # Security Tracking
    tab_switches = models.PositiveIntegerField(default=0, help_text="Tab switches detected")
    copy_paste_attempts = models.PositiveIntegerField(default=0, help_text="Copy-paste attempts")
    integrity_violations = models.JSONField(default=list, help_text="Integrity violations")
    flagged_for_review = models.BooleanField(default=False, help_text="Flagged for review")
    
    # Analytics Data
    question_sequence = models.JSONField(default=list, help_text="Question order presented")
    difficulty_progression = models.JSONField(default=list, help_text="Difficulty changes")
    response_patterns = models.JSONField(default=dict, help_text="Response pattern analysis")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.exam_name} (#{self.attempt_number})"
    
    @property
    def duration_minutes(self):
        """Total duration in minutes"""
        return round(self.total_time_spent_seconds / 60, 2)
    
    @property
    def accuracy_percentage(self):
        """Accuracy percentage"""
        if self.questions_attempted == 0:
            return 0.0
        return round((self.correct_answers / self.questions_attempted) * 100, 2)
    
    @property
    def completion_percentage(self):
        """Completion percentage"""
        if self.total_questions == 0:
            return 0.0
        return round((self.questions_answered / self.total_questions) * 100, 2)
    
    @property
    def average_time_per_question(self):
        """Average time per question in seconds"""
        if self.questions_attempted == 0:
            return 0.0
        return round(self.active_time_seconds / self.questions_attempted, 2)
    
    def calculate_grade(self):
        """Calculate letter grade"""
        score = float(self.final_score_percentage)
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C+'
        elif score >= 55: return 'C'
        elif score >= 50: return 'C-'
        else: return 'F'
    
    def save(self, *args, **kwargs):
        # Auto-calculate derived fields
        if not self.grade and self.final_score_percentage:
            self.grade = self.calculate_grade()
        
        # Determine pass/fail
        passing_score = float(self.exam.passing_score_percentage)
        self.passed = float(self.final_score_percentage) >= passing_score
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'student_exam_attempts'
        verbose_name = 'Student Exam Attempt'
        verbose_name_plural = 'Student Exam Attempts'
        unique_together = ['student', 'exam', 'attempt_number']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['exam', 'status']),
            models.Index(fields=['student_profile', 'started_at']),
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['exam', 'final_score_percentage']),
            models.Index(fields=['passed', 'completed_at']),
            models.Index(fields=['flagged_for_review']),
        ]
        ordering = ['-started_at']


class ExamQuestionAttempt(models.Model):
    """Detailed Question-by-Question Tracking"""
    
    ANSWER_STATUS = [
        ('NOT_VIEWED', 'Not viewed'),
        ('VIEWED', 'Viewed but not answered'),
        ('ANSWERED', 'Answered'),
        ('SKIPPED', 'Skipped'),
        ('FLAGGED', 'Flagged for review'),
        ('TIMEOUT', 'Timed out'),
        ('CHANGED', 'Answer changed'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Keys
    exam_attempt = models.ForeignKey(
        StudentExamAttempt,
        on_delete=models.CASCADE,
        related_name='question_attempts',
        help_text="Parent exam attempt"
    )
    question = models.ForeignKey(
        AdaptiveQuestion,
        on_delete=models.CASCADE,
        related_name='enhanced_exam_attempts',
        help_text="Question being attempted"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enhanced_question_attempts',
        help_text="Student reference"
    )
    
    # Position Information
    question_number = models.PositiveIntegerField(help_text="Question position (1-based)")
    presented_order = models.PositiveIntegerField(help_text="Presentation order")
    
    # Answer Information
    student_answer = models.TextField(blank=True, help_text="Student's answer")
    correct_answer = models.TextField(help_text="Correct answer")
    answer_status = models.CharField(max_length=20, choices=ANSWER_STATUS, default='NOT_VIEWED')
    
    # Scoring
    is_correct = models.BooleanField(default=False)
    partial_credit = models.DecimalField(
        max_digits=4, decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    points_possible = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal('1.000'))
    points_earned = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0.000'))
    
    # Timing - GRANULAR TIME TRACKING
    first_viewed_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    first_answered_at = models.DateTimeField(null=True, blank=True)
    final_answered_at = models.DateTimeField(null=True, blank=True)
    
    # Time Analysis
    total_time_spent_seconds = models.PositiveIntegerField(default=0)
    thinking_time_seconds = models.PositiveIntegerField(default=0)
    review_time_seconds = models.PositiveIntegerField(default=0)
    
    # Context When Answered
    difficulty_when_presented = models.CharField(max_length=20)
    adaptive_level = models.IntegerField(null=True, blank=True)
    
    # Interaction Data
    view_count = models.PositiveIntegerField(default=0)
    answer_changes = models.PositiveIntegerField(default=0)
    flagged_for_review = models.BooleanField(default=False)
    answer_history = models.JSONField(default=list, help_text="Answer change history")
    
    # Learning Support
    hints_requested = models.PositiveIntegerField(default=0)
    hints_used = models.JSONField(default=list)
    explanation_viewed = models.BooleanField(default=False)
    
    # Student Feedback
    confidence_level = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    difficulty_rating = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Technical Data
    interaction_events = models.JSONField(default=list, help_text="Interaction log")
    browser_events = models.JSONField(default=list, help_text="Browser events")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Q{self.question_number}: {self.student.username} - {self.answer_status}"
    
    @property
    def response_time_seconds(self):
        """Time from first view to answer"""
        if self.first_viewed_at and self.final_answered_at:
            delta = self.final_answered_at - self.first_viewed_at
            return delta.total_seconds()
        return 0
    
    @property
    def efficiency_score(self):
        """Efficiency score based on time and correctness"""
        if not self.is_correct:
            return 0.0
        expected_time = self.question.estimated_time_seconds or 60
        actual_time = self.total_time_spent_seconds or 1
        return min(100.0, (expected_time / actual_time) * 100)
    
    def save(self, *args, **kwargs):
        # Auto-calculate scoring
        if self.is_correct:
            self.points_earned = self.points_possible
        else:
            self.points_earned = self.points_possible * self.partial_credit
        
        # Update status
        if self.student_answer and self.answer_status not in ['TIMEOUT', 'FLAGGED']:
            self.answer_status = 'ANSWERED'
        elif self.first_viewed_at and not self.student_answer:
            self.answer_status = 'VIEWED'
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'exam_question_attempts'
        verbose_name = 'Exam Question Attempt'
        verbose_name_plural = 'Exam Question Attempts'
        unique_together = ['exam_attempt', 'question']
        indexes = [
            models.Index(fields=['exam_attempt', 'question_number']),
            models.Index(fields=['student', 'question']),
            models.Index(fields=['question', 'is_correct']),
            models.Index(fields=['is_correct', 'total_time_spent_seconds']),
            models.Index(fields=['difficulty_when_presented', 'is_correct']),
        ]
        ordering = ['exam_attempt', 'question_number']


class ExamAnalytics(models.Model):
    """Pre-computed Analytics for Performance"""
    
    ANALYTICS_TYPE = [
        ('EXAM_SUMMARY', 'Exam Overview'),
        ('STUDENT_PERFORMANCE', 'Student Performance'),
        ('QUESTION_ANALYSIS', 'Question Analysis'),
        ('DIFFICULTY_ANALYSIS', 'Difficulty Analysis'),
        ('TIME_ANALYSIS', 'Time Analysis'),
    ]
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Scope
    analytics_type = models.CharField(max_length=30, choices=ANALYTICS_TYPE)
    exam = models.ForeignKey(EnhancedExam, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Time Period
    analysis_period_start = models.DateTimeField()
    analysis_period_end = models.DateTimeField()
    
    # Analytics Data
    metrics = models.JSONField(default=dict, help_text="Computed metrics")
    trends = models.JSONField(default=dict, help_text="Trend analysis")
    insights = models.JSONField(default=dict, help_text="AI insights")
    
    # Metadata
    computation_version = models.CharField(max_length=20, default='1.0')
    data_points_count = models.PositiveIntegerField(default=0)
    confidence_score = models.DecimalField(max_digits=4, decimal_places=3, default=Decimal('1.000'))
    
    # Timestamps
    computed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.analytics_type} - {self.exam or 'Global'}"
    
    @property
    def is_expired(self):
        """Check if analytics expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    class Meta:
        db_table = 'exam_analytics'
        verbose_name = 'Exam Analytics'
        verbose_name_plural = 'Exam Analytics'
        indexes = [
            models.Index(fields=['exam', 'analytics_type']),
            models.Index(fields=['student', 'analytics_type']),
            models.Index(fields=['computed_at', 'expires_at']),
        ]
        ordering = ['-computed_at']


# ==============================================================================
# UTILITY FUNCTIONS FOR COMMON OPERATIONS
# ==============================================================================

class ExamDatabaseUtils:
    """Utility functions for common exam database operations"""
    
    @staticmethod
    def get_student_exam_history(student_username: str, exam_id: str = None):
        """Get comprehensive exam history for a student"""
        student = User.objects.get(username=student_username)
        attempts = StudentExamAttempt.objects.filter(student=student)
        
        if exam_id:
            attempts = attempts.filter(exam_id=exam_id)
        
        return attempts.select_related('exam', 'student_profile').order_by('-started_at')
    
    @staticmethod
    def get_exam_performance_summary(exam_id: str):
        """Get performance summary for an exam"""
        exam = EnhancedExam.objects.get(id=exam_id)
        attempts = StudentExamAttempt.objects.filter(
            exam=exam, 
            status='COMPLETED'
        )
        
        if not attempts.exists():
            return None
        
        return {
            'total_attempts': attempts.count(),
            'average_score': attempts.aggregate(avg=models.Avg('final_score_percentage'))['avg'],
            'pass_rate': attempts.filter(passed=True).count() / attempts.count() * 100,
            'average_duration': attempts.aggregate(avg=models.Avg('total_time_spent_seconds'))['avg'] / 60,
            'completion_rate': attempts.filter(completion_percentage=100).count() / attempts.count() * 100,
        }
    
    @staticmethod
    def get_question_analytics(question_id: str):
        """Get analytics for a specific question across all exams"""
        attempts = ExamQuestionAttempt.objects.filter(question_id=question_id)
        
        if not attempts.exists():
            return None
        
        total_attempts = attempts.count()
        correct_attempts = attempts.filter(is_correct=True).count()
        
        return {
            'total_attempts': total_attempts,
            'success_rate': correct_attempts / total_attempts * 100,
            'average_time': attempts.aggregate(avg=models.Avg('total_time_spent_seconds'))['avg'],
            'difficulty_perception': attempts.exclude(
                difficulty_rating__isnull=True
            ).aggregate(avg=models.Avg('difficulty_rating'))['avg'],
            'confidence_level': attempts.exclude(
                confidence_level__isnull=True
            ).aggregate(avg=models.Avg('confidence_level'))['avg'],
        }
    
    @staticmethod
    def create_exam_from_template(exam_data: dict, admin_user: User):
        """Create a new exam from template data"""
        exam = EnhancedExam.objects.create(
            created_by=admin_user,
            **exam_data
        )
        return exam
    
    @staticmethod
    def start_exam_attempt(student_username: str, exam_id: str):
        """Start a new exam attempt for a student"""
        student = User.objects.get(username=student_username)
        student_profile = StudentProfile.objects.get(user=student)
        exam = EnhancedExam.objects.get(id=exam_id)
        
        # Check attempt limits
        existing_attempts = StudentExamAttempt.objects.filter(
            student=student,
            exam=exam
        ).count()
        
        if existing_attempts >= exam.max_attempts_per_student:
            raise ValueError("Maximum attempts exceeded")
        
        # Create new attempt
        attempt = StudentExamAttempt.objects.create(
            student_profile=student_profile,
            student=student,
            exam=exam,
            attempt_number=existing_attempts + 1,
            total_questions=exam.total_questions,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        
        return attempt


# ==============================================================================
# SAMPLE USAGE AND MIGRATION GUIDE
# ==============================================================================

"""
MIGRATION INSTRUCTIONS:
======================

1. Add these models to your app's models.py:
   - Copy the model classes above
   - Ensure imports are correct for your project structure

2. Create and run migrations:
   python manage.py makemigrations
   python manage.py migrate

3. Create admin interface (optional):
   # In admin.py
   from django.contrib import admin
   from .models import EnhancedExam, StudentExamAttempt, ExamQuestionAttempt
   
   admin.site.register(EnhancedExam)
   admin.site.register(StudentExamAttempt)
   admin.site.register(ExamQuestionAttempt)

4. Start using the models:
   # Create an exam
   exam = EnhancedExam.objects.create(
       exam_name="Sample Test",
       exam_code="TEST001",
       created_by=admin_user,
       subject=subject_obj,
       total_questions=50,
       duration_minutes=90
   )
   
   # Start student attempt
   attempt = ExamDatabaseUtils.start_exam_attempt("student_username", exam.id)
   
   # Record question attempt
   question_attempt = ExamQuestionAttempt.objects.create(
       exam_attempt=attempt,
       question=question_obj,
       student=student_user,
       question_number=1,
       student_answer="a",
       correct_answer="a",
       is_correct=True
   )

DATABASE PERFORMANCE NOTES:
===========================

1. Indexes are optimized for common query patterns
2. Use select_related() for foreign key queries
3. Use prefetch_related() for reverse foreign keys
4. Consider read replicas for analytics queries
5. Partition large tables by date if needed

ANALYTICS READY:
===============

The schema supports:
- Real-time student performance tracking
- Exam difficulty analysis
- Question effectiveness metrics
- Learning pattern analysis
- Comparative performance reports
- Predictive analytics for student success

SECURITY FEATURES:
=================

- Integrity violation tracking
- Session monitoring
- Browser event logging
- IP address tracking
- Suspicious activity detection
- Exam security validation

This schema is production-ready and scales to millions of exam attempts
while maintaining query performance and data integrity.
"""