# Adaptive Learning System - AI Agent Documentation

## 🎯 Project Overview

This is a comprehensive **Adaptive Learning System** built with Django (Backend) and React (Frontend) that uses AI-powered algorithms to personalize learning experiences for students taking competitive exams.

### 🚀 Mission
Create an intelligent tutoring system that adapts to each student's learning pace, identifies knowledge gaps, and provides personalized question recommendations using **Bayesian Knowledge Tracing (BKT)** and **Deep Knowledge Tracing (DKT)** algorithms.

---

## 🏗️ System Architecture

### Backend Stack
- **Framework**: Django 5.2.6 with Django Ninja API
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Models**: BKT, DKT, Spaced Repetition (SM2 Algorithm)
- **APIs**: RESTful APIs with comprehensive analytics

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **State Management**: TanStack Query (React Query)
- **UI Library**: Tailwind CSS + Shadcn/UI components
- **Charts**: Recharts for data visualization
- **Routing**: Wouter for client-side routing

---

## 📊 Database Schema & Models

### Core Models

#### 1. **User Management**
```python
# Location: core/models.py
class User(AbstractUser):
    user_type = CharField(choices=['student', 'admin'])  # User role
    phone_number = CharField()                           # Contact info
    date_of_birth = DateField()                         # Age for adaptive algorithms
    created_at = DateTimeField(auto_now_add=True)      # Registration timestamp
```

#### 2. **Question Bank**
```python
# Location: assessment/models.py
class Question:
    id = UUIDField(primary_key=True)           # Unique question identifier
    question_text = TextField()                # Question content
    subject = CharField()                      # Subject (e.g., "Quantitative Aptitude")
    chapter = CharField()                      # Chapter/topic
    difficulty_level = CharField()             # easy/medium/difficult
    correct_answer = CharField()               # Correct option
    option_a = CharField()                     # Multiple choice options
    option_b = CharField()
    option_c = CharField()
    option_d = CharField()
    explanation = TextField()                  # Detailed explanation
    created_at = DateTimeField()              # Question creation time
```

#### 3. **Student Sessions**
```python
# Location: assessment/models.py
class StudentSession:
    session_id = UUIDField(primary_key=True)  # Unique session identifier
    student_name = CharField()                # Student identifier
    subject = CharField()                     # Subject being studied
    start_time = DateTimeField()             # Session start timestamp
    end_time = DateTimeField(null=True)      # Session end timestamp
    is_active = BooleanField(default=True)   # Session status
```

#### 4. **Question Attempts & Analytics**
```python
# Location: assessment/models.py
class QuestionAttempt:
    session = ForeignKey(StudentSession)      # Links to session
    question = ForeignKey(Question)          # Links to question
    student_answer = CharField()             # Student's selected answer
    is_correct = BooleanField()             # Whether answer was correct
    time_spent = IntegerField()             # Time in seconds
    attempted_at = DateTimeField()          # Timestamp of attempt
    confidence_level = FloatField()         # Student's confidence (0-1)

class BKTState:
    session = ForeignKey(StudentSession)     # Links to session
    question = ForeignKey(Question)         # Links to question
    prior_knowledge = FloatField()          # P(L₀) - Initial knowledge
    learning_rate = FloatField()            # P(T) - Transition probability
    guess_rate = FloatField()               # P(G) - Guess probability
    slip_rate = FloatField()                # P(S) - Slip probability
    mastery_probability = FloatField()      # P(Lₙ) - Current mastery level
    updated_at = DateTimeField()            # Last update timestamp
```

