"""
Bayesian Knowledge Tracing (BKT) Algorithm Implementation

BKT is a user modeling approach in intelligent tutoring systems that models
learner knowledge as a set of binary variables (known/unknown) for skills.

Parameters:
- P(L0): Initial probability that the skill is learned
- P(T): Probability that the skill transitions from unknown to known (learning rate)
- P(G): Probability of getting the answer right despite not knowing the skill (guess rate)  
- P(S): Probability of getting the answer wrong despite knowing the skill (slip rate)
"""

import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from django.contrib.auth.models import User
from core.models import StudentProfile


@dataclass
class BKTParameters:
    """BKT parameters for a specific skill"""
    P_L0: float  # Initial probability of knowing the skill
    P_T: float   # Learning (transition) rate
    P_G: float   # Guess rate
    P_S: float   # Slip rate
    P_L: float   # Current probability of knowing the skill
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'P_L0': self.P_L0,
            'P_T': self.P_T,
            'P_G': self.P_G,
            'P_S': self.P_S,
            'P_L': self.P_L
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'BKTParameters':
        return cls(
            P_L0=data['P_L0'],
            P_T=data['P_T'],
            P_G=data['P_G'],
            P_S=data['P_S'],
            P_L=data['P_L']
        )


def initialize_bkt_skill(
    skill_id: str,
    P_L0: float = 0.1,
    P_T: float = 0.3,
    P_G: float = 0.2,
    P_S: float = 0.1
) -> BKTParameters:
    """
    Initialize BKT parameters for a new skill
    
    Args:
        skill_id: Unique identifier for the skill
        P_L0: Initial probability of knowing the skill (default 0.1)
        P_T: Learning rate (default 0.3)
        P_G: Guess rate (default 0.2) 
        P_S: Slip rate (default 0.1)
    
    Returns:
        BKTParameters object with initialized values
    """
    return BKTParameters(
        P_L0=P_L0,
        P_T=P_T,
        P_G=P_G,
        P_S=P_S,
        P_L=P_L0  # Initially, P(L) = P(L0)
    )


def update_bkt(bkt_params: BKTParameters, is_correct: bool) -> BKTParameters:
    """
    Update BKT parameters based on student response using Bayesian inference
    
    The BKT update equations:
    1. P(L_t+1 | evidence) = P(L_t+1 | Obs_t, L_t) * P(L_t | evidence) + 
                              P(L_t+1 | Obs_t, ¬L_t) * P(¬L_t | evidence)
    2. P(L_t | evidence) updated using Bayes' rule based on correctness
    
    Args:
        bkt_params: Current BKT parameters
        is_correct: Whether the student answered correctly
        
    Returns:
        Updated BKTParameters
    """
    P_L = bkt_params.P_L
    P_T = bkt_params.P_T
    P_G = bkt_params.P_G  
    P_S = bkt_params.P_S
    
    # Step 1: Update P(L) based on the observation using Bayes' rule
    if is_correct:
        # P(correct | L) = 1 - P_S
        # P(correct | ¬L) = P_G
        P_correct_given_L = 1 - P_S
        P_correct_given_not_L = P_G
        
        # Bayes' rule: P(L | correct) = P(correct | L) * P(L) / P(correct)
        P_correct = P_correct_given_L * P_L + P_correct_given_not_L * (1 - P_L)
        P_L_given_evidence = (P_correct_given_L * P_L) / P_correct if P_correct > 0 else P_L
    else:
        # P(incorrect | L) = P_S
        # P(incorrect | ¬L) = 1 - P_G
        P_incorrect_given_L = P_S
        P_incorrect_given_not_L = 1 - P_G
        
        # Bayes' rule: P(L | incorrect) = P(incorrect | L) * P(L) / P(incorrect)
        P_incorrect = P_incorrect_given_L * P_L + P_incorrect_given_not_L * (1 - P_L)
        P_L_given_evidence = (P_incorrect_given_L * P_L) / P_incorrect if P_incorrect > 0 else P_L
    
    # Step 2: Apply learning (transition) - P(L_t+1)
    # P(L_t+1) = P(L_t+1 | L_t) * P(L_t) + P(L_t+1 | ¬L_t) * P(¬L_t)
    # P(L_t+1 | L_t) = 1 (if you know it, you still know it)
    # P(L_t+1 | ¬L_t) = P_T (learning probability)
    P_L_new = P_L_given_evidence + P_T * (1 - P_L_given_evidence)
    
    # Ensure probability bounds
    P_L_new = max(0.0, min(1.0, P_L_new))
    
    return BKTParameters(
        P_L0=bkt_params.P_L0,  # Keep original initial probability
        P_T=P_T,
        P_G=P_G,
        P_S=P_S,
        P_L=P_L_new
    )


def calculate_mastery_probability(bkt_params: BKTParameters) -> float:
    """
    Calculate the probability that a student has mastered a skill
    
    Args:
        bkt_params: Current BKT parameters
        
    Returns:
        Probability of mastery (P_L)
    """
    return bkt_params.P_L


def is_skill_mastered(bkt_params: BKTParameters, threshold: float = 0.95) -> bool:
    """
    Check if a skill is considered mastered based on threshold
    
    Args:
        bkt_params: Current BKT parameters
        threshold: Mastery threshold (default 0.95)
        
    Returns:
        True if skill is mastered, False otherwise
    """
    return bkt_params.P_L >= threshold


