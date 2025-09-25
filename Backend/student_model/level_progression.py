"""
Mastery-Based Level Progression System

Manages student progression through skill levels based on:
- BKT mastery probability (>= threshold)
- Consecutive correct answers (>= required count)
- Level unlocking and locking logic
"""

import logging
from typing import Dict, List, Tuple, Optional
from django.utils import timezone
from core.models import StudentProfile

logger = logging.getLogger(__name__)

class LevelProgressionService:
    """Manages mastery-based level progression for students"""
    
    def __init__(self):
        self.default_mastery_threshold = 0.8
        self.required_consecutive_correct = 3
        self.max_level = 10  # Maximum level per skill
    
    def initialize_student_levels(self, student_profile: StudentProfile, skill_id: str) -> None:
        """Initialize level progression data for a new skill"""
        if not student_profile.current_level:
            student_profile.current_level = {}
        if not student_profile.consecutive_correct_count:
            student_profile.consecutive_correct_count = {}
        if not student_profile.level_lock_status:
            student_profile.level_lock_status = {}
        
        # Initialize skill if not exists
        if skill_id not in student_profile.current_level:
            student_profile.current_level[skill_id] = 0  # Start at level 0
            student_profile.level_lock_status[skill_id] = [0]  # Level 0 is always unlocked
            
        # Initialize consecutive count for current level
        current_level = student_profile.current_level[skill_id]
        level_key = f"{skill_id}_level_{current_level}"
        if level_key not in student_profile.consecutive_correct_count:
            student_profile.consecutive_correct_count[level_key] = 0
            
        student_profile.save()
        logger.info(f"Initialized levels for {skill_id}: level={current_level}")
    
    def update_progression(self, student_profile: StudentProfile, skill_id: str, 
                          is_correct: bool, bkt_mastery: float) -> Dict:
        """
        Update level progression based on answer correctness and BKT mastery
        
        Returns:
            Dict with progression info: {
                'level_changed': bool,
                'new_level': int,
                'mastery_achieved': bool,
                'consecutive_count': int,
                'next_level_unlocked': bool,
                'congratulations_message': str
            }
        """
        self.initialize_student_levels(student_profile, skill_id)
        
        current_level = student_profile.current_level[skill_id]
        level_key = f"{skill_id}_level_{current_level}"
        mastery_threshold = student_profile.mastery_threshold or self.default_mastery_threshold
        
        progression_info = {
            'level_changed': False,
            'new_level': current_level,
            'mastery_achieved': False,
            'consecutive_count': 0,
            'next_level_unlocked': False,
            'congratulations_message': ''
        }
        
        if is_correct:
            # Increment consecutive correct count
            student_profile.consecutive_correct_count[level_key] += 1
            consecutive_count = student_profile.consecutive_correct_count[level_key]
            
            # Check for level mastery
            mastery_achieved = (
                bkt_mastery >= mastery_threshold and 
                consecutive_count >= self.required_consecutive_correct
            )
            
            progression_info.update({
                'consecutive_count': consecutive_count,
                'mastery_achieved': mastery_achieved
            })
            
            if mastery_achieved and current_level < self.max_level:
                # Level up!
                new_level = current_level + 1
                student_profile.current_level[skill_id] = new_level
                
                # Unlock new level
                if new_level not in student_profile.level_lock_status[skill_id]:
                    student_profile.level_lock_status[skill_id].append(new_level)
                
                # Reset consecutive count for new level
                new_level_key = f"{skill_id}_level_{new_level}"
                student_profile.consecutive_correct_count[new_level_key] = 0
                
                progression_info.update({
                    'level_changed': True,
                    'new_level': new_level,
                    'next_level_unlocked': True,
                    'congratulations_message': f"🎉 Congratulations! You've mastered {skill_id} Level {current_level} and unlocked Level {new_level}!"
                })
                
                logger.info(f"Level progression: {skill_id} {current_level} → {new_level} (mastery: {bkt_mastery:.3f})")
            
            elif consecutive_count >= self.required_consecutive_correct:
                progression_info['congratulations_message'] = f"Great streak! {consecutive_count} correct in a row for {skill_id}!"
                
        else:
            # Incorrect answer - reset consecutive count but stay at current level
            student_profile.consecutive_correct_count[level_key] = 0
            progression_info['consecutive_count'] = 0
            logger.info(f"Reset consecutive count for {skill_id} level {current_level}")
        
        student_profile.save()
        return progression_info
    
    def get_student_current_level(self, student_profile: StudentProfile, skill_id: str) -> int:
        """Get student's current level for a skill"""
        self.initialize_student_levels(student_profile, skill_id)
        return student_profile.current_level.get(skill_id, 0)
    
    def get_unlocked_levels(self, student_profile: StudentProfile, skill_id: str) -> List[int]:
        """Get list of unlocked levels for a skill"""
        self.initialize_student_levels(student_profile, skill_id)
        return student_profile.level_lock_status.get(skill_id, [0])
    
    def is_level_unlocked(self, student_profile: StudentProfile, skill_id: str, level: int) -> bool:
        """Check if a specific level is unlocked for the student"""
        unlocked_levels = self.get_unlocked_levels(student_profile, skill_id)
        return level in unlocked_levels
    
    def get_progression_status(self, student_profile: StudentProfile, skill_id: str) -> Dict:
        """Get comprehensive progression status for a skill"""
        self.initialize_student_levels(student_profile, skill_id)
        
        current_level = student_profile.current_level.get(skill_id, 0)
        unlocked_levels = student_profile.level_lock_status.get(skill_id, [0])
        level_key = f"{skill_id}_level_{current_level}"
        consecutive_count = student_profile.consecutive_correct_count.get(level_key, 0)
        
        # Get BKT mastery for the skill
        bkt_mastery = 0.5
        if student_profile.bkt_parameters and skill_id in student_profile.bkt_parameters:
            bkt_mastery = student_profile.bkt_parameters[skill_id].get('P_L', 0.5)
        
        mastery_threshold = student_profile.mastery_threshold or self.default_mastery_threshold
        
        return {
            'skill_id': skill_id,
            'current_level': current_level,
            'unlocked_levels': sorted(unlocked_levels),
            'consecutive_correct_count': consecutive_count,
            'required_consecutive': self.required_consecutive_correct,
            'bkt_mastery': bkt_mastery,
            'mastery_threshold': mastery_threshold,
            'mastery_achieved': bkt_mastery >= mastery_threshold and consecutive_count >= self.required_consecutive_correct,
            'progress_to_next_level': {
                'mastery_progress': min(100, int(bkt_mastery / mastery_threshold * 100)),
                'consecutive_progress': min(100, int(consecutive_count / self.required_consecutive_correct * 100))
            }
        }
    
    def get_available_question_levels(self, student_profile: StudentProfile, skill_id: str) -> List[int]:
        """Get levels from which questions can be served to the student"""
        current_level = self.get_student_current_level(student_profile, skill_id)
        unlocked_levels = self.get_unlocked_levels(student_profile, skill_id)
        
        # Student can attempt questions from current level or any previously unlocked level
        available_levels = [level for level in unlocked_levels if level <= current_level]
        
        # Always include current level even if not fully mastered
        if current_level not in available_levels:
            available_levels.append(current_level)
            
        return sorted(available_levels)