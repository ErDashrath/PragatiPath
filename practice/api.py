from ninja import Router
from ninja import Schema
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

router = Router()

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

# SRS Schemas
class FlashcardSchema(Schema):
    id: Optional[int] = None
    knowledge_component_id: int
    front_content: str
    back_content: str
    difficulty: float
    tags: List[str] = []
    created_at: Optional[datetime] = None

class FlashcardCreateSchema(Schema):
    knowledge_component_id: int
    front_content: str
    back_content: str
    difficulty: float = 0.5
    tags: List[str] = []

class StudentCardSchema(Schema):
    id: Optional[int] = None
    student_id: int
    flashcard_id: int
    status: CardStatus
    ease_factor: float = 2.5  # SM-2 algorithm parameter
    interval: int = 1         # Days until next review
    repetitions: int = 0      # Number of successful repetitions
    next_review: datetime
    last_reviewed: Optional[datetime] = None

class ReviewSessionSchema(Schema):
    id: Optional[int] = None
    student_id: int
    cards_due: List[StudentCardSchema]
    session_start: datetime
    session_end: Optional[datetime] = None
    cards_reviewed: int = 0

class CardReviewSchema(Schema):
    student_card_id: int
    result: ReviewResult
    response_time: float  # in seconds
    review_timestamp: datetime

class SubmitReviewSchema(Schema):
    student_card_id: int
    result: ReviewResult
    response_time: float

class StudyStatsSchema(Schema):
    student_id: int
    total_cards: int
    new_cards: int
    learning_cards: int
    review_cards: int
    graduated_cards: int
    daily_streak: int
    next_review_time: Optional[datetime] = None

# Flashcard management
@router.get("/flashcards", response=List[FlashcardSchema])
def list_flashcards(request, knowledge_component_id: Optional[int] = None):
    """Get all flashcards, optionally filtered by knowledge component"""
    # TODO: Implement actual database query
    return [
        {
            "id": 1,
            "knowledge_component_id": 1,
            "front_content": "What is the quadratic formula?",
            "back_content": "x = (-b ± √(b²-4ac)) / 2a",
            "difficulty": 0.7,
            "tags": ["algebra", "quadratic", "formula"],
            "created_at": datetime.now()
        }
    ]

@router.post("/flashcards", response=FlashcardSchema)
def create_flashcard(request, payload: FlashcardCreateSchema):
    """Create a new flashcard"""
    # TODO: Implement actual database creation
    return {
        "id": 1,
        "knowledge_component_id": payload.knowledge_component_id,
        "front_content": payload.front_content,
        "back_content": payload.back_content,
        "difficulty": payload.difficulty,
        "tags": payload.tags,
        "created_at": datetime.now()
    }

@router.get("/flashcards/{flashcard_id}", response=FlashcardSchema)
def get_flashcard(request, flashcard_id: int):
    """Get a specific flashcard"""
    # TODO: Implement actual database query
    return {
        "id": flashcard_id,
        "knowledge_component_id": 1,
        "front_content": "What is the quadratic formula?",
        "back_content": "x = (-b ± √(b²-4ac)) / 2a",
        "difficulty": 0.7,
        "tags": ["algebra", "quadratic", "formula"],
        "created_at": datetime.now()
    }

# SRS System endpoints
@router.get("/students/{student_id}/due-cards", response=List[StudentCardSchema])
def get_due_cards(request, student_id: int, limit: int = 20):
    """Get cards due for review for a specific student"""
    # TODO: Implement actual SRS algorithm to find due cards
    return [
        {
            "id": 1,
            "student_id": student_id,
            "flashcard_id": 1,
            "status": CardStatus.REVIEW,
            "ease_factor": 2.5,
            "interval": 3,
            "repetitions": 2,
            "next_review": datetime.now() - timedelta(hours=1),  # Due now
            "last_reviewed": datetime.now() - timedelta(days=3)
        }
    ]

@router.post("/students/{student_id}/study-session", response=ReviewSessionSchema)
def start_study_session(request, student_id: int):
    """Start a new study session for a student"""
    # TODO: Implement actual session creation
    due_cards = []  # Get from get_due_cards logic
    
    return {
        "id": 1,
        "student_id": student_id,
        "cards_due": due_cards,
        "session_start": datetime.now(),
        "cards_reviewed": 0
    }