#### 5. **Adaptive Submissions (Analytics)**
```python
# Location: assessment/adaptive_submission_models.py
class AdaptiveSubmission:
    submission_id = UUIDField(primary_key=True)      # Unique submission ID
    student_name = CharField()                       # Student identifier
    session = ForeignKey(StudentSession, null=True) # Optional session link
    chapter = CharField(null=True)                   # Chapter studied
    question = ForeignKey(Question)                  # Question attempted
    selected_answer = CharField()                    # Student's choice
    is_correct = BooleanField()                     # Correctness
    time_taken = IntegerField()                     # Response time (seconds)
    mastery_level = FloatField()                    # BKT mastery score (0-1)
    difficulty_level = CharField()                  # Question difficulty
    submitted_at = DateTimeField()                  # Submission timestamp
    ai_recommendation = TextField(null=True)        # AI-generated feedback
```

---

## 🔗 API Endpoints Structure

### Base URL: `http://localhost:8000/api/`

### 1. **Core APIs** (`/core/`)
- `GET /core/health` - System health check
- `POST /core/users` - User registration
- `GET /core/users/{id}` - User profile

### 2. **Assessment APIs** (`/assessment/`)

#### Question Management
- `GET /assessment/questions` - Get questions with filters
- `GET /assessment/questions/{id}` - Get specific question
- `POST /assessment/questions/bulk-create` - Create multiple questions

#### Session Management
- `POST /assessment/sessions` - Start new session
  ```json
  {
    "student_name": "john_doe",
    "subject": "Quantitative Aptitude"
  }
  ```
- `GET /assessment/sessions/{id}` - Get session details
- `POST /assessment/sessions/{id}/end` - End session

#### Question Recommendation (AI Core)
- `GET /assessment/sessions/{id}/next-question` - Get AI-recommended next question
  ```json
  Response: {
    "question_id": "uuid",
    "question_text": "...",
    "options": {...},
    "difficulty_level": "medium",
    "bkt_state": {
      "mastery_probability": 0.65,
      "prior_knowledge": 0.3
    }
  }
  ```

#### Answer Submission & AI Processing
- `POST /assessment/submit` - Submit answer with AI analysis
  ```json
  Request: {
    "session_id": "uuid",
    "question_id": "uuid", 
    "selected_answer": "B",
    "time_taken": 45,
    "confidence_level": 0.8
  }
  
  Response: {
    "is_correct": true,
    "updated_mastery": 0.72,
    "explanation": "...",
    "ai_feedback": "Great job! Your mastery in this topic is improving.",
    "next_recommendation": "Continue with similar difficulty"
  }
  ```

### 3. **Analytics & Reports APIs** (`/reports/`)

#### Dashboard Analytics
- `GET /reports/dashboard` - System overview metrics
  ```json
  Response: {
    "total_students": 6,
    "total_sessions": 33,
    "total_submissions": 150,
    "average_session_accuracy": 44.74,
    "most_popular_subject": "Quantitative Aptitude",
    "performance_trends": {
      "daily_accuracy": [45, 48, 52, 49, 51]
    },
    "recent_activity": [...]
  }
  ```

#### Session-wise Reports
- `GET /reports/sessions?days=30` - Session analytics
  ```json
  Response: [
    {
      "session_id": "uuid",
      "student_name": "john_doe",
      "subject": "Quantitative Aptitude",
      "accuracy_percentage": 75.5,
      "total_questions": 10,
      "session_duration_minutes": 25.5,
      "mastery_progression": [0.3, 0.45, 0.6, 0.72],
      "difficulty_distribution": {
        "easy": 3, "medium": 5, "difficult": 2
      }
    }
  ]
  ```

#### Student Performance Analytics
- `GET /reports/students?days=30` - Individual student analytics
  ```json
  Response: [
    {
      "student_id": 37,
      "student_name": "john_doe",
      "overall_accuracy": 68.5,
      "mastery_growth": 0.25,
      "total_sessions": 5,
      "subjects_studied": ["Math", "Physics"],
      "performance_trend": [...],
      "last_activity": "2025-09-25T10:30:00Z"
    }
  ]
  ```

