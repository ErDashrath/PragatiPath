"""
Item Response Theory (IRT) Question Selection Engine

This module implements IRT-based adaptive question selection for the assessment system.
It integrates with existing BKT algorithms and Django models to provide optimal
question difficulty matching to student ability levels.
"""

import math
import random
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

import logging
logger = logging.getLogger(__name__)


class IRTEngine:
    """
    Item Response Theory Engine for adaptive question selection
    
    This engine implements the 1-Parameter Logistic (1PL) IRT model with
    integration to BKT algorithms and existing Django models.
    """
    
    def __init__(self, 
                 exposure_window_hours: int = 24,
                 min_theta: float = -3.0, 
                 max_theta: float = 3.0,
                 theta_adjustment: float = 0.5):
        """
        Initialize IRT Engine with parameters
        
        Args:
            exposure_window_hours: Hours to avoid re-showing same questions
            min_theta: Minimum theta (ability) value
            max_theta: Maximum theta (ability) value  
            theta_adjustment: Basic theta adjustment per correct/incorrect answer
        """
        self.exposure_window_hours = exposure_window_hours
        self.min_theta = min_theta
        self.max_theta = max_theta
        self.theta_adjustment = theta_adjustment
    
    def select_question_for_theta(self, 
                                  item_bank: List[Any], 
                                  theta: float,
                                  skill_id: Optional[str] = None,
                                  exclude_recent: bool = True,
                                  student_id: Optional[str] = None) -> Optional[Any]:
        """
        Select optimal question based on student's theta (ability level)
        
        Uses IRT principle: optimal question difficulty should match student ability
        
        Args:
            item_bank: List of AdaptiveQuestion objects
            theta: Student's current ability estimate (-3 to +3 scale)
            skill_id: Filter questions by specific skill (optional)
            exclude_recent: Whether to exclude recently seen questions
            student_id: Student ID for exposure tracking
            
        Returns:
            AdaptiveQuestion object or None if no suitable question found
        """
        try:
            # Filter questions by skill if specified
            available_questions = item_bank
            if skill_id:
                available_questions = [q for q in item_bank 
                                     if hasattr(q, 'skill_id') and q.skill_id == skill_id]
            
            # Exclude recently seen questions if requested
            if exclude_recent and student_id:
                available_questions = self._filter_recent_questions(
                    available_questions, student_id
                )
            
            if not available_questions:
                logger.warning(f"No available questions for theta={theta}, skill_id={skill_id}")
                return None
            
            # Find question with difficulty closest to student's theta
            best_question = None
            min_distance = float('inf')
            
            for question in available_questions:
                # Use question difficulty as IRT 'b' parameter
                question_difficulty = getattr(question, 'difficulty', 0.0)
                
                # Calculate distance between student ability and question difficulty
                distance = abs(theta - question_difficulty)
                
                # Add small random factor to avoid always selecting same question
                # when multiple questions have similar difficulty
                random_factor = random.uniform(-0.1, 0.1)
                adjusted_distance = distance + random_factor
                
                if adjusted_distance < min_distance:
                    min_distance = adjusted_distance
                    best_question = question
            
            if best_question:
                logger.info(f"Selected question ID={getattr(best_question, 'id', 'unknown')} "
                           f"with difficulty={getattr(best_question, 'difficulty', 0.0)} "
                           f"for student theta={theta}")
            
            return best_question
            
        except Exception as e:
            logger.error(f"Error in select_question_for_theta: {e}")
            return None
    
    def update_theta_simple(self, 
                           current_theta: float, 
                           is_correct: bool,
                           question_difficulty: Optional[float] = None) -> float:
        """
        Simple theta update based on response correctness
        
        This is a basic implementation. More sophisticated methods would use
        Maximum Likelihood Estimation (MLE) or Expected A Posteriori (EAP).
        
        Args:
            current_theta: Student's current ability estimate
            is_correct: Whether the student answered correctly
            question_difficulty: Difficulty of the answered question (optional)
            
        Returns:
            Updated theta value
        """
        try:
            # Basic theta adjustment
            if is_correct:
                new_theta = current_theta + self.theta_adjustment
            else:
                new_theta = current_theta - self.theta_adjustment
            
            # Enhanced adjustment based on question difficulty
            if question_difficulty is not None:
                # If student got a hard question right, boost more
                # If student got an easy question wrong, penalize more
                difficulty_factor = abs(question_difficulty - current_theta)
                
                if is_correct and question_difficulty > current_theta:
                    # Correctly answered harder question
                    new_theta += difficulty_factor * 0.2
                elif not is_correct and question_difficulty < current_theta:
                    # Incorrectly answered easier question
                    new_theta -= difficulty_factor * 0.2
            
            # Clamp theta to valid range
            new_theta = max(self.min_theta, min(self.max_theta, new_theta))
            
            logger.debug(f"Updated theta: {current_theta} → {new_theta} "
                        f"(correct={is_correct}, difficulty={question_difficulty})")
            
            return new_theta
            
        except Exception as e:
            logger.error(f"Error in update_theta_simple: {e}")
            return current_theta
    
    def estimate_theta_from_bkt(self, bkt_params: Dict[str, float]) -> float:
        """
        Convert BKT mastery probability to IRT theta scale
        
        This creates a bridge between BKT (probability-based) and IRT (logit-based)
        approaches for consistent ability estimation.
        
        Args:
            bkt_params: Dictionary containing BKT parameters, must include 'P_L'
            
        Returns:
            Estimated theta value on -3 to +3 scale
        """
        try:
            # Extract mastery probability from BKT parameters
            mastery_prob = bkt_params.get('P_L', 0.5)
            
            # Ensure mastery probability is in valid range
            mastery_prob = max(0.01, min(0.99, mastery_prob))
            
            # Convert probability to logit (log-odds) scale
            # logit(p) = ln(p / (1-p))
            logit = math.log(mastery_prob / (1 - mastery_prob))
            
            # Scale logit to theta range (-3 to +3)
            # Typical logit range is about -6 to +6, so we scale by 0.5
            theta = logit * 0.5
            
            # Clamp to valid theta range
            theta = max(self.min_theta, min(self.max_theta, theta))
            
            logger.debug(f"Converted BKT P_L={mastery_prob} to theta={theta}")
            
            return theta
            
        except Exception as e:
            logger.error(f"Error in estimate_theta_from_bkt: {e}")
            return 0.0  # Default to neutral ability
    
    def estimate_theta_from_interactions(self, interactions: List[Dict]) -> float:
        """
        Estimate theta from interaction history using simple success rate
        
        Args:
            interactions: List of interaction dictionaries with 'is_correct' field
            
        Returns:
            Estimated theta value
        """
        try:
            if not interactions:
                return 0.0  # Default neutral ability
            
            # Calculate success rate
            correct_count = sum(1 for interaction in interactions 
                              if interaction.get('is_correct', False))
            success_rate = correct_count / len(interactions)
            
            # Convert success rate to theta using logit transformation
            success_rate = max(0.01, min(0.99, success_rate))  # Avoid log(0)
            logit = math.log(success_rate / (1 - success_rate))
            theta = logit * 0.5
            
            # Clamp to valid range
            theta = max(self.min_theta, min(self.max_theta, theta))
            
            logger.debug(f"Estimated theta={theta} from {len(interactions)} interactions "
                        f"(success_rate={success_rate:.3f})")
            
            return theta
            
        except Exception as e:
            logger.error(f"Error in estimate_theta_from_interactions: {e}")
            return 0.0
    
    def calculate_question_probability(self, 
                                     theta: float, 
                                     question_difficulty: float,
                                     discrimination: float = 1.0,
                                     guessing: float = 0.0) -> float:
        """
        Calculate probability of correct response using IRT model
        
        Uses the 3-Parameter Logistic (3PL) model:
        P(correct) = guessing + (1 - guessing) * (1 / (1 + exp(-discrimination * (theta - difficulty))))
        
        Args:
            theta: Student ability
            question_difficulty: Question difficulty (b parameter)
            discrimination: Question discrimination (a parameter), default 1.0
            guessing: Guessing parameter (c parameter), default 0.0
            
        Returns:
            Probability of correct response (0.0 to 1.0)
        """
        try:
            # Calculate logistic function
            exponent = -discrimination * (theta - question_difficulty)
            
            # Avoid overflow in exp function
            if exponent > 700:  # exp(700) is approximately infinity
                probability = guessing
            elif exponent < -700:
                probability = guessing + (1 - guessing)
            else:
                probability = guessing + (1 - guessing) * (1 / (1 + math.exp(exponent)))
            
            return max(0.0, min(1.0, probability))
            
        except Exception as e:
            logger.error(f"Error in calculate_question_probability: {e}")
            return 0.5  # Default to 50% probability
    
    def get_question_information(self, 
                               theta: float, 
                               question_difficulty: float,
                               discrimination: float = 1.0,
                               guessing: float = 0.0) -> float:
        """
        Calculate Fisher Information for a question at given theta
        
        Information indicates how much a question contributes to ability estimation.
        Higher information = better for ability estimation at that theta level.
        
        Args:
            theta: Student ability
            question_difficulty: Question difficulty
            discrimination: Question discrimination
            guessing: Guessing parameter
            
        Returns:
            Information value (higher = more informative)
        """
        try:
            # Calculate probability of correct response
            prob = self.calculate_question_probability(
                theta, question_difficulty, discrimination, guessing
            )
            
            # Calculate information using IRT formula
            # I(theta) = a^2 * P * (1-P) * [(1-c)/(1-c*P)]^2
            if prob == 0 or prob == 1 or guessing == 1:
                return 0.0
            
            base_info = prob * (1 - prob)
            correction_factor = (1 - guessing) / (1 - guessing + guessing * prob)
            information = (discrimination ** 2) * base_info * (correction_factor ** 2)
            
            return max(0.0, information)
            
        except Exception as e:
            logger.error(f"Error in get_question_information: {e}")
            return 0.0
    
    def _filter_recent_questions(self, 
                               questions: List[Any], 
                               student_id: str) -> List[Any]:
        """
        Filter out questions that were recently shown to student
        
        Args:
            questions: List of question objects
            student_id: Student identifier
            
        Returns:
            Filtered list of questions
        """
        try:
            # Import here to avoid circular imports
            from assessment.models import Interaction
            
            # Calculate cutoff time
            cutoff_time = timezone.now() - timedelta(hours=self.exposure_window_hours)
            
            # Get recently seen question IDs
            recent_question_ids = Interaction.objects.filter(
                student_id=student_id,
                timestamp__gte=cutoff_time
            ).values_list('question_id', flat=True).distinct()
            
            # Filter out recently seen questions
            filtered_questions = [
                q for q in questions 
                if getattr(q, 'id', None) not in recent_question_ids
            ]
            
            logger.debug(f"Filtered {len(questions)} questions to {len(filtered_questions)} "
                        f"(excluded {len(recent_question_ids)} recent)")
            
            return filtered_questions
            
        except Exception as e:
            logger.error(f"Error in _filter_recent_questions: {e}")
            return questions  # Return all questions if filtering fails


