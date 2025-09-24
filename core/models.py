import uuid
from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # BKT Parameters - JSON field storing skill-wise BKT parameters
    # Format: {"skill_id": {"P_L0": 0.1, "P_T": 0.3, "P_G": 0.2, "P_S": 0.1, "P_L": 0.4}}
    bkt_parameters = models.JSONField(default=dict, blank=True)
    
    # DKT Hidden State - Neural network hidden state vector
    # Format: [0.1, 0.2, 0.3, ...] (vector of floats)
    dkt_hidden_state = models.JSONField(default=list, blank=True)
    
    # Fundamentals - Core learning ability scores
    # Format: {"listening": 0.8, "grasping": 0.7, "retention": 0.9, "application": 0.6}
    fundamentals = models.JSONField(default=dict, blank=True)
    
    # Interaction History - Raw interaction data for analysis
    # Format: [{"question_id": "123", "timestamp": "...", "correct": true, "time": 15.2}, ...]
    interaction_history = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"StudentProfile: {self.user.username}"
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