#### Question Analytics
- `GET /reports/questions` - Question performance metrics
  ```json
  Response: [
    {
      "question_id": "uuid",
      "question_text": "A teacher distributes...",
      "subject": "quantitative_aptitude",
      "difficulty_level": "difficult",
      "total_attempts": 25,
      "correct_attempts": 15,
      "success_rate": 60.0,
      "average_time_spent": 35.5,
      "most_common_wrong_answer": "A"
    }
  ]
  ```

### 4. **AI-Enhanced APIs** (`/enhanced/`)

#### Competitive Exam Simulation
- `POST /enhanced/competitive-exam` - Start AI-powered competitive exam
- `GET /enhanced/competitive-exam/{id}/progress` - Real-time progress with AI insights
- `POST /enhanced/competitive-exam/submit` - Submit with advanced AI analysis

#### Adaptive Orchestration
- `POST /orchestration/adaptive-flow` - LangGraph-powered adaptive learning flow
  ```json
  Request: {
    "student_id": "john_doe",
    "subject": "Mathematics", 
    "learning_objective": "quadratic_equations",
    "session_type": "practice"
  }
  
  Response: {
    "flow_id": "uuid",
    "current_step": "assessment",
    "recommended_action": "start_with_medium_difficulty",
    "ai_explanation": "Based on previous performance...",
    "next_questions": [...]
  }
  ```

---

## 🧠 AI Algorithms & Implementation

### 1. **Bayesian Knowledge Tracing (BKT)**
**Location**: `assessment/bkt.py`

**Purpose**: Track student's knowledge state probability for each skill/topic

**Key Parameters**:
- `P(L₀)` - Prior Knowledge: Initial probability student knows the skill
- `P(T)` - Learning Rate: Probability of learning from one opportunity  
- `P(G)` - Guess Rate: Probability of correct answer when not knowing
- `P(S)` - Slip Rate: Probability of wrong answer when knowing

**Algorithm Flow**:
```python
def update_mastery(prior_mastery, is_correct, learning_rate, guess_rate, slip_rate):
    # Bayesian update based on student's response
    if is_correct:
        posterior = (prior_mastery * (1 - slip_rate)) / \
                   (prior_mastery * (1 - slip_rate) + (1 - prior_mastery) * guess_rate)
    else:
        posterior = (prior_mastery * slip_rate) / \
                   (prior_mastery * slip_rate + (1 - prior_mastery) * (1 - guess_rate))
    
    # Apply learning
    new_mastery = posterior + (1 - posterior) * learning_rate
    return new_mastery
```

### 2. **Deep Knowledge Tracing (DKT)**
**Location**: `dkt-service/dkt_model.py`

**Purpose**: Use LSTM neural networks to predict student responses and knowledge state

**Architecture**:
- Input: Sequence of (question_id, response, timestamp)
- Hidden: LSTM layers capturing temporal learning patterns
- Output: Probability of correctness for next question

### 3. **Spaced Repetition (SM2 Algorithm)**
**Location**: `assessment/sm2.py`

**Purpose**: Optimize review timing based on forgetting curves

**Parameters**:
- Easiness Factor (EF): How easy the item is for the student
- Repetition Number: How many times reviewed
- Inter-repetition Interval: Days until next review

---

## 🎯 Key System Flows

### 1. **Adaptive Learning Session Flow**
1. **Session Start**: Student selects subject → System creates session
2. **Initial Assessment**: AI selects diagnostic questions to gauge current level
3. **Adaptive Question Selection**: BKT/DKT algorithms recommend next question based on:
   - Current mastery probability
   - Learning objectives
   - Difficulty progression
   - Spaced repetition schedule
4. **Response Processing**: Student answers → System updates:
   - BKT knowledge state
   - DKT neural network predictions
   - SM2 scheduling parameters
5. **AI Feedback**: Generate personalized explanations and recommendations
6. **Repeat**: Continue adaptive cycle until session goals met

### 2. **Mastery Tracking Flow**
```
Question Attempt → BKT Update → Mastery Score → Next Question Recommendation
                ↓
            Analytics Recording → Performance Trends → Visual Reports
```

