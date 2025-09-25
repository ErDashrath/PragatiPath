from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class BKTSkillState(models.Model):
    """
    Model to store Bayesian Knowledge Tracing parameters for each student-skill combination
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bkt_skill_states')
    skill_id = models.CharField(max_length=100, help_text="Unique identifier for the skill")
    
    # BKT Parameters
    P_L0 = models.FloatField(default=0.1, help_text="Initial probability of knowing the skill")
    P_T = models.FloatField(default=0.3, help_text="Learning (transition) rate")
    P_G = models.FloatField(default=0.2, help_text="Guess rate")
    P_S = models.FloatField(default=0.1, help_text="Slip rate")
    P_L = models.FloatField(default=0.1, help_text="Current probability of knowing the skill")
    
    # Metadata
    interactions_count = models.IntegerField(default=0, help_text="Number of interactions with this skill")
    last_interaction = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_model_bkt_skill_state'
        unique_together = ['user', 'skill_id']
        verbose_name = 'BKT Skill State'
        verbose_name_plural = 'BKT Skill States'
        
    def __str__(self):
        return f"{self.user.username} - {self.skill_id} (P_L: {self.P_L:.3f})"
    
    @property 
    def is_mastered(self, threshold=0.95):
        """Check if skill is mastered based on threshold"""
        return self.P_L >= threshold
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'skill_id': self.skill_id,
            'P_L0': self.P_L0,
            'P_T': self.P_T,
            'P_G': self.P_G,
            'P_S': self.P_S,
            'P_L': self.P_L,
            'interactions_count': self.interactions_count,
            'is_mastered': self.is_mastered(),
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'updated_at': self.updated_at.isoformat()
        }


class StudentKnowledgeState(models.Model):
    """
    Model to store overall knowledge state and learning analytics for students
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='knowledge_state')
    
    # Overall Statistics
    total_skills_tracked = models.IntegerField(default=0)
    mastered_skills_count = models.IntegerField(default=0)
    average_mastery = models.FloatField(default=0.0)
    
    # Learning Analytics
    total_interactions = models.IntegerField(default=0)
    correct_interactions = models.IntegerField(default=0)
    learning_velocity = models.FloatField(default=0.0, help_text="Rate of skill acquisition")
    
    # DKT Integration
    dkt_hidden_state = models.JSONField(default=list, blank=True, help_text="DKT LSTM hidden state")
    dkt_skill_predictions = models.JSONField(default=list, blank=True, help_text="DKT skill predictions")
    dkt_last_updated = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_model_knowledge_state'
        verbose_name = 'Student Knowledge State'
        verbose_name_plural = 'Student Knowledge States'
        
    def __str__(self):
        return f"{self.user.username} - Knowledge State ({self.mastered_skills_count}/{self.total_skills_tracked} mastered)"
    
    def update_statistics(self):
        """Update overall statistics based on BKT skill states"""
        bkt_states = self.user.bkt_skill_states.all()
        
        self.total_skills_tracked = bkt_states.count()
        self.mastered_skills_count = bkt_states.filter(P_L__gte=0.95).count()
        
        if self.total_skills_tracked > 0:
            self.average_mastery = bkt_states.aggregate(
                avg_mastery=models.Avg('P_L')
            )['avg_mastery'] or 0.0
        
        self.save()
    
    def get_weak_skills(self, threshold=0.6):
        """Get skills that need more practice"""
        return self.user.bkt_skill_states.filter(P_L__lt=threshold)
    
    def get_mastered_skills(self, threshold=0.95):
        """Get mastered skills"""
        return self.user.bkt_skill_states.filter(P_L__gte=threshold)


class InteractionHistory(models.Model):
    """
    Model to store interaction history for analytics and research
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interaction_history')
    skill_id = models.CharField(max_length=100)
    
    # Interaction Details
    is_correct = models.BooleanField()
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    question_id = models.CharField(max_length=100, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # BKT State Before/After
    bkt_before = models.JSONField(default=dict, help_text="BKT parameters before interaction")
    bkt_after = models.JSONField(default=dict, help_text="BKT parameters after interaction")
    
    # Additional Context
    interaction_context = models.JSONField(default=dict, help_text="Additional interaction metadata")
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_model_interaction_history'
        verbose_name = 'Interaction History'
        verbose_name_plural = 'Interaction Histories'
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.skill_id} ({'✓' if self.is_correct else '✗'}) - {self.timestamp}"