@router.post("/review-card", response=StudentCardSchema)
def submit_card_review(request, payload: SubmitReviewSchema):
    """Submit a review result for a flashcard using SM-2 algorithm"""
    # TODO: Implement actual SM-2 algorithm
    
    # Mock SM-2 calculation
    if payload.result == ReviewResult.EASY:
        new_interval = 7
        new_ease_factor = 2.6
        new_repetitions = 3
    elif payload.result == ReviewResult.GOOD:
        new_interval = 3
        new_ease_factor = 2.5
        new_repetitions = 2
    elif payload.result == ReviewResult.HARD:
        new_interval = 1
        new_ease_factor = 2.3
        new_repetitions = 1
    else:  # AGAIN
        new_interval = 1
        new_ease_factor = 2.0
        new_repetitions = 0
    
    next_review = datetime.now() + timedelta(days=new_interval)
    
    return {
        "id": payload.student_card_id,
        "student_id": 1,  # TODO: Get from actual student card
        "flashcard_id": 1,
        "status": CardStatus.REVIEW,
        "ease_factor": new_ease_factor,
        "interval": new_interval,
        "repetitions": new_repetitions,
        "next_review": next_review,
        "last_reviewed": datetime.now()
    }

@router.get("/students/{student_id}/study-stats", response=StudyStatsSchema)
def get_study_statistics(request, student_id: int):
    """Get study statistics and progress for a student"""
    # TODO: Implement actual statistics calculation
    return {
        "student_id": student_id,
        "total_cards": 45,
        "new_cards": 5,
        "learning_cards": 8,
        "review_cards": 25,
        "graduated_cards": 7,
        "daily_streak": 12,
        "next_review_time": datetime.now() + timedelta(hours=2)
    }

# Advanced SRS features
@router.post("/students/{student_id}/add-cards")
def add_cards_to_student(request, student_id: int, flashcard_ids: List[int]):
    """Add new flashcards to a student's study deck"""
    # TODO: Implement adding cards to student's deck
    added_cards = []
    for card_id in flashcard_ids:
        added_cards.append({
            "student_id": student_id,
            "flashcard_id": card_id,
            "status": CardStatus.NEW,
            "ease_factor": 2.5,
            "interval": 1,
            "repetitions": 0,
            "next_review": datetime.now(),
            "last_reviewed": None
        })
    
    return {
        "message": f"Added {len(flashcard_ids)} cards to student {student_id}",
        "cards_added": added_cards
    }

@router.get("/students/{student_id}/learning-curve")
def get_learning_curve(request, student_id: int, days: int = 30):
    """Get learning curve data for visualization"""
    # TODO: Implement learning curve calculation
    curve_data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        curve_data.append({
            "date": date,
            "cards_reviewed": 5 + i,
            "accuracy_rate": min(0.95, 0.6 + (i * 0.01)),
            "average_ease_factor": 2.3 + (i * 0.005)
        })
    
    return {
        "student_id": student_id,
        "learning_curve": curve_data,
        "trend": "improving",
        "predicted_mastery_date": datetime.now() + timedelta(days=45)
    }

@router.get("/students/{student_id}/difficult-cards", response=List[StudentCardSchema])
def get_difficult_cards(request, student_id: int, limit: int = 10):
    """Get cards that the student finds most difficult"""
    # TODO: Implement difficulty analysis
    return [
        {
            "id": 1,
            "student_id": student_id,
            "flashcard_id": 5,
            "status": CardStatus.LEARNING,
            "ease_factor": 1.8,  # Low ease factor indicates difficulty
            "interval": 1,
            "repetitions": 0,
            "next_review": datetime.now(),
            "last_reviewed": datetime.now() - timedelta(hours=2)
        }
    ]

@router.get("/optimize/{student_id}")
def optimize_study_schedule(request, student_id: int):
    """Get optimized study schedule recommendations"""
    # TODO: Implement optimization algorithm
    return {
        "student_id": student_id,
        "recommended_daily_cards": 15,
        "optimal_study_times": ["09:00", "15:00", "20:00"],
        "focus_areas": ["Quadratic equations", "Linear functions"],
        "estimated_time_per_session": 20,  # minutes
        "weekly_goals": {
            "new_cards": 35,
            "reviews": 150,
            "target_accuracy": 0.85
        }
    }

@router.get("/status")
def practice_status(request):
    """Practice app status endpoint"""
    return {
        "app": "practice", 
        "status": "ready", 
        "description": "Spaced Repetition System (SRS) for flashcard practice",
        "features": [
            "SM-2 Algorithm", 
            "Adaptive Scheduling", 
            "Learning Analytics",
            "Difficulty Optimization",
            "Progress Tracking"
        ],
        "algorithms": ["SM-2", "Custom SRS"]
    }