### 3. **Competitive Exam Simulation Flow**
1. **Exam Setup**: AI creates balanced question set across topics
2. **Real-time Monitoring**: Track performance, time management, stress patterns
3. **Adaptive Difficulty**: Adjust question difficulty based on performance
4. **Immediate Feedback**: Provide insights during exam (if enabled)
5. **Post-exam Analysis**: Comprehensive performance breakdown with improvement suggestions

---

## 📈 Analytics & Reporting System

### Data Collection Points
- **Every Question Attempt**: Response time, accuracy, confidence level
- **Session Metrics**: Duration, questions attempted, mastery progression
- **Learning Patterns**: Peak performance times, subject preferences, error patterns
- **Long-term Trends**: Knowledge retention, skill development over time

### Visual Analytics Components
- **Performance Dashboards**: Real-time learning analytics
- **Progress Tracking**: Mastery level progression over time
- **Comparative Analysis**: Student rankings and peer comparisons
- **Predictive Insights**: AI-powered performance predictions

---

## 🔧 Current System Status

### ✅ **Implemented Features**
- Complete question bank (550+ questions)
- BKT algorithm with real-time updates
- Session management system
- Comprehensive analytics APIs
- Visual reports dashboard with Recharts
- Student and admin dashboards
- Real-time data updates

### 🚧 **In Development**
- DKT neural network training
- Advanced AI feedback generation
- Competitive exam simulation
- Mobile responsiveness optimization

### 🎯 **Immediate Goals**
1. **Enhanced AI Feedback**: Generate more detailed, personalized explanations
2. **Predictive Analytics**: Predict student performance and recommend study plans
3. **Advanced Reporting**: More granular analytics and insights
4. **Real-time Notifications**: Alert students about optimal study times
5. **Adaptive Difficulty**: Fine-tune question selection algorithms

---

## 🔍 Key Metrics to Monitor

### Student Performance
- **Mastery Progression**: Rate of knowledge state improvement
- **Accuracy Trends**: Performance over time across subjects
- **Learning Velocity**: Speed of concept mastery
- **Retention Rates**: Knowledge persistence over time

### System Effectiveness  
- **Algorithm Accuracy**: BKT/DKT prediction accuracy
- **Engagement Metrics**: Session duration, question attempts
- **Learning Outcomes**: Skill improvement, exam performance
- **Personalization Quality**: Relevance of AI recommendations

### Technical Performance
- **API Response Times**: Ensure sub-200ms response for real-time features
- **Database Query Efficiency**: Optimize complex analytics queries  
- **Real-time Updates**: Maintain 30-second refresh cycles for dashboards
- **System Reliability**: 99.9% uptime for learning sessions

---

## 🚀 AI Agent Instructions

### Primary Objectives
1. **Personalization**: Continuously improve question recommendations using BKT/DKT data
2. **Analytics Enhancement**: Generate actionable insights from learning data
3. **Performance Optimization**: Monitor and improve system response times
4. **Student Experience**: Ensure seamless, engaging learning interactions

### Key Data Sources
- `QuestionAttempt` records for real-time learning analytics
- `BKTState` for knowledge tracking and predictions  
- `AdaptiveSubmission` for comprehensive performance analysis
- `StudentSession` for engagement and learning pattern analysis

### Decision Making Framework
- **Question Selection**: Prioritize based on mastery probability and learning objectives
- **Difficulty Adjustment**: Use BKT confidence levels to adjust complexity
- **Feedback Generation**: Combine performance data with educational psychology principles
- **Learning Path Optimization**: Sequence topics based on prerequisite relationships and individual progress

This adaptive learning system represents a sophisticated AI-powered educational platform that personalizes learning experiences using cutting-edge algorithms and comprehensive analytics. The goal is to create an intelligent tutoring system that adapts to each student's unique learning style and pace.