class IRTAdaptiveSelector:
    """
    High-level adaptive question selector that integrates IRT with BKT/DKT
    """
    
    def __init__(self, irt_engine: Optional[IRTEngine] = None):
        """Initialize with optional IRT engine"""
        self.irt_engine = irt_engine or IRTEngine()
    
    def select_next_question(self, 
                           student_id: str,
                           skill_id: Optional[str] = None,
                           use_bkt_integration: bool = True,
                           level_based_filtering: bool = True) -> Optional[Any]:
        """
        Select next optimal question for student using integrated approach with level progression
        
        Args:
            student_id: Student identifier
            skill_id: Target skill (optional)
            use_bkt_integration: Whether to use BKT for theta estimation
            level_based_filtering: Whether to filter questions by unlocked levels
            
        Returns:
            Selected AdaptiveQuestion object or None
        """
        try:
            # Import models here to avoid circular imports
            from core.models import StudentProfile
            from assessment.models import AdaptiveQuestion, Interaction
            from student_model.level_progression import LevelProgressionService
            
            # Get student profile
            try:
                student = StudentProfile.objects.get(id=student_id)
            except StudentProfile.DoesNotExist:
                logger.error(f"Student {student_id} not found")
                return None
            
            # Estimate current theta (ability)
            if use_bkt_integration and student.bkt_parameters:
                # Use BKT parameters if available
                bkt_params = student.bkt_parameters.get(skill_id, {}) if skill_id else {}
                if bkt_params:
                    theta = self.irt_engine.estimate_theta_from_bkt(bkt_params)
                else:
                    theta = self._estimate_theta_from_history(student)
            else:
                # Use interaction history
                theta = self._estimate_theta_from_history(student)
            
            # Get available questions with level filtering
            questions = AdaptiveQuestion.objects.all()
            if skill_id:
                questions = questions.filter(skill_id=skill_id)
                
                # Apply level-based filtering
                if level_based_filtering:
                    progression_service = LevelProgressionService()
                    available_levels = progression_service.get_available_question_levels(student, skill_id)
                    questions = questions.filter(level__in=available_levels)
                    
                    logger.info(f"Filtered questions for {skill_id} to levels {available_levels}")
            
            # Get active questions
            questions = questions.filter(is_active=True)
            
            # Select optimal question
            selected_question = self.irt_engine.select_question_for_theta(
                item_bank=list(questions),
                theta=theta,
                skill_id=skill_id,
                student_id=student_id
            )
            
            if selected_question:
                logger.info(f"Selected question {selected_question.id} for student {student_id} "
                           f"(theta={theta:.3f}, skill={skill_id})")
            
            return selected_question
            
        except Exception as e:
            logger.error(f"Error in select_next_question: {e}")
            return None
    
    def _estimate_theta_from_history(self, student) -> float:
        """Estimate theta from student's interaction history"""
        try:
            from assessment.models import Interaction
            
            # Get recent interactions
            interactions = Interaction.objects.filter(
                student=student.user if hasattr(student, 'user') else student
            ).order_by('-timestamp')[:20].values('is_correct')
            
            interaction_list = [
                {'is_correct': interaction['is_correct']} 
                for interaction in interactions
            ]
            
            return self.irt_engine.estimate_theta_from_interactions(interaction_list)
            
        except Exception as e:
            logger.error(f"Error estimating theta from history: {e}")
            return 0.0


