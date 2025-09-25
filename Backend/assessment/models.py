import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Import user session models (legacy)
from .user_session_models import UserSession, UserQuestionHistory, UserSubjectProgress, UserDailyStats

# Import improved multi-student models
from .improved_models import (
    Subject, Chapter, StudentSession, QuestionAttempt, 
    StudentProgress, DailyStudyStats
)

class AdaptiveQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('numerical', 'Numerical'),
        ('matching', 'Matching'),
    ]
    
    FUNDAMENTAL_TYPES = [
        ('listening', 'Listening'),
        ('grasping', 'Grasping'), 
        ('retention', 'Retention'),
        ('application', 'Application'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('very_easy', 'Very Easy'),
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
    ]
    
    SUBJECT_CHOICES = [
        ('quantitative_aptitude', 'Quantitative Aptitude'),
        ('logical_reasoning', 'Logical Reasoning'),
        ('data_interpretation', 'Data Interpretation'),
        ('verbal_ability', 'Verbal Ability'),
    ]
    
    ANSWER_CHOICES = [
        ('a', 'Option A'),
        ('b', 'Option B'),
        ('c', 'Option C'),
        ('d', 'Option D'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Question Content
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    
    # Multiple Choice Options
    option_a = models.TextField(blank=True)
    option_b = models.TextField(blank=True)
    option_c = models.TextField(blank=True)
    option_d = models.TextField(blank=True)
    
    # Answer and Difficulty (CSV format)
    answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, default='a', help_text="Correct option (a/b/c/d)")
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='moderate', help_text="Difficulty from CSV")
    tags = models.TextField(blank=True, help_text="Comma-separated tags from CSV")
    subject = models.CharField(max_length=25, choices=SUBJECT_CHOICES, default='quantitative_aptitude', help_text="Subject area")
    
    # Legacy fields for backward compatibility
    correct_answer = models.TextField(blank=True, help_text="Legacy correct answer field")
    options = models.JSONField(default=list, blank=True)  # For multiple choice options
    
    # IRT (Item Response Theory) Parameters
    difficulty = models.FloatField(default=0.0, help_text="IRT difficulty parameter (-3 to 3)")
    discrimination = models.FloatField(default=1.0, help_text="IRT discrimination parameter (>0)")
    guessing = models.FloatField(default=0.0, help_text="IRT guessing parameter (0-1)")
    
    # Learning Classification (legacy)
    skill_id = models.CharField(max_length=100, help_text="Knowledge component/skill identifier", blank=True)
    fundamental_type = models.CharField(max_length=20, choices=FUNDAMENTAL_TYPES, blank=True)
    
    # Mastery-Based Progression (updated for competitive exams)
    level = models.IntegerField(default=1, help_text="Difficulty level (1=very_easy, 2=easy, 3=moderate, 4=difficult)")
    
    # Metadata
    topic = models.CharField(max_length=200, blank=True)
    subtopic = models.CharField(max_length=200, blank=True)
    bloom_taxonomy_level = models.CharField(max_length=50, blank=True)
    estimated_time_seconds = models.IntegerField(default=60)
    
    # Statistics (updated from interactions)
    times_attempted = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Question: {self.question_text[:50]}... ({self.subject} - {self.difficulty_level})"
    
    @property
    def success_rate(self):
        return self.times_correct / self.times_attempted if self.times_attempted > 0 else 0
    
    @property
    def formatted_options(self):
        """Return formatted options for display"""
        return {
            'a': self.option_a,
            'b': self.option_b,
            'c': self.option_c,
            'd': self.option_d
        }
    
    @property
    def correct_option_text(self):
        """Get the text of the correct option"""
        options = self.formatted_options
        return options.get(self.answer, '')
    
    def get_difficulty_threshold(self):
        """Get BKT mastery threshold based on difficulty level"""
        thresholds = {
            'very_easy': 0.6,
            'easy': 0.7,
            'moderate': 0.8,
            'difficult': 0.9
        }
        return thresholds.get(self.difficulty_level, 0.8)
    
    class Meta:
        db_table = 'adaptive_questions'
        verbose_name = 'Adaptive Question'
        verbose_name_plural = 'Adaptive Questions'
        indexes = [
            models.Index(fields=['skill_id']),
            models.Index(fields=['fundamental_type']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['subject', 'level']),  # For subject-wise level filtering
            models.Index(fields=['subject', 'difficulty_level']),  # For subject-wise difficulty filtering
            models.Index(fields=['difficulty_level']),
        ]


class Interaction(models.Model):
    ASSESSMENT_MODES = [
        ('EXAM', 'Exam Mode - No AI Help'),
        ('PRACTICE', 'Practice Mode - AI Assistance Available'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Keys
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    question = models.ForeignKey(AdaptiveQuestion, on_delete=models.CASCADE, related_name='interactions')
    
    # Response Data
    is_correct = models.BooleanField()
    student_answer = models.TextField()
    response_time = models.FloatField(help_text="Response time in seconds")
    hints_used = models.IntegerField(default=0)
    confidence_level = models.IntegerField(
        choices=[(1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')],
        null=True, blank=True
    )
    
    # Session Information
    session_id = models.UUIDField(help_text="Study session identifier")
    attempt_number = models.IntegerField(default=1, help_text="Attempt number for this question")
    assessment_mode = models.CharField(max_length=10, choices=ASSESSMENT_MODES, default='EXAM', 
                                     help_text="Assessment mode: EXAM (no AI) or PRACTICE (AI help)")
    
    # Context
    previous_questions = models.JSONField(default=list, blank=True, help_text="Previous questions in session")
    device_type = models.CharField(max_length=50, blank=True)
    
    # AI Assistance Data (only for PRACTICE mode)
    hints_requested = models.JSONField(default=list, blank=True, help_text="List of hints requested")
    ai_explanation_viewed = models.BooleanField(default=False, help_text="Whether AI explanation was viewed")
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Interaction: {self.student.username} - {self.question.question_text[:30]}..."
    
    class Meta:
        db_table = 'interactions'
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        indexes = [
            models.Index(fields=['student', 'timestamp']),
            models.Index(fields=['question', 'timestamp']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_correct', 'timestamp']),
        ]
        ordering = ['-timestamp']


class ExamSession(models.Model):
    """Track complete exam sessions for post-exam analysis"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active Session'),
        ('COMPLETED', 'Completed Session'),
        ('ABANDONED', 'Abandoned Session'),
    ]
    
    ASSESSMENT_MODES = [
        ('EXAM', 'Exam Mode - No AI Help'),
        ('PRACTICE', 'Practice Mode - AI Assistance Available'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session Details
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    subject = models.CharField(max_length=25, choices=AdaptiveQuestion.SUBJECT_CHOICES)
    assessment_mode = models.CharField(max_length=10, choices=ASSESSMENT_MODES, default='EXAM')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Session Statistics
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    total_time_spent = models.FloatField(default=0.0, help_text="Total time in seconds")
    current_difficulty = models.CharField(max_length=15, 
                                        choices=AdaptiveQuestion.DIFFICULTY_CHOICES, 
                                        default='very_easy')
    
    # BKT Integration
    initial_mastery_score = models.FloatField(default=0.0)
    final_mastery_score = models.FloatField(default=0.0)
    mastery_improvement = models.FloatField(default=0.0)
    
    # AI Analysis Status
    ai_analysis_requested = models.BooleanField(default=False)
    ai_analysis_completed = models.BooleanField(default=False)
    ai_analysis_data = models.JSONField(default=dict, blank=True, 
                                      help_text="Stored AI analysis results")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Exam Session: {self.student.username} - {self.subject} ({self.status})"
    
    @property
    def accuracy_rate(self):
        """Calculate accuracy rate"""
        if self.questions_attempted == 0:
            return 0.0
        return self.questions_correct / self.questions_attempted
    
    @property
    def duration_minutes(self):
        """Get duration in minutes"""
        return self.total_time_spent / 60 if self.total_time_spent else 0
    
    def mark_completed(self):
        """Mark session as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
    
    def can_request_ai_analysis(self):
        """Check if AI analysis can be requested (only for completed exams)"""
        return self.status == 'COMPLETED' and not self.ai_analysis_completed
    
    class Meta:
        db_table = 'exam_sessions'
        verbose_name = 'Exam Session'
        verbose_name_plural = 'Exam Sessions'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['subject', 'status']),
            models.Index(fields=['assessment_mode', 'status']),
            models.Index(fields=['ai_analysis_requested', 'ai_analysis_completed']),
        ]
        ordering = ['-started_at']
