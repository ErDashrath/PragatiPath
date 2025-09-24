from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Avg, Q

from .models import SRSCard
from .sm2 import SM2Scheduler, SM2AdaptiveSelector
from assessment.models import AdaptiveQuestion

router = Router()
logger = logging.getLogger(__name__)

# Initialize SM-2 components
sm2_scheduler = SM2Scheduler()
sm2_selector = SM2AdaptiveSelector(sm2_scheduler)

class CardStatus(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    GRADUATED = "graduated"

class ReviewResult(str, Enum):
    AGAIN = "again"      # Hard to remember
    HARD = "hard"        # Difficult but correct
    GOOD = "good"        # Correct with some effort
    EASY = "easy"        # Very easy

# ============================================================================
# SM-2 Spaced Repetition System Schemas
# ============================================================================

class DueCardSchema(Schema):
    """Schema for due cards in SM-2 system"""
    card_id: str
    question_id: str
    question_text: str
    question_type: str
    stage: str
    ease_factor: float
    interval: int
    repetition: int
    due_date: datetime
    last_reviewed: Optional[datetime]
    correct_streak: int
    total_reviews: int
    success_rate: float
    average_response_time: float
    is_overdue: bool
    priority_score: float

class DueCardsResponseSchema(Schema):
    """Response schema for due cards endpoint"""
    student_id: str
    total_due: int
    cards: List[DueCardSchema]
    session_metadata: Dict[str, Any]
    study_recommendations: List[str]

class ReviewRequestSchema(Schema):
    """Schema for review submission"""
    card_id: str
    quality: int  # SM-2 quality score (0-5)
    response_time: float  # Response time in seconds
    session_id: Optional[str] = None

class ReviewResponseSchema(Schema):
    """Response schema for review processing"""
    card_id: str
    success: bool
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    review_result: Dict[str, Any]
    sm2_metadata: Dict[str, Any]
    performance_stats: Dict[str, Any]

class StudyStatsSchema(Schema):
    """Schema for study statistics"""
    student_id: str
    analysis_period_days: int
    total_cards: int
    stage_distribution: Dict[str, int]
    due_analysis: Dict[str, int]
    performance_metrics: Dict[str, float]
    learning_progress: Dict[str, int]
    session_statistics: Dict[str, Any]
    recommendations: List[str]

class OptimalStudySetSchema(Schema):
    """Schema for optimal study set selection"""
    student_id: str
    target_duration_minutes: int
    selected_cards: List[DueCardSchema]
    estimated_session_time: int
    session_metadata: Dict[str, Any]

class AddCardsRequestSchema(Schema):
    """Schema for adding cards to student deck"""
    student_id: str
    question_ids: List[str]
    initial_stage: Optional[str] = "apprentice_1"

class AddCardsResponseSchema(Schema):
    """Response schema for adding cards"""
    student_id: str
    cards_added: int
    cards_already_exist: int
    new_cards: List[Dict[str, Any]]
    success: bool

# ============================================================================
# SM-2 Spaced Repetition API Endpoints
# ============================================================================

@router.get("/api/v1/practice/{student_id}/due-cards", 
           response=DueCardsResponseSchema,
           tags=["SM-2 Spaced Repetition"])
def get_due_cards_sm2(request, student_id: str, limit: int = 20, 
                      stage_filter: Optional[str] = None):
    """
    Get cards due for review using SM-2 algorithm.
    
    Returns cards that are due for review, ordered by priority score.
    Includes comprehensive metadata for optimal study sessions.
    """
    try:
        # Parse stage filter if provided
        include_stages = None
        if stage_filter:
            include_stages = [s.strip() for s in stage_filter.split(',')]
        
        # Get due cards using SM-2 scheduler
        due_cards_data = sm2_scheduler.get_due_cards(
            student_id=student_id,
            limit=limit,
            include_stage_filter=include_stages
        )
        
        # Convert to schema format
        cards = []
        for card_data in due_cards_data:
            card_schema = DueCardSchema(**card_data)
            cards.append(card_schema)
        
        # Generate session metadata
        session_metadata = {
            "total_requested": limit,
            "stage_filter_applied": stage_filter is not None,
            "estimated_session_time_minutes": len(cards) * 0.5,  # 30 seconds per card
            "priority_range": {
                "min": min((card.priority_score for card in cards), default=0),
                "max": max((card.priority_score for card in cards), default=0)
            }
        }
        
        # Get study recommendations
        try:
            student_stats = sm2_scheduler.get_review_statistics(student_id, days=7)
            recommendations = student_stats.get('recommendations', [])
        except:
            recommendations = ["Start reviewing your due cards!"]
        
        return {
            "student_id": student_id,
            "total_due": len(cards),
            "cards": cards,
            "session_metadata": session_metadata,
            "study_recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting due cards for student {student_id}: {e}")
        raise HttpError(500, f"Failed to get due cards: {str(e)}")


@router.post("/api/v1/practice/review", 
            response=ReviewResponseSchema,
            tags=["SM-2 Spaced Repetition"])
def process_review_sm2(request, payload: ReviewRequestSchema):
    """
    Process a review using SM-2 algorithm.
    
    Updates card parameters, calculates new intervals, and manages
    SRS stage progressions based on review quality.
    """
    try:
        # Validate quality score
        if not (0 <= payload.quality <= 5):
            raise HttpError(400, "Quality must be between 0 and 5")
        
        # Process the review using SM-2 scheduler
        review_result = sm2_scheduler.process_review(
            card_id=payload.card_id,
            quality=payload.quality,
            response_time=payload.response_time
        )
        
        if not review_result.get('success', False):
            error_msg = review_result.get('error', 'Unknown error')
            raise HttpError(500, f"Review processing failed: {error_msg}")
        
        return ReviewResponseSchema(**review_result)
        
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error processing review: {e}")
        raise HttpError(500, f"Review processing failed: {str(e)}")


@router.get("/api/v1/practice/{student_id}/stats", 
           response=StudyStatsSchema,
           tags=["SM-2 Analytics"])
def get_study_statistics_sm2(request, student_id: str, days: int = 30):
    """
    Get comprehensive study statistics using SM-2 analytics.
    
    Provides detailed analysis of learning progress, performance metrics,
    and personalized recommendations.
    """
    try:
        # Get statistics from SM-2 scheduler
        stats_data = sm2_scheduler.get_review_statistics(student_id, days=days)
        
        if 'error' in stats_data:
            raise HttpError(500, f"Statistics error: {stats_data['error']}")
        
        return StudyStatsSchema(**stats_data)
        
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics for student {student_id}: {e}")
        raise HttpError(500, f"Statistics retrieval failed: {str(e)}")


@router.get("/api/v1/practice/{student_id}/optimal-study-set",
           response=OptimalStudySetSchema,
           tags=["SM-2 Optimization"])
def get_optimal_study_set(request, student_id: str, 
                         target_duration: int = 20, max_cards: int = 50):
    """
    Get optimally selected study set for maximum learning efficiency.
    
    Uses SM-2 adaptive selection to choose the best cards for a
    targeted study session duration.
    """
    try:
        # Get optimal study set
        selected_cards_data = sm2_selector.select_optimal_study_set(
            student_id=student_id,
            target_duration=target_duration,
            max_cards=max_cards
        )
        
        # Convert to schema format
        selected_cards = []
        for card_data in selected_cards_data:
            card_schema = DueCardSchema(**card_data)
            selected_cards.append(card_schema)
        
        # Estimate actual session time
        estimated_time = len(selected_cards) * 0.5  # 30 seconds per card average
        
        # Generate session metadata
        session_metadata = {
            "selection_algorithm": "SM-2 Adaptive",
            "target_duration_minutes": target_duration,
            "actual_cards_selected": len(selected_cards),
            "estimated_completion_time": estimated_time,
            "efficiency_score": min(1.0, target_duration / max(estimated_time, 1)),
            "stage_variety": len(set(card.stage for card in selected_cards))
        }
        
        return {
            "student_id": student_id,
            "target_duration_minutes": target_duration,
            "selected_cards": selected_cards,
            "estimated_session_time": int(estimated_time),
            "session_metadata": session_metadata
        }
        
    except Exception as e:
        logger.error(f"Error selecting optimal study set for {student_id}: {e}")
        raise HttpError(500, f"Optimal study set selection failed: {str(e)}")


@router.post("/api/v1/practice/add-cards",
            response=AddCardsResponseSchema,
            tags=["SM-2 Card Management"])
def add_cards_to_student_sm2(request, payload: AddCardsRequestSchema):
    """
    Add new cards to student's SRS deck.
    
    Creates new SRS cards with SM-2 parameters initialized.
    Handles duplicate detection and batch processing.
    """
    try:
        with transaction.atomic():
            # Verify student exists
            try:
                student = User.objects.get(id=payload.student_id)
            except User.DoesNotExist:
                raise HttpError(404, f"Student {payload.student_id} not found")
            
            # Get questions
            questions = AdaptiveQuestion.objects.filter(
                id__in=payload.question_ids,
                is_active=True
            )
            
            if not questions.exists():
                raise HttpError(404, "No valid questions found")
            
            # Check for existing cards
            existing_card_questions = set(
                SRSCard.objects.filter(
                    student=student,
                    question__id__in=payload.question_ids
                ).values_list('question_id', flat=True)
            )
            
            # Create new cards
            new_cards = []
            cards_created = 0
            
            for question in questions:
                if question.id not in existing_card_questions:
                    card = SRSCard.objects.create(
                        student=student,
                        question=question,
                        stage=payload.initial_stage,
                        ease_factor=sm2_scheduler.DEFAULT_EASE_FACTOR,
                        interval=1,
                        repetition=0,
                        due_date=timezone.now(),  # Available immediately
                    )
                    
                    new_cards.append({
                        "card_id": str(card.id),
                        "question_id": str(question.id),
                        "question_text": question.question_text[:50] + "...",
                        "stage": card.stage,
                        "due_date": card.due_date
                    })
                    cards_created += 1
            
            return {
                "student_id": payload.student_id,
                "cards_added": cards_created,
                "cards_already_exist": len(existing_card_questions),
                "new_cards": new_cards,
                "success": True
            }
            
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Error adding cards to student {payload.student_id}: {e}")
        raise HttpError(500, f"Card addition failed: {str(e)}")


@router.get("/api/v1/practice/{student_id}/difficult-cards",
           response=List[DueCardSchema],
           tags=["SM-2 Analytics"])
def get_difficult_cards_sm2(request, student_id: str, limit: int = 10):
    """
    Get cards that the student finds most difficult.
    
    Identifies cards with low ease factors, high incorrect counts,
    or poor success rates for targeted practice.
    """
    try:
        # Query for difficult cards
        difficult_cards_query = SRSCard.objects.filter(
            student_id=student_id,
            is_suspended=False
        ).filter(
            Q(ease_factor__lt=2.0) |  # Low ease factor
            Q(incorrect_count__gte=3) |  # Many incorrect answers
            Q(correct_streak=0)  # Currently struggling
        ).select_related('question').order_by(
            'ease_factor', '-incorrect_count', 'due_date'
        )[:limit]
        
        # Convert to due card format
        difficult_cards = []
        for card in difficult_cards_query:
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
                'is_overdue': card.due_date < timezone.now(),
                'priority_score': sm2_scheduler._calculate_priority_score(card)
            }
            difficult_cards.append(DueCardSchema(**card_data))
        
        return difficult_cards
        
    except Exception as e:
        logger.error(f"Error getting difficult cards for student {student_id}: {e}")
        raise HttpError(500, f"Difficult cards retrieval failed: {str(e)}")