# Utility functions for IRT calculations
def convert_difficulty_to_irt_scale(raw_difficulty: float, 
                                  min_raw: float = 0.0, 
                                  max_raw: float = 1.0) -> float:
    """
    Convert raw difficulty score to IRT theta scale (-3 to +3)
    
    Args:
        raw_difficulty: Raw difficulty score
        min_raw: Minimum raw difficulty value
        max_raw: Maximum raw difficulty value
        
    Returns:
        Difficulty on IRT scale
    """
    try:
        # Normalize to 0-1 range
        normalized = (raw_difficulty - min_raw) / (max_raw - min_raw)
        normalized = max(0.0, min(1.0, normalized))
        
        # Convert to IRT scale (-3 to +3)
        # 0.5 normalized = 0 theta (average difficulty)
        irt_difficulty = (normalized - 0.5) * 6
        
        return max(-3.0, min(3.0, irt_difficulty))
        
    except Exception as e:
        logger.error(f"Error converting difficulty to IRT scale: {e}")
        return 0.0


def theta_to_probability_scale(theta: float) -> float:
    """
    Convert theta to probability scale (0-1) for easier interpretation
    
    Args:
        theta: Ability on IRT scale (-3 to +3)
        
    Returns:
        Probability scale equivalent (0.0 to 1.0)
    """
    try:
        # Convert theta to probability using logistic function
        # Scaled so that theta=0 -> prob=0.5, theta=3 -> prob≈0.95, theta=-3 -> prob≈0.05
        probability = 1 / (1 + math.exp(-theta))
        return max(0.0, min(1.0, probability))
        
    except Exception as e:
        logger.error(f"Error converting theta to probability: {e}")
        return 0.5