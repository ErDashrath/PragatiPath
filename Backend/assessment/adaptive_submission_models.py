#!/usr/bin/env python3
"""
Adaptive Submission Models for Detailed Analysis and Reports

This module defines comprehensive models for tracking adaptive learning submissions
with detailed analytics, foreign key relationships, and reporting capabilities.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid


class AdaptiveSubmission(models.Model):
    """
    Comprehensive adaptive learning submission model for detailed analysis
    
    This model tracks every submission with detailed context for analytics,
    performance tracking, and adaptive algorithm improvement.
    """
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign Key relationships for analysis
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='adaptive_submissions',
        help_text="Student who made this submission"
    )
    
    session = models.ForeignKey(
        'assessment.StudentSession',
        on_delete=models.CASCADE,
        related_name='adaptive_submissions',
        help_text="Learning session this submission belongs to"
    )
    
    subject = models.ForeignKey(
        'assessment.Subject',
        on_delete=models.CASCADE,
        related_name='adaptive_submissions',
        help_text="Subject/topic of the question"
    )
    
    question = models.ForeignKey(
        'assessment.AdaptiveQuestion',
        on_delete=models.CASCADE,
        related_name='adaptive_submissions',
        help_text="The question that was answered"
    )
    
    # Question context and metadata
    question_type = models.CharField(max_length=50, help_text="Type of question (multiple_choice, etc.)")
    chapter = models.CharField(max_length=100, blank=True, null=True, help_text="Chapter/topic within subject")
    subtopic = models.CharField(max_length=100, blank=True, null=True, help_text="Specific subtopic")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('moderate', 'Moderate'), 
            ('difficult', 'Difficult'),
            ('expert', 'Expert')
        ],
        help_text="Difficulty level when question was presented"
    )
    
    # Student response data
    selected_answer = models.CharField(max_length=10, help_text="Student's selected answer")
    correct_answer = models.CharField(max_length=10, help_text="Correct answer for the question")
    is_correct = models.BooleanField(help_text="Whether the student answered correctly")
    
    # Timing and engagement metrics
    time_spent_seconds = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Time spent on this question in seconds"
    )
    question_number_in_session = models.PositiveIntegerField(help_text="Question order in session")
    
    # Adaptive algorithm state (before submission)
    bkt_mastery_before = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5,
        help_text="BKT mastery level before this submission"
    )
    dkt_prediction_before = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5,
        help_text="DKT prediction before this submission"
    )
    
    # Adaptive algorithm state (after submission)
    bkt_mastery_after = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5,
        help_text="BKT mastery level after this submission"
    )
    dkt_prediction_after = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.5,
        help_text="DKT prediction after this submission"
    )
    
    # Knowledge tracing parameters
    skill_id = models.CharField(max_length=100, help_text="Skill ID for knowledge tracing")
    bkt_params = models.JSONField(
        default=dict,
        help_text="BKT parameters (P_L, P_T, P_G, P_S) at time of submission"
    )
    dkt_hidden_state = models.JSONField(
        default=dict,
        help_text="DKT hidden state vector at time of submission"
    )
    
    # Adaptation decisions
    next_difficulty_recommended = models.CharField(
        max_length=20,
        choices=[
            ('easier', 'Easier'),
            ('same', 'Same'),
            ('harder', 'Harder')
        ],
        default='same',
        help_text="Recommended difficulty change after this submission"
    )
    adaptation_reason = models.TextField(
        blank=True,
        help_text="Explanation for why adaptation was chosen"
    )
    
    # Performance context
    session_accuracy_before = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
        help_text="Session accuracy before this submission"
    )
    session_accuracy_after = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
        help_text="Session accuracy after this submission"
    )
    
    # Metadata and additional context
    submission_source = models.CharField(
        max_length=50,
        choices=[
            ('frontend_api', 'Frontend API'),
            ('mobile_app', 'Mobile App'),
            ('web_interface', 'Web Interface'),
            ('api_test', 'API Test'),
            ('system_test', 'System Test')
        ],
        default='frontend_api',
        help_text="Source/origin of this submission"
    )
    
    interaction_data = models.JSONField(
        default=dict,
        help_text="Additional interaction data and context"
    )
    
    # Analytics flags
    is_first_attempt = models.BooleanField(
        default=True,
        help_text="Whether this is the first attempt at this question type"
    )
    is_mastery_achieved = models.BooleanField(
        default=False,
        help_text="Whether mastery was achieved after this submission"
    )
    contributed_to_mastery = models.BooleanField(
        default=False,
        help_text="Whether this submission contributed to mastery improvement"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'created_at']),
            models.Index(fields=['subject', 'chapter']),
            models.Index(fields=['difficulty_level', 'is_correct']),
            models.Index(fields=['session', 'question_number_in_session']),
            models.Index(fields=['skill_id', 'created_at']),
        ]
    
    def __str__(self):
        return (f"Submission by {self.student.username} - "
                f"{self.subject.name} - Q{self.question_number_in_session} - "
                f"{'✓' if self.is_correct else '✗'}")
    
    @property
    def mastery_improvement(self):
        """Calculate mastery improvement from this submission"""
        return self.bkt_mastery_after - self.bkt_mastery_before
    
    @property
    def dkt_improvement(self):
        """Calculate DKT prediction improvement from this submission"""
        return self.dkt_prediction_after - self.dkt_prediction_before
    
    @property
    def time_efficiency_score(self):
        """Calculate efficiency based on time spent and correctness"""
        if self.is_correct:
            # Less time for correct answers is better (up to a reasonable minimum)
            optimal_time = 30.0  # 30 seconds optimal
            if self.time_spent_seconds <= optimal_time:
                return 1.0
            else:
                return max(0.1, optimal_time / self.time_spent_seconds)
        else:
            # More time on incorrect answers might indicate effort
            return min(1.0, self.time_spent_seconds / 60.0)  # Up to 1 minute
    
    def get_performance_context(self):
        """Get performance context for analytics"""
        return {
            'mastery_before': self.bkt_mastery_before,
            'mastery_after': self.bkt_mastery_after,
            'mastery_change': self.mastery_improvement,
            'dkt_before': self.dkt_prediction_before,
            'dkt_after': self.dkt_prediction_after,
            'dkt_change': self.dkt_improvement,
            'time_efficiency': self.time_efficiency_score,
            'session_progress': {
                'question_number': self.question_number_in_session,
                'accuracy_before': self.session_accuracy_before,
                'accuracy_after': self.session_accuracy_after
            }
        }


class AdaptiveSubmissionAnalytics(models.Model):
    """
    Aggregated analytics for adaptive submissions
    
    This model stores pre-computed analytics for faster reporting
    and dashboard generation.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Analytics scope
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey('assessment.Subject', on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey('assessment.StudentSession', on_delete=models.CASCADE, null=True, blank=True)
    
    analytics_type = models.CharField(
        max_length=50,
        choices=[
            ('student_subject', 'Student-Subject Analytics'),
            ('session_summary', 'Session Summary'),
            ('subject_performance', 'Subject Performance'),
            ('skill_mastery', 'Skill Mastery Analytics'),
            ('difficulty_progression', 'Difficulty Progression')
        ]
    )
    
    # Time period for analytics
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Computed metrics
    total_submissions = models.PositiveIntegerField(default=0)
    correct_submissions = models.PositiveIntegerField(default=0)
    accuracy_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    average_time_per_question = models.FloatField(default=0.0)
    mastery_improvement_rate = models.FloatField(default=0.0)
    
    # Difficulty distribution
    easy_questions_attempted = models.PositiveIntegerField(default=0)
    moderate_questions_attempted = models.PositiveIntegerField(default=0)
    difficult_questions_attempted = models.PositiveIntegerField(default=0)
    
    # Learning trajectory
    starting_mastery = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    ending_mastery = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    mastery_growth = models.FloatField()
    
    # Detailed analytics data
    analytics_data = models.JSONField(
        default=dict,
        help_text="Detailed analytics data and metrics"
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [
            ['student', 'subject', 'analytics_type', 'period_start']
        ]
    
    def __str__(self):
        scope = []
        if self.student:
            scope.append(f"Student: {self.student.username}")
        if self.subject:
            scope.append(f"Subject: {self.subject.name}")
        if self.session:
            scope.append(f"Session: {self.session.id}")
        
        return f"{self.analytics_type} - {' | '.join(scope)}"


# Analytics helper functions
class AdaptiveSubmissionAnalyzer:
    """
    Helper class for analyzing adaptive submissions
    """
    
    @staticmethod
    def analyze_student_performance(student, subject=None, days=30):
        """Analyze student performance over a time period"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        submissions = AdaptiveSubmission.objects.filter(
            student=student,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        if subject:
            submissions = submissions.filter(subject=subject)
        
        if not submissions.exists():
            return None
        
        # Calculate metrics
        total_submissions = submissions.count()
        correct_submissions = submissions.filter(is_correct=True).count()
        accuracy = correct_submissions / total_submissions if total_submissions > 0 else 0
        
        # Mastery progression
        first_submission = submissions.order_by('created_at').first()
        last_submission = submissions.order_by('created_at').last()
        
        mastery_growth = (last_submission.bkt_mastery_after - 
                         first_submission.bkt_mastery_before)
        
        # Time analysis
        avg_time = submissions.aggregate(
            avg_time=models.Avg('time_spent_seconds')
        )['avg_time'] or 0
        
        # Difficulty progression
        difficulty_counts = submissions.values('difficulty_level').annotate(
            count=models.Count('id')
        )
        
        return {
            'total_submissions': total_submissions,
            'accuracy': accuracy,
            'mastery_growth': mastery_growth,
            'average_time_per_question': avg_time,
            'difficulty_distribution': list(difficulty_counts),
            'starting_mastery': first_submission.bkt_mastery_before,
            'ending_mastery': last_submission.bkt_mastery_after,
            'period_days': days
        }
    
    @staticmethod
    def generate_learning_insights(student, subject=None):
        """Generate learning insights and recommendations"""
        analysis = AdaptiveSubmissionAnalyzer.analyze_student_performance(
            student, subject, days=7
        )
        
        if not analysis:
            return {'insights': [], 'recommendations': []}
        
        insights = []
        recommendations = []
        
        # Accuracy insights
        if analysis['accuracy'] >= 0.8:
            insights.append("🎉 Excellent accuracy! You're mastering this topic.")
            recommendations.append("Ready for more challenging questions.")
        elif analysis['accuracy'] >= 0.6:
            insights.append("📈 Good progress! Keep practicing.")
            recommendations.append("Continue with current difficulty level.")
        else:
            insights.append("💪 Building foundations. Stay focused!")
            recommendations.append("Try easier questions to build confidence.")
        
        # Mastery growth insights
        if analysis['mastery_growth'] > 0.2:
            insights.append("🚀 Rapid learning! Your mastery is growing fast.")
        elif analysis['mastery_growth'] > 0.1:
            insights.append("📊 Steady improvement in your understanding.")
        else:
            insights.append("🎯 Focus on understanding concepts better.")
            recommendations.append("Review explanations and try practice problems.")
        
        # Time efficiency insights
        avg_time = analysis['average_time_per_question']
        if avg_time < 20:
            insights.append("⚡ Very quick responses! Make sure you're reading carefully.")
            recommendations.append("Take a bit more time to ensure accuracy.")
        elif avg_time > 120:
            insights.append("🤔 Taking time to think through problems - that's good!")
            recommendations.append("Try to balance thoroughness with efficiency.")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'analysis_summary': analysis
        }