@router.post("/api/v1/practice/{student_id}/reset-card/{card_id}",
            tags=["SM-2 Card Management"])
def reset_card_sm2(request, student_id: str, card_id: str):
    """
    Reset a card back to apprentice level.
    
    Useful for cards that have become too difficult or need fresh start.
    """
    try:
        with transaction.atomic():
            card = SRSCard.objects.select_for_update().get(
                id=card_id,
                student_id=student_id
            )
            
            old_stage = card.stage
            card.reset_to_apprentice()
            
            return {
                "success": True,
                "card_id": card_id,
                "message": f"Card reset from {old_stage} to {card.stage}",
                "new_due_date": card.due_date
            }
            
    except SRSCard.DoesNotExist:
        raise HttpError(404, f"Card {card_id} not found for student {student_id}")
    except Exception as e:
        logger.error(f"Error resetting card {card_id}: {e}")
        raise HttpError(500, f"Card reset failed: {str(e)}")


@router.get("/api/v1/practice/{student_id}/session-summary",
           tags=["SM-2 Analytics"])
def get_session_summary(request, student_id: str):
    """
    Get current session summary statistics.
    
    Shows progress within the current study session.
    """
    try:
        session_stats = sm2_scheduler.session_stats.copy()
        
        # Calculate derived metrics
        accuracy = 0.0
        avg_response_time = 0.0
        
        if session_stats['cards_reviewed'] > 0:
            accuracy = session_stats['correct_answers'] / session_stats['cards_reviewed']
        
        if session_stats['total_response_time'] > 0 and session_stats['cards_reviewed'] > 0:
            avg_response_time = session_stats['total_response_time'] / session_stats['cards_reviewed']
        
        return {
            "student_id": student_id,
            "session_stats": session_stats,
            "derived_metrics": {
                "accuracy_rate": round(accuracy, 3),
                "average_response_time": round(avg_response_time, 1),
                "cards_per_progression": (
                    session_stats['cards_reviewed'] / max(1, session_stats['stage_progressions'])
                )
            },
            "session_active": session_stats['cards_reviewed'] > 0
        }
        
    except Exception as e:
        logger.error(f"Error getting session summary for {student_id}: {e}")
        raise HttpError(500, f"Session summary failed: {str(e)}")


