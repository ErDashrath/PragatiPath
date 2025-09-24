import uuid
from django.db import models
from django.contrib.auth.models import User

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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Question Content
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    correct_answer = models.TextField()
    options = models.JSONField(default=list, blank=True)  # For multiple choice options
    
    # IRT (Item Response Theory) Parameters
    difficulty = models.FloatField(default=0.0, help_text="IRT difficulty parameter (-3 to 3)")
    discrimination = models.FloatField(default=1.0, help_text="IRT discrimination parameter (>0)")
    guessing = models.FloatField(default=0.0, help_text="IRT guessing parameter (0-1)")
    
    # Learning Classification
    skill_id = models.CharField(max_length=100, help_text="Knowledge component/skill identifier")
    fundamental_type = models.CharField(max_length=20, choices=FUNDAMENTAL_TYPES)
    
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
        return f"Question: {self.question_text[:50]}..."
    
    @property
    def success_rate(self):
        return self.times_correct / self.times_attempted if self.times_attempted > 0 else 0
    
    class Meta:
        db_table = 'adaptive_questions'
        verbose_name = 'Adaptive Question'
        verbose_name_plural = 'Adaptive Questions'
        indexes = [
            models.Index(fields=['skill_id']),
            models.Index(fields=['fundamental_type']),
            models.Index(fields=['difficulty']),
        ]


class Interaction(models.Model):
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
    
    # Context
    previous_questions = models.JSONField(default=list, blank=True, help_text="Previous questions in session")
    device_type = models.CharField(max_length=50, blank=True)
    
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
