"""
User Session Management Schemas for Django Ninja API
Handles user sessions, question history, and progress tracking
"""
from ninja import Schema
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums for choices
class SessionType(str, Enum):
    PRACTICE = "PRACTICE"
    MOCK_TEST = "MOCK_TEST"
    CHAPTER_TEST = "CHAPTER_TEST"
    FULL_TEST = "FULL_TEST"

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class AnswerStatus(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"

class DifficultyLevel(str, Enum):
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"

class Subject(str, Enum):
    QUANTITATIVE_APTITUDE = "quantitative_aptitude"
    LOGICAL_REASONING = "logical_reasoning"
    DATA_INTERPRETATION = "data_interpretation"
    VERBAL_ABILITY = "verbal_ability"

# Input Schemas (for creating/updating)
class CreateSessionSchema(Schema):
    """Schema for creating a new user session"""
    user_id: int
    session_type: SessionType
    subject: Subject
    chapter_number: Optional[int] = None

class SubmitAnswerSchema(Schema):
    """Schema for submitting an answer to a question"""
    session_id: str
    question_id: str
    user_answer: str
    confidence_level: Optional[int] = None
    hints_requested: Optional[int] = 0
    explanation_viewed: Optional[bool] = False
    time_spent_seconds: Optional[float] = None

class UpdateSessionSchema(Schema):
    """Schema for updating session status"""
    status: Optional[SessionStatus] = None
    current_question_index: Optional[int] = None
    current_score: Optional[float] = None
    current_difficulty_level: Optional[DifficultyLevel] = None

# Output Schemas (for API responses)
class UserSessionResponse(Schema):
    """Response schema for user sessions"""
    id: str
    user_id: int
    username: str
    session_type: SessionType
    subject: Subject
    chapter_number: Optional[int]
    status: SessionStatus
    current_question_index: int
    session_start_time: datetime
    session_end_time: Optional[datetime]
    total_duration_seconds: int
    questions_attempted: int
    questions_correct: int
    current_score: float
    accuracy_percentage: float
    average_time_per_question: float
    current_difficulty_level: DifficultyLevel
    is_active: bool
    created_at: datetime
    updated_at: datetime

class QuestionHistoryResponse(Schema):
    """Response schema for question history"""
    id: str
    user_id: int
    username: str
    session_id: str
    session_type: SessionType
    question_id: str
    question_text: str
    question_subject: Subject
    user_answer: str
    correct_answer: str
    answer_status: AnswerStatus
    is_correct: bool
    question_start_time: datetime
    question_end_time: Optional[datetime]
    time_spent_seconds: float
    question_order_in_session: int
    difficulty_when_presented: DifficultyLevel
    hints_requested: int
    explanation_viewed: bool
    confidence_level: Optional[int]
    attempt_number: int
    created_at: datetime

class SubjectProgressResponse(Schema):
    """Response schema for subject progress"""
    id: str
    user_id: int
    username: str
    subject: Subject
    total_questions_attempted: int
    total_questions_correct: int
    overall_accuracy_percentage: float
    current_mastery_level: DifficultyLevel
    total_study_time_seconds: int
    average_time_per_question: float
    total_sessions: int
    average_session_duration_minutes: float
    current_correct_streak: int
    longest_correct_streak: int
    current_study_streak_days: int
    longest_study_streak_days: int
    chapter_progress: Dict[str, Any]
    topic_mastery_scores: Dict[str, float]
    last_session_date: Optional[datetime]
    last_question_answered: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class DailyStatsResponse(Schema):
    """Response schema for daily statistics"""
    id: str
    user_id: int
    username: str
    date: datetime
    total_study_time_seconds: int
    study_time_hours: float
    questions_attempted: int
    questions_correct: int
    accuracy_percentage: float
    sessions_completed: int
    subject_time_distribution: Dict[str, int]
    subject_question_counts: Dict[str, int]
    new_topics_attempted: int
    difficulty_levels_unlocked: List[str]
    personal_bests: List[str]
    created_at: datetime
    updated_at: datetime

class UserDashboardResponse(Schema):
    """Combined dashboard response schema"""
    user_info: Dict[str, Any]
    active_sessions: List[UserSessionResponse]
    subject_progress: List[SubjectProgressResponse]
    recent_activity: List[QuestionHistoryResponse]
    daily_stats: Optional[DailyStatsResponse]
    overall_stats: Dict[str, Any]

class SessionStatsResponse(Schema):
    """Session statistics response"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    total_questions_answered: int
    average_accuracy: float
    total_study_time_hours: float
    subjects_studied: List[str]

class NextQuestionResponse(Schema):
    """Response for getting next question in session"""
    question_id: str
    question_text: str
    options: Dict[str, str]
    difficulty_level: DifficultyLevel
    subject: Subject
    chapter_name: Optional[str]
    question_order: int
    session_progress: Dict[str, Any]

# API Response wrapper schemas
class SessionCreateResponse(Schema):
    """Response after creating a session"""
    success: bool
    message: str
    session: UserSessionResponse
    next_question: Optional[NextQuestionResponse] = None

class AnswerSubmissionResponse(Schema):
    """Response after submitting an answer"""
    success: bool
    message: str
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    session_updated: UserSessionResponse
    next_question: Optional[NextQuestionResponse] = None
    mastery_update: Optional[Dict[str, float]] = None

class ErrorResponse(Schema):
    """Standard error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Query parameter schemas
class SessionListFilters(Schema):
    """Filters for listing sessions"""
    user_id: Optional[int] = None
    subject: Optional[Subject] = None
    session_type: Optional[SessionType] = None
    status: Optional[SessionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class QuestionHistoryFilters(Schema):
    """Filters for question history"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    subject: Optional[Subject] = None
    answer_status: Optional[AnswerStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0