@router.post("/api/v1/practice/reset-session",
            tags=["SM-2 Session Management"])
def reset_session_stats(request):
    """
    Reset session statistics for new study session.
    
    Clears current session counters and timers.
    """
    try:
        sm2_scheduler.reset_session_stats()
        
        return {
            "success": True,
            "message": "Session statistics reset",
            "new_session_stats": sm2_scheduler.session_stats
        }
        
    except Exception as e:
        logger.error(f"Error resetting session stats: {e}")
        raise HttpError(500, f"Session reset failed: {str(e)}")


@router.get("/status")
def practice_status(request):
    """Practice app status endpoint with SM-2 integration"""
    return {
        "app": "practice", 
        "status": "ready", 
        "description": "SM-2 Spaced Repetition System with WaniKani-style progression",
        "features": [
            "SM-2 Algorithm Implementation", 
            "WaniKani-style SRS Stages",
            "Adaptive Card Selection", 
            "Performance Analytics",
            "Session Management",
            "Difficulty Analysis",
            "Optimal Study Scheduling"
        ],
        "algorithms": {
            "sm2": {
                "status": "implemented",
                "version": "Enhanced SuperMemo-2",
                "features": ["mathematical_intervals", "ease_factor_optimization", "stage_progression"]
            }
        },
        "endpoints": {
            "due_cards": "/api/v1/practice/{student_id}/due-cards",
            "process_review": "/api/v1/practice/review",
            "statistics": "/api/v1/practice/{student_id}/stats",
            "optimal_study": "/api/v1/practice/{student_id}/optimal-study-set",
            "add_cards": "/api/v1/practice/add-cards"
        }
    }