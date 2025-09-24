"""
SM-2 Spaced Repetition Algorithm Implementation
Enhanced version with WaniKani-style progression stages and Django ORM integration.

SuperMemo-2 Algorithm:
- Quality grades: 0-5 (0=wrong, 5=perfect)
- Ease Factor: Starting at 2.5, modified by performance
- Intervals: Calculated based on ease factor and repetition count
"""

import math
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.db import transaction
from .models import SRSCard

logger = logging.getLogger(__name__)


class SM2Scheduler:
    """
    SuperMemo-2 Algorithm implementation with WaniKani-style stage progression.
    
    Features:
    - Pure mathematical SM-2 calculations
    - WaniKani-style SRS stage management
    - Performance tracking and analytics  
    - Exposure control and optimization
    - Django ORM integration
    """
    
    # SM-2 Algorithm constants
    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    EASE_FACTOR_MODIFIER = 0.1
    EASE_FACTOR_PENALTY = 0.08
    EASE_FACTOR_BONUS = 0.02
    
    # Quality thresholds
    FAILURE_THRESHOLD = 3  # Below this is considered failure
    PERFECT_SCORE = 5      # Perfect recall
    
    # WaniKani-style stage progression requirements
    STAGE_PROGRESSION_REQUIREMENTS = {
        'apprentice_1': {'correct_streak': 1, 'min_reviews': 1},
        'apprentice_2': {'correct_streak': 1, 'min_reviews': 1},
        'apprentice_3': {'correct_streak': 1, 'min_reviews': 1},
        'apprentice_4': {'correct_streak': 1, 'min_reviews': 1},
        'guru_1': {'correct_streak': 2, 'min_reviews': 2},
        'guru_2': {'correct_streak': 2, 'min_reviews': 2},
        'master': {'correct_streak': 3, 'min_reviews': 3},
        'enlightened': {'correct_streak': 4, 'min_reviews': 4},
        'burned': {'correct_streak': 5, 'min_reviews': 5}
    }
    
    def __init__(self):
        """Initialize SM-2 scheduler"""
        self.session_stats = {
            'cards_reviewed': 0,
            'correct_answers': 0,
            'total_response_time': 0.0,
            'stage_progressions': 0
        }
    
    def calculate_sm2_parameters(self, 
                                current_ease_factor: float,
                                current_interval: int,
                                current_repetition: int,
                                quality: int,
                                response_time: float = 0.0) -> Dict:
        """
        Calculate new SM-2 parameters based on review quality.
        
        Args:
            current_ease_factor: Current ease factor (minimum 1.3)
            current_interval: Current interval in days
            current_repetition: Number of successful repetitions
            quality: Review quality (0-5, where 0=wrong, 5=perfect)
            response_time: Response time in seconds (optional)
            
        Returns:
            Dict with new SM-2 parameters and metadata
        """
        try:
            # Initialize result
            result = {
                'ease_factor': current_ease_factor,
                'interval': current_interval,
                'repetition': current_repetition,
                'is_correct': quality >= self.FAILURE_THRESHOLD,
                'quality_rating': self._get_quality_rating(quality),
                'response_time': response_time,
                'calculation_metadata': {}
            }
            
            if quality < self.FAILURE_THRESHOLD:
                # Failed review - reset progress
                result['repetition'] = 0
                result['interval'] = 1
                result['ease_factor'] = max(
                    self.MIN_EASE_FACTOR,
                    current_ease_factor - 0.15  # Penalty for failure
                )
                result['calculation_metadata']['action'] = 'reset_due_to_failure'
                
            else:
                # Successful review - calculate new parameters
                result['repetition'] = current_repetition + 1
                
                # Update ease factor based on quality
                ease_change = (
                    self.EASE_FACTOR_MODIFIER - 
                    (self.PERFECT_SCORE - quality) * 
                    (self.EASE_FACTOR_PENALTY + (self.PERFECT_SCORE - quality) * self.EASE_FACTOR_BONUS)
                )
                result['ease_factor'] = max(self.MIN_EASE_FACTOR, current_ease_factor + ease_change)
                
                # Calculate new interval using SM-2 formula
                if result['repetition'] == 1:
                    result['interval'] = 1
                elif result['repetition'] == 2:
                    result['interval'] = 6
                else:
                    result['interval'] = max(1, round(current_interval * result['ease_factor']))
                
                # Apply response time modifier (faster = slightly easier next time)
                if response_time > 0:
                    time_factor = self._calculate_time_factor(response_time, quality)
                    result['interval'] = max(1, round(result['interval'] * time_factor))
                    result['calculation_metadata']['time_factor_applied'] = time_factor
                
                result['calculation_metadata']['action'] = 'successful_advancement'
            
            # Calculate next due date
            result['next_due_date'] = timezone.now() + timedelta(days=result['interval'])
            result['calculation_metadata']['ease_factor_change'] = result['ease_factor'] - current_ease_factor
            
            return result
            
        except Exception as e:
            logger.error(f"Error in SM-2 calculation: {e}")
            # Return safe defaults
            return {
                'ease_factor': current_ease_factor,
                'interval': max(1, current_interval),
                'repetition': current_repetition,
                'is_correct': False,
                'next_due_date': timezone.now() + timedelta(days=1),
                'error': str(e)
            }
    
    def process_review(self, card_id: str, quality: int, response_time: float = 0.0) -> Dict:
        """
        Process a single card review using SM-2 algorithm with full database update.
        
        Args:
            card_id: UUID of the SRS card
            quality: Review quality (0-5)
            response_time: Response time in seconds
            
        Returns:
            Dict with updated card state and review results
        """
        try:
            with transaction.atomic():
                # Get the card
                try:
                    card = SRSCard.objects.select_for_update().get(id=card_id)
                except SRSCard.DoesNotExist:
                    return {'error': f'Card {card_id} not found'}
                
                # Store previous state for comparison
                previous_state = {
                    'stage': card.stage,
                    'ease_factor': card.ease_factor,
                    'interval': card.interval,
                    'repetition': card.repetition
                }
                
                # Calculate new SM-2 parameters
                sm2_result = self.calculate_sm2_parameters(
                    current_ease_factor=card.ease_factor,
                    current_interval=card.interval,
                    current_repetition=card.repetition,
                    quality=quality,
                    response_time=response_time
                )
                
                # Update card with SM-2 results
                card.ease_factor = sm2_result['ease_factor']
                card.interval = sm2_result['interval']
                card.repetition = sm2_result['repetition']
                card.due_date = sm2_result['next_due_date']
                card.last_reviewed = timezone.now()
                card.total_reviews += 1
                
                # Update performance tracking
                if sm2_result['is_correct']:
                    card.correct_streak += 1
                else:
                    card.correct_streak = 0
                    card.incorrect_count += 1
                
                # Update average response time
                if response_time > 0:
                    if card.average_response_time == 0:
                        card.average_response_time = response_time
                    else:
                        # Running average
                        card.average_response_time = (
                            (card.average_response_time * (card.total_reviews - 1) + response_time) /
                            card.total_reviews
                        )
                
                # Handle SRS stage progression
                stage_changed = self._update_srs_stage(card, quality)
                
                # Save all changes
                card.save()
                
                # Update session statistics
                self._update_session_stats(sm2_result['is_correct'], response_time, stage_changed)
                
                # Prepare response
                return {
                    'card_id': str(card.id),
                    'success': True,
                    'previous_state': previous_state,
                    'new_state': {
                        'stage': card.stage,
                        'ease_factor': card.ease_factor,
                        'interval': card.interval,
                        'repetition': card.repetition,
                        'due_date': card.due_date,
                        'correct_streak': card.correct_streak
                    },
                    'review_result': {
                        'quality': quality,
                        'is_correct': sm2_result['is_correct'],
                        'quality_rating': sm2_result['quality_rating'],
                        'response_time': response_time,
                        'stage_changed': stage_changed
                    },
                    'sm2_metadata': sm2_result.get('calculation_metadata', {}),
                    'performance_stats': {
                        'total_reviews': card.total_reviews,
                        'success_rate': card.success_rate,
                        'average_response_time': card.average_response_time
                    }
                }
                
        except Exception as e:
            logger.error(f"Error processing review for card {card_id}: {e}")
            return {'error': str(e), 'success': False}
    
    def get_due_cards(self, student_id: str, limit: int = 20, 
                     include_stage_filter: Optional[List[str]] = None) -> List[Dict]:
        """
        Get cards due for review using optimized database queries.
        
        Args:
            student_id: Student's user ID
            limit: Maximum number of cards to return
            include_stage_filter: Optional list of stages to include
            
        Returns:
            List of due cards with metadata
        """
        try:
            # Base query for due cards
            query = SRSCard.objects.filter(
                student_id=student_id,
                due_date__lte=timezone.now(),
                is_suspended=False,
                is_locked=False
            ).select_related('question').order_by('due_date', 'stage')
            
            # Apply stage filter if provided
            if include_stage_filter:
                query = query.filter(stage__in=include_stage_filter)
            
            # Limit results
            due_cards = query[:limit]
            
            # Format cards for response
            card_list = []
            for card in due_cards:
                card_data = {
                    'card_id': str(card.id),
                    'question_id': str(card.question.id),
                    'question_text': card.question.question_text,
                    'question_type': card.question.question_type,
                    'stage': card.stage,
                    'ease_factor': card.ease_factor,
                    'interval': card.interval,
                    'repetition': card.repetition,
                    'due_date': card.due_date,
                    'last_reviewed': card.last_reviewed,
                    'correct_streak': card.correct_streak,
                    'total_reviews': card.total_reviews,
                    'success_rate': card.success_rate,
                    'average_response_time': card.average_response_time,
                    'is_overdue': card.due_date < timezone.now() - timedelta(hours=1),
                    'priority_score': self._calculate_priority_score(card)
                }
                card_list.append(card_data)
            
            return card_list
            
        except Exception as e:
            logger.error(f"Error getting due cards for student {student_id}: {e}")
            return []
    
    def get_review_statistics(self, student_id: str, days: int = 30) -> Dict:
        """
        Generate comprehensive review statistics for a student.
        
        Args:
            student_id: Student's user ID
            days: Number of days to analyze (default 30)
            
        Returns:
            Dict with detailed statistics
        """
        try:
            from django.db.models import Count, Avg, Q
            from django.utils import timezone
            
            # Get all cards for the student
            cards = SRSCard.objects.filter(student_id=student_id)
            
            # Date range for analysis
            cutoff_date = timezone.now() - timedelta(days=days)
            recent_cards = cards.filter(last_reviewed__gte=cutoff_date)
            
            # Basic counts by stage
            stage_counts = cards.values('stage').annotate(count=Count('id'))
            stage_distribution = {item['stage']: item['count'] for item in stage_counts}
            
            # Due cards analysis
            due_now = cards.filter(due_date__lte=timezone.now(), is_suspended=False).count()
            overdue = cards.filter(due_date__lt=timezone.now() - timedelta(hours=1)).count()
            
            # Performance metrics
            total_reviews = sum(card.total_reviews for card in cards)
            total_correct = sum(card.total_reviews - card.incorrect_count for card in cards)
            overall_success_rate = total_correct / total_reviews if total_reviews > 0 else 0
            
            # Average statistics
            avg_ease_factor = cards.aggregate(Avg('ease_factor'))['ease_factor__avg'] or self.DEFAULT_EASE_FACTOR
            avg_response_time = cards.filter(average_response_time__gt=0).aggregate(
                Avg('average_response_time'))['average_response_time__avg'] or 0
            
            # Learning progress analysis
            advanced_stages = ['guru_1', 'guru_2', 'master', 'enlightened', 'burned']
            mastered_cards = cards.filter(stage__in=advanced_stages).count()
            mastery_rate = mastered_cards / cards.count() if cards.count() > 0 else 0
            
            # Session statistics (if available)
            session_stats = self.session_stats.copy()
            
            return {
                'student_id': student_id,
                'analysis_period_days': days,
                'total_cards': cards.count(),
                'stage_distribution': stage_distribution,
                'due_analysis': {
                    'due_now': due_now,
                    'overdue': overdue,
                    'next_24h': cards.filter(
                        due_date__range=[timezone.now(), timezone.now() + timedelta(days=1)]
                    ).count()
                },
                'performance_metrics': {
                    'total_reviews': total_reviews,
                    'overall_success_rate': round(overall_success_rate, 3),
                    'average_ease_factor': round(avg_ease_factor, 2),
                    'average_response_time': round(avg_response_time, 1),
                    'mastery_rate': round(mastery_rate, 3)
                },
                'learning_progress': {
                    'mastered_cards': mastered_cards,
                    'cards_in_learning': cards.filter(
                        stage__in=['apprentice_1', 'apprentice_2', 'apprentice_3', 'apprentice_4']
                    ).count(),
                    'cards_in_review': cards.filter(
                        stage__in=['guru_1', 'guru_2']
                    ).count()
                },
                'session_statistics': session_stats,
                'recommendations': self._generate_study_recommendations(cards, stage_distribution)
            }
            
        except Exception as e:
            logger.error(f"Error generating statistics for student {student_id}: {e}")
            return {'error': str(e)}
    
    def _update_srs_stage(self, card: SRSCard, quality: int) -> bool:
        """
        Update SRS stage based on performance and progression requirements.
        
        Args:
            card: SRSCard instance
            quality: Review quality (0-5)
            
        Returns:
            bool: True if stage changed
        """
        original_stage = card.stage
        
        if quality < self.FAILURE_THRESHOLD:
            # Failed review - demote stage
            stage_list = [choice[0] for choice in SRSCard.SRS_STAGES]
            current_index = stage_list.index(card.stage)
            
            # Move back 1-2 stages based on current stage
            if card.stage in ['burned', 'enlightened', 'master']:
                new_index = max(0, current_index - 2)  # Bigger penalty for advanced stages
            else:
                new_index = max(0, current_index - 1)
            
            card.stage = stage_list[new_index]
            
        else:
            # Successful review - check for promotion
            requirements = self.STAGE_PROGRESSION_REQUIREMENTS.get(card.stage, {})
            required_streak = requirements.get('correct_streak', 1)
            required_reviews = requirements.get('min_reviews', 1)
            
            if (card.correct_streak >= required_streak and 
                card.total_reviews >= required_reviews and
                card.stage != 'burned'):
                
                # Advance to next stage
                stage_list = [choice[0] for choice in SRSCard.SRS_STAGES]
                current_index = stage_list.index(card.stage)
                
                if current_index < len(stage_list) - 1:
                    card.stage = stage_list[current_index + 1]
        
        return card.stage != original_stage
    
    def _calculate_time_factor(self, response_time: float, quality: int) -> float:
        """
        Calculate time-based interval modifier.
        
        Args:
            response_time: Response time in seconds
            quality: Review quality (0-5)
            
        Returns:
            float: Time factor (0.8 to 1.2)
        """
        if response_time <= 0:
            return 1.0
        
        # Expected response time based on quality
        expected_times = {5: 2.0, 4: 4.0, 3: 8.0, 2: 15.0, 1: 30.0, 0: 60.0}
        expected = expected_times.get(quality, 10.0)
        
        # Calculate ratio
        ratio = response_time / expected
        
        # Convert to factor (faster response = slight interval reduction)
        if ratio < 0.5:  # Very fast
            return 0.95
        elif ratio < 1.0:  # Fast
            return 0.98
        elif ratio < 2.0:  # Normal
            return 1.0
        elif ratio < 4.0:  # Slow
            return 1.05
        else:  # Very slow
            return 1.1
    
    def _calculate_priority_score(self, card: SRSCard) -> float:
        """
        Calculate priority score for card ordering.
        Higher score = higher priority for review.
        """
        score = 0.0
        
        # Overdue factor
        if card.due_date < timezone.now():
            overdue_hours = (timezone.now() - card.due_date).total_seconds() / 3600
            score += min(10.0, overdue_hours * 0.1)
        
        # Difficulty factor (lower ease = higher priority)
        score += (self.DEFAULT_EASE_FACTOR - card.ease_factor) * 2
        
        # Stage priority (earlier stages get priority)
        stage_priorities = {
            'apprentice_1': 10, 'apprentice_2': 9, 'apprentice_3': 8, 'apprentice_4': 7,
            'guru_1': 6, 'guru_2': 5, 'master': 4, 'enlightened': 3, 'burned': 1
        }
        score += stage_priorities.get(card.stage, 5)
        
        return round(score, 2)
    
    def _get_quality_rating(self, quality: int) -> str:
        """Convert numeric quality to descriptive rating"""
        ratings = {
            0: 'wrong', 1: 'very_hard', 2: 'hard',
            3: 'good', 4: 'easy', 5: 'perfect'
        }
        return ratings.get(quality, 'unknown')
    
    def _update_session_stats(self, is_correct: bool, response_time: float, stage_changed: bool):
        """Update session statistics"""
        self.session_stats['cards_reviewed'] += 1
        if is_correct:
            self.session_stats['correct_answers'] += 1
        if response_time > 0:
            self.session_stats['total_response_time'] += response_time
        if stage_changed:
            self.session_stats['stage_progressions'] += 1
    
    def _generate_study_recommendations(self, cards, stage_distribution: Dict) -> List[str]:
        """Generate study recommendations based on card analysis"""
        recommendations = []
        total_cards = cards.count()
        
        if total_cards == 0:
            recommendations.append("Start by adding some cards to study!")
            return recommendations
        
        # Check stage balance
        apprentice_count = sum(stage_distribution.get(f'apprentice_{i}', 0) for i in range(1, 5))
        if apprentice_count / total_cards > 0.6:
            recommendations.append("Focus on reviewing apprentice-level cards to advance them")
        
        # Check for difficult cards
        difficult_cards = cards.filter(ease_factor__lt=2.0).count()
        if difficult_cards > total_cards * 0.2:
            recommendations.append("Review your most difficult cards more frequently")
        
        # Check for overdue cards
        overdue_count = cards.filter(due_date__lt=timezone.now() - timedelta(hours=1)).count()
        if overdue_count > 0:
            recommendations.append(f"You have {overdue_count} overdue cards - prioritize these!")
        
        return recommendations
    
    def reset_session_stats(self):
        """Reset session statistics"""
        self.session_stats = {
            'cards_reviewed': 0,
            'correct_answers': 0,
            'total_response_time': 0.0,
            'stage_progressions': 0
        }