class BKTService:
    """
    Service class for managing BKT operations with database integration
    """
    
    @staticmethod
    def get_or_create_student_profile(user: User) -> StudentProfile:
        """Get or create StudentProfile for a user"""
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'bkt_parameters': {},
                'dkt_hidden_state': [],
                'fundamentals': {
                    'listening': 0.5,
                    'grasping': 0.5,
                    'retention': 0.5,
                    'application': 0.5
                },
                'interaction_history': []
            }
        )
        return profile
    
    @staticmethod
    def get_skill_bkt_params(user: User, skill_id: str) -> BKTParameters:
        """
        Get BKT parameters for a specific skill, initializing if necessary
        
        Args:
            user: Django User object
            skill_id: Skill identifier
            
        Returns:
            BKTParameters object
        """
        profile = BKTService.get_or_create_student_profile(user)
        
        if skill_id not in profile.bkt_parameters:
            # Initialize new skill with default parameters
            bkt_params = initialize_bkt_skill(skill_id)
            profile.bkt_parameters[skill_id] = bkt_params.to_dict()
            profile.save()
            return bkt_params
        
        return BKTParameters.from_dict(profile.bkt_parameters[skill_id])
    
    @staticmethod
    def update_skill_bkt_with_progression(
        user: User, 
        skill_id: str, 
        is_correct: bool,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[BKTParameters, Dict[str, Any]]:
        """
        Update BKT parameters for a skill with level progression logic
        
        Args:
            user: Django User object
            skill_id: Skill identifier
            is_correct: Whether the student answered correctly
            interaction_data: Additional interaction data for history
            
        Returns:
            Tuple of (Updated BKTParameters, Level Progression Info)
        """
        from student_model.level_progression import LevelProgressionService
        
        profile = BKTService.get_or_create_student_profile(user)
        
        # Get current BKT parameters
        current_params = BKTService.get_skill_bkt_params(user, skill_id)
        
        # Update BKT parameters
        updated_params = update_bkt(current_params, is_correct)
        
        # Save to database
        profile.bkt_parameters[skill_id] = updated_params.to_dict()
        
        # Update interaction history
        if interaction_data:
            interaction_entry = {
                'timestamp': interaction_data.get('timestamp'),
                'skill_id': skill_id,
                'is_correct': is_correct,
                'P_L_before': current_params.P_L,
                'P_L_after': updated_params.P_L,
                **interaction_data
            }
            profile.interaction_history.append(interaction_entry)
        
        # Update level progression
        progression_service = LevelProgressionService()
        progression_info = progression_service.update_progression(
            profile, skill_id, is_correct, updated_params.P_L
        )
        
        profile.save()
        
        return updated_params, progression_info
    
    @staticmethod
    def update_skill_bkt(
        user: User, 
        skill_id: str, 
        is_correct: bool,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> BKTParameters:
        """
        Update BKT parameters for a skill based on student interaction
        
        Args:
            user: Django User object
            skill_id: Skill identifier
            is_correct: Whether the student answered correctly
            interaction_data: Additional interaction data for history
            
        Returns:
            Updated BKTParameters
        """
        profile = BKTService.get_or_create_student_profile(user)
        
        # Get current BKT parameters
        current_params = BKTService.get_skill_bkt_params(user, skill_id)
        
        # Update BKT parameters
        updated_params = update_bkt(current_params, is_correct)
        
        # Save to database
        profile.bkt_parameters[skill_id] = updated_params.to_dict()
        
        # Add to interaction history
        if interaction_data:
            interaction_record = {
                'skill_id': skill_id,
                'is_correct': is_correct,
                'timestamp': interaction_data.get('timestamp'),
                'P_L_before': current_params.P_L,
                'P_L_after': updated_params.P_L,
                **interaction_data
            }
            profile.interaction_history.append(interaction_record)
            
            # Keep only last 1000 interactions to prevent unbounded growth
            if len(profile.interaction_history) > 1000:
                profile.interaction_history = profile.interaction_history[-1000:]
        
        profile.save()
        return updated_params
    
    @staticmethod
    def get_all_skill_states(user: User) -> Dict[str, BKTParameters]:
        """
        Get BKT parameters for all skills for a user
        
        Args:
            user: Django User object
            
        Returns:
            Dictionary mapping skill_id to BKTParameters
        """
        profile = BKTService.get_or_create_student_profile(user)
        
        skill_states = {}
        for skill_id, params_dict in profile.bkt_parameters.items():
            skill_states[skill_id] = BKTParameters.from_dict(params_dict)
            
        return skill_states
    
    @staticmethod
    def get_mastered_skills(user: User, threshold: float = 0.95) -> Dict[str, float]:
        """
        Get all mastered skills for a user
        
        Args:
            user: Django User object
            threshold: Mastery threshold
            
        Returns:
            Dictionary of mastered skills and their mastery probabilities
        """
        skill_states = BKTService.get_all_skill_states(user)
        mastered_skills = {}
        
        for skill_id, params in skill_states.items():
            if is_skill_mastered(params, threshold):
                mastered_skills[skill_id] = params.P_L
                
        return mastered_skills
    
    @staticmethod
    def reset_skill(user: User, skill_id: str) -> BKTParameters:
        """
        Reset a skill's BKT parameters to initial state
        
        Args:
            user: Django User object
            skill_id: Skill identifier
            
        Returns:
            Reset BKTParameters
        """
        profile = BKTService.get_or_create_student_profile(user)
        
        # Get current parameters to preserve P_T, P_G, P_S values
        current_params = BKTService.get_skill_bkt_params(user, skill_id)
        
        # Reset to initial state
        reset_params = BKTParameters(
            P_L0=current_params.P_L0,
            P_T=current_params.P_T,
            P_G=current_params.P_G,
            P_S=current_params.P_S,
            P_L=current_params.P_L0  # Reset P_L to initial value
        )
        
        profile.bkt_parameters[skill_id] = reset_params.to_dict()
        profile.save()
        
        return reset_params