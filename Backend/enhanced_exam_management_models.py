"""
Enhanced Exam Models for Industry-Standard Exam Management
Supports scheduling, broadcasting, notifications, and comprehensive analytics
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

from core.models import StudentProfile
from assessment.models import Subject, Chapter


class ExamStatus(models.TextChoices):
    """Standard exam status choices"""
    DRAFT = 'DRAFT', 'Draft'
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    ACTIVE = 'ACTIVE', 'Active'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    EXPIRED = 'EXPIRED', 'Expired'


class ExamType(models.TextChoices):
    """Types of exams"""
    PRACTICE = 'PRACTICE', 'Practice'
    ASSESSMENT = 'ASSESSMENT', 'Assessment'
    MIDTERM = 'MIDTERM', 'Midterm'
    FINAL = 'FINAL', 'Final'
    QUIZ = 'QUIZ', 'Quiz'
    MOCK = 'MOCK', 'Mock Test'


class NotificationType(models.TextChoices):
    """Types of exam notifications"""
    EXAM_SCHEDULED = 'EXAM_SCHEDULED', 'Exam Scheduled'
    EXAM_REMINDER = 'EXAM_REMINDER', 'Exam Reminder'
    EXAM_STARTED = 'EXAM_STARTED', 'Exam Started'
    EXAM_ENDING_SOON = 'EXAM_ENDING_SOON', 'Exam Ending Soon'
    EXAM_ENDED = 'EXAM_ENDED', 'Exam Ended'
    RESULTS_AVAILABLE = 'RESULTS_AVAILABLE', 'Results Available'


class EnhancedExam(models.Model):
    """
    Enhanced exam model with industry-standard features:
    - Flexible scheduling
    - Multi-chapter content selection
    - Adaptive difficulty
    - Comprehensive analytics
    - Student enrollment management
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_code = models.CharField(max_length=50, unique=True, db_index=True)
    exam_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Content Configuration
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enhanced_exams')
    chapters = models.ManyToManyField(Chapter, blank=True, related_name='enhanced_exams')
    
    # Exam Type and Configuration
    exam_type = models.CharField(max_length=20, choices=ExamType.choices, default=ExamType.PRACTICE)
    difficulty_level = models.CharField(max_length=20, default='mixed')
    
    # Scheduling
    scheduled_start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    scheduled_end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(480)]  # 5 minutes to 8 hours
    )
    
    # Question Configuration
    total_questions = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    question_distribution = models.JSONField(default=dict, help_text="Difficulty-wise question distribution")
    
    # Content Selection Configuration
    content_selection = models.JSONField(default=dict, help_text="Chapter and content selection configuration")
    
    # Enrollment and Access Control
    auto_assign_all_active = models.BooleanField(default=True, help_text="Auto-enroll all active students")
    max_attempts_per_student = models.PositiveIntegerField(default=1)
    
    # Exam Behavior Settings
    randomize_questions = models.BooleanField(default=True)
    allow_question_navigation = models.BooleanField(default=True)
    show_question_feedback = models.BooleanField(default=False)
    allow_question_review = models.BooleanField(default=True)
    auto_submit_on_expiry = models.BooleanField(default=True)
    
    # Proctoring and Security
    proctoring_enabled = models.BooleanField(default=False)
    allow_browser_navigation = models.BooleanField(default=False)
    require_fullscreen = models.BooleanField(default=True)
    
    # Analytics and Reporting
    detailed_analytics = models.BooleanField(default=True)
    generate_performance_report = models.BooleanField(default=True)
    
    # Grading Configuration
    passing_score = models.FloatField(
        default=60.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=ExamStatus.choices, default=ExamStatus.DRAFT)
    metadata = models.JSONField(default=dict, help_text="Additional exam metadata and settings")
    
    # Adaptive Learning Integration
    adaptive_config = models.JSONField(
        default=dict, 
        help_text="BKT/DKT adaptive learning configuration"
    )
    
    # Timestamps and Tracking
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')
    
    class Meta:
        db_table = 'enhanced_exams'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_start_time']),
            models.Index(fields=['subject', 'status']),
            models.Index(fields=['created_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.exam_name} ({self.subject.name})"
    
    @property
    def is_active(self):
        """Check if exam is currently active"""
        now = timezone.now()
        return (self.status == ExamStatus.ACTIVE and
                (not self.scheduled_start_time or self.scheduled_start_time <= now) and
                (not self.scheduled_end_time or self.scheduled_end_time >= now))
    
    @property
    def is_upcoming(self):
        """Check if exam is upcoming"""
        now = timezone.now()
        return (self.status == ExamStatus.SCHEDULED and
                self.scheduled_start_time and
                self.scheduled_start_time > now)
    
    @property
    def is_expired(self):
        """Check if exam has expired"""
        now = timezone.now()
        return (self.scheduled_end_time and 
                self.scheduled_end_time < now and
                self.status != ExamStatus.COMPLETED)
    
    @property
    def enrolled_students_count(self):
        """Get count of enrolled students"""
        if self.auto_assign_all_active:
            return User.objects.filter(
                is_active=True,
                student_profile__isnull=False
            ).count()
        else:
            return len(self.metadata.get('enrolled_students', []))
    
    def can_student_attempt(self, student):
        """Check if student can attempt this exam"""
        if not self.is_active:
            return False, "Exam is not currently active"
        
        # Check enrollment
        if not self.auto_assign_all_active:
            enrolled_ids = self.metadata.get('enrolled_students', [])
            if str(student.id) not in enrolled_ids:
                return False, "You are not enrolled in this exam"
        
        # Check attempt limits
        existing_attempts = self.student_attempts.filter(student=student).count()
        if existing_attempts >= self.max_attempts_per_student:
            return False, f"Maximum attempts ({self.max_attempts_per_student}) reached"
        
        return True, "Can attempt"
    
    def get_time_remaining(self):
        """Get time remaining for exam in minutes"""
        if not self.scheduled_end_time:
            return None
        
        now = timezone.now()
        if now >= self.scheduled_end_time:
            return 0
        
        return int((self.scheduled_end_time - now).total_seconds() / 60)


class StudentExamAttempt(models.Model):
    """
    Individual student exam attempts with comprehensive tracking
    """
    
    class AttemptStatus(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        AUTO_SUBMITTED = 'AUTO_SUBMITTED', 'Auto Submitted'
        TIMED_OUT = 'TIMED_OUT', 'Timed Out'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    exam = models.ForeignKey(EnhancedExam, on_delete=models.CASCADE, related_name='student_attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts')
    student_profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_attempts')
    
    # Attempt Tracking
    attempt_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=AttemptStatus.choices, default=AttemptStatus.IN_PROGRESS)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    total_time_minutes = models.FloatField(null=True, blank=True)
    
    # Question and Answer Tracking
    total_questions = models.PositiveIntegerField()
    questions_attempted = models.PositiveIntegerField(default=0)
    questions_answered = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    
    # Scoring and Grading
    raw_score = models.FloatField(null=True, blank=True)
    final_score_percentage = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=5, null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    # Detailed Analytics
    answer_details = models.JSONField(default=dict, help_text="Detailed answer tracking and analytics")
    performance_metrics = models.JSONField(default=dict, help_text="Performance analytics and insights")
    
    # Adaptive Learning Data
    adaptive_data = models.JSONField(default=dict, help_text="BKT/DKT learning analytics")
    
    # Browser and Behavior Tracking
    session_data = models.JSONField(default=dict, help_text="Session behavior and integrity data")
    
    class Meta:
        db_table = 'student_exam_attempts'
        ordering = ['-started_at']
        unique_together = ['exam', 'student', 'attempt_number']
        indexes = [
            models.Index(fields=['exam', 'student']),
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['student', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.exam_name} (Attempt {self.attempt_number})"
    
    @property
    def is_active(self):
        """Check if attempt is currently active"""
        return self.status == self.AttemptStatus.IN_PROGRESS
    
    @property
    def time_elapsed_minutes(self):
        """Get elapsed time in minutes"""
        if not self.started_at:
            return 0
        
        end_time = self.submitted_at or timezone.now()
        return (end_time - self.started_at).total_seconds() / 60
    
    @property
    def time_remaining_minutes(self):
        """Get remaining time in minutes"""
        if not self.is_active:
            return 0
        
        elapsed = self.time_elapsed_minutes
        return max(0, self.exam.duration_minutes - elapsed)
    
    def calculate_final_score(self):
        """Calculate and update final score"""
        if self.total_questions == 0:
            return 0
        
        percentage = (self.correct_answers / self.total_questions) * 100
        self.final_score_percentage = percentage
        self.passed = percentage >= self.exam.passing_score
        
        # Grade assignment
        if percentage >= 95:
            self.grade = 'A+'
        elif percentage >= 90:
            self.grade = 'A'
        elif percentage >= 85:
            self.grade = 'A-'
        elif percentage >= 80:
            self.grade = 'B+'
        elif percentage >= 75:
            self.grade = 'B'
        elif percentage >= 70:
            self.grade = 'B-'
        elif percentage >= 65:
            self.grade = 'C+'
        elif percentage >= 60:
            self.grade = 'C'
        elif percentage >= 55:
            self.grade = 'D+'
        elif percentage >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        
        self.save(update_fields=['final_score_percentage', 'grade', 'passed'])
        return percentage


class ExamNotification(models.Model):
    """
    Exam-related notifications for students and admins
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    exam = models.ForeignKey(EnhancedExam, on_delete=models.CASCADE, related_name='notifications')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_notifications', null=True, blank=True)
    
    # Notification Details
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status and Tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority and Urgency
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium'
    )
    
    # Delivery Tracking
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_method = models.CharField(
        max_length=20,
        choices=[('websocket', 'WebSocket'), ('email', 'Email'), ('sms', 'SMS'), ('push', 'Push')],
        default='websocket'
    )
    
    # Metadata
    metadata = models.JSONField(default=dict, help_text="Additional notification data")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'exam_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_read']),
            models.Index(fields=['exam', 'notification_type']),
            models.Index(fields=['created_at', 'priority']),
        ]
    
    def __str__(self):
        recipient = self.student.username if self.student else "All"
        return f"{self.title} -> {recipient}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class ExamAnalytics(models.Model):
    """
    Comprehensive exam analytics and insights
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.OneToOneField(EnhancedExam, on_delete=models.CASCADE, related_name='analytics')
    
    # Participation Metrics
    total_enrolled = models.PositiveIntegerField(default=0)
    total_started = models.PositiveIntegerField(default=0)
    total_completed = models.PositiveIntegerField(default=0)
    total_auto_submitted = models.PositiveIntegerField(default=0)
    
    # Performance Metrics
    average_score = models.FloatField(null=True, blank=True)
    median_score = models.FloatField(null=True, blank=True)
    highest_score = models.FloatField(null=True, blank=True)
    lowest_score = models.FloatField(null=True, blank=True)
    
    # Time Analytics
    average_completion_time = models.FloatField(null=True, blank=True)
    median_completion_time = models.FloatField(null=True, blank=True)
    
    # Grade Distribution
    grade_distribution = models.JSONField(default=dict, help_text="Distribution of grades")
    
    # Question-wise Analytics
    question_analytics = models.JSONField(default=dict, help_text="Per-question performance analytics")
    
    # Difficulty Analysis
    difficulty_analysis = models.JSONField(default=dict, help_text="Difficulty-wise performance analysis")
    
    # Chapter-wise Analysis
    chapter_analytics = models.JSONField(default=dict, help_text="Chapter-wise performance analysis")
    
    # Adaptive Learning Insights
    adaptive_insights = models.JSONField(default=dict, help_text="BKT/DKT learning insights")
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_analytics'
    
    def __str__(self):
        return f"Analytics for {self.exam.exam_name}"
    
    def calculate_analytics(self):
        """Calculate and update all analytics"""
        attempts = self.exam.student_attempts.filter(status='COMPLETED')
        
        if not attempts.exists():
            return
        
        # Basic metrics
        self.total_enrolled = self.exam.enrolled_students_count
        self.total_started = self.exam.student_attempts.count()
        self.total_completed = attempts.count()
        self.total_auto_submitted = self.exam.student_attempts.filter(status='AUTO_SUBMITTED').count()
        
        # Score analytics
        scores = list(attempts.values_list('final_score_percentage', flat=True))
        if scores:
            self.average_score = sum(scores) / len(scores)
            sorted_scores = sorted(scores)
            self.median_score = sorted_scores[len(sorted_scores) // 2]
            self.highest_score = max(scores)
            self.lowest_score = min(scores)
        
        # Time analytics
        completion_times = [
            attempt.total_time_minutes for attempt in attempts 
            if attempt.total_time_minutes
        ]
        if completion_times:
            self.average_completion_time = sum(completion_times) / len(completion_times)
            sorted_times = sorted(completion_times)
            self.median_completion_time = sorted_times[len(sorted_times) // 2]
        
        # Grade distribution
        grades = attempts.values_list('grade', flat=True)
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        self.grade_distribution = grade_counts
        
        self.save()


class ExamSession(models.Model):
    """
    Live exam session tracking for real-time monitoring
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(EnhancedExam, on_delete=models.CASCADE, related_name='live_sessions')
    
    # Session Status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Live Statistics
    current_participants = models.PositiveIntegerField(default=0)
    peak_participants = models.PositiveIntegerField(default=0)
    
    # Real-time Metrics
    live_metrics = models.JSONField(default=dict, help_text="Real-time exam metrics")
    
    # System Health
    system_status = models.JSONField(default=dict, help_text="System health and performance")
    
    class Meta:
        db_table = 'exam_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Live Session: {self.exam.exam_name}"