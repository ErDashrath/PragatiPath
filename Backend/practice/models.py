import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from assessment.models import AdaptiveQuestion

class SRSCard(models.Model):
    # WaniKani-style stages
    SRS_STAGES = [
        ('apprentice_1', 'Apprentice 1'),
        ('apprentice_2', 'Apprentice 2'), 
        ('apprentice_3', 'Apprentice 3'),
        ('apprentice_4', 'Apprentice 4'),
        ('guru_1', 'Guru 1'),
        ('guru_2', 'Guru 2'),
        ('master', 'Master'),
        ('enlightened', 'Enlightened'),
        ('burned', 'Burned'),
    ]
    
    # Stage intervals (in days)
    STAGE_INTERVALS = {
        'apprentice_1': 1,
        'apprentice_2': 2,
        'apprentice_3': 4,
        'apprentice_4': 8,
        'guru_1': 16,
        'guru_2': 32,
        'master': 64,
        'enlightened': 128,
        'burned': 0,  # No more reviews
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Foreign Keys
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='srs_cards')
    question = models.ForeignKey(AdaptiveQuestion, on_delete=models.CASCADE, related_name='srs_cards')
    
    # SM-2 Algorithm Parameters
    ease_factor = models.FloatField(default=2.5, help_text="SM-2 ease factor (minimum 1.3)")
    interval = models.IntegerField(default=1, help_text="Current interval in days")
    repetition = models.IntegerField(default=0, help_text="Number of successful repetitions")
    
    # SRS Stage (WaniKani style)
    stage = models.CharField(max_length=20, choices=SRS_STAGES, default='apprentice_1')
    
    # Scheduling
    due_date = models.DateTimeField(default=timezone.now, help_text="When the card is due for review")
    last_reviewed = models.DateTimeField(null=True, blank=True)
    
    # Performance Tracking
    correct_streak = models.IntegerField(default=0)
    incorrect_count = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    # Status
    is_suspended = models.BooleanField(default=False, help_text="Temporarily suspend reviews")
    is_locked = models.BooleanField(default=False, help_text="Lock until prerequisites met")
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SRS Card: {self.student.username} - {self.question.question_text[:30]}..."
    
    @property
    def is_due(self):
        """Check if the card is due for review"""
        return timezone.now() >= self.due_date and not self.is_suspended
    
    @property
    def success_rate(self):
        """Calculate success rate for this card"""
        if self.total_reviews == 0:
            return 0
        return (self.total_reviews - self.incorrect_count) / self.total_reviews
    
    def update_sm2(self, quality):
        """
        Update SM-2 parameters based on review quality
        Quality: 0-5 (0=wrong, 5=perfect)
        """
        if quality < 3:
            # Incorrect answer - reset repetition and interval
            self.repetition = 0
            self.interval = 1
            self.incorrect_count += 1
            self.correct_streak = 0
            
            # Move back in SRS stages
            if self.stage != 'apprentice_1':
                stage_list = [choice[0] for choice in self.SRS_STAGES]
                current_index = stage_list.index(self.stage)
                if current_index > 0:
                    self.stage = stage_list[max(0, current_index - 2)]
        else:
            # Correct answer
            self.repetition += 1
            self.correct_streak += 1
            
            # Update ease factor
            self.ease_factor = self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            self.ease_factor = max(1.3, self.ease_factor)  # Minimum ease factor
            
            # Update interval
            if self.repetition == 1:
                self.interval = 1
            elif self.repetition == 2:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
            
            # Advance SRS stage if conditions met
            self._advance_srs_stage()
        
        # Update due date
        self.due_date = timezone.now() + timedelta(days=self.interval)
        self.last_reviewed = timezone.now()
        self.total_reviews += 1
        
        self.save()
    
    def _advance_srs_stage(self):
        """Advance to next SRS stage based on performance"""
        stage_list = [choice[0] for choice in self.SRS_STAGES]
        current_index = stage_list.index(self.stage)
        
        # Conditions for advancing
        if self.stage.startswith('apprentice') and self.correct_streak >= 1:
            if current_index < len(stage_list) - 1:
                self.stage = stage_list[current_index + 1]
        elif self.stage.startswith('guru') and self.correct_streak >= 2:
            if current_index < len(stage_list) - 1:
                self.stage = stage_list[current_index + 1]
        elif self.stage in ['master', 'enlightened'] and self.correct_streak >= 3:
            if current_index < len(stage_list) - 1:
                self.stage = stage_list[current_index + 1]
    
    def reset_to_apprentice(self):
        """Reset card back to apprentice level"""
        self.stage = 'apprentice_1'
        self.repetition = 0
        self.interval = 1
        self.ease_factor = 2.5
        self.correct_streak = 0
        self.due_date = timezone.now()
        self.save()
    
    class Meta:
        db_table = 'srs_cards'
        verbose_name = 'SRS Card'
        verbose_name_plural = 'SRS Cards'
        unique_together = ['student', 'question']  # One card per student-question pair
        indexes = [
            models.Index(fields=['student', 'due_date']),
            models.Index(fields=['stage', 'due_date']),
            models.Index(fields=['due_date']),
        ]
        ordering = ['due_date']