class SM2AdaptiveSelector:
    """
    Adaptive card selector that works with SM-2 scheduler for optimal study sessions.
    """
    
    def __init__(self, scheduler: SM2Scheduler):
        self.scheduler = scheduler
    
    def select_optimal_study_set(self, student_id: str, target_duration: int = 20, 
                                max_cards: int = 50) -> List[Dict]:
        """
        Select optimal set of cards for a study session.
        
        Args:
            student_id: Student's user ID
            target_duration: Target session duration in minutes
            max_cards: Maximum number of cards to include
            
        Returns:
            List of optimally selected cards
        """
        try:
            # Get all due cards
            due_cards = self.scheduler.get_due_cards(student_id, limit=max_cards * 2)
            
            if not due_cards:
                return []
            
            # Estimate time per card based on average response time
            estimated_time_per_card = 30  # seconds, default estimate
            if due_cards[0]['average_response_time'] > 0:
                estimated_time_per_card = max(15, min(120, due_cards[0]['average_response_time'] * 1.5))
            
            # Calculate how many cards fit in target duration
            target_cards = min(max_cards, (target_duration * 60) // estimated_time_per_card)
            
            # Sort by priority score (descending)
            sorted_cards = sorted(due_cards, key=lambda x: x['priority_score'], reverse=True)
            
            # Select top cards with some variety
            selected_cards = []
            stage_counts = {}
            
            for card in sorted_cards[:target_cards]:
                stage = card['stage']
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
                
                # Ensure stage variety (max 60% from any single stage)
                if len(selected_cards) > 5 and stage_counts[stage] / len(selected_cards) > 0.6:
                    continue
                
                selected_cards.append(card)
                
                if len(selected_cards) >= target_cards:
                    break
            
            return selected_cards
            
        except Exception as e:
            logger.error(f"Error selecting optimal study set for {student_id}: {e}")
            return []