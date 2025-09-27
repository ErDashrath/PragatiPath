# Enhanced Adaptive Learning Frontend Integration Guide

## 🎯 Overview
Complete integration guide for connecting your frontend with the enhanced adaptive learning system featuring real-time mastery tracking, BKT/DKT orchestration, and comprehensive analytics.

## 🗄️ Database Schema Enhancements

### New Models Added

#### StudentMastery Model
```python
# Foreign key relationships for analytics and reporting
student_session = ForeignKey(StudentSession)  # Links to session
subject = ForeignKey(Subject)                 # Subject mastery tracking
chapter = ForeignKey(Chapter)                 # Chapter mastery tracking

# Core mastery metrics
mastery_score          # 0.0 to 1.0 mastery level
mastery_level          # novice, developing, proficient, advanced, expert
confidence_score       # Confidence in assessment

# BKT specific metrics
bkt_knowledge_probability
bkt_learning_rate
bkt_guess_rate
bkt_slip_rate

# DKT specific metrics
dkt_knowledge_state       # JSON vector
dkt_prediction_confidence

# Analytics fields
questions_attempted
questions_correct
average_response_time
difficulty_progression    # JSON array
```

#### Enhanced StudentSession Fields
```python
# Enhanced mastery tracking
current_mastery_score    # Overall session mastery
mastery_threshold        # Achievement threshold (default 0.8)
mastery_achieved         # Boolean flag
mastery_achieved_at      # Timestamp
session_analytics        # Comprehensive analytics JSON
```

## 🔗 API Endpoints

### Base URL: `/api/v1/adaptive/`

### 1. Get Next Adaptive Question
**POST** `/next-question/`

```javascript
// Request
{
  "session_id": "session_123",
  "user_id": 1,
  "subject_id": 2,
  "chapter_id": 3  // Optional
}

// Response
{
  "success": true,
  "question": {
    "id": 45,
    "question_text": "What is the capital of France?",
    "options": ["Paris", "London", "Berlin", "Madrid"],
    "difficulty": "medium",
    "chapter_name": "Geography Basics"
  },
  "mastery_status": {
    "current_score": 0.65,
    "mastery_achieved": false,
    "mastery_level": "proficient", 
    "confidence": 0.72,
    "questions_remaining": 8
  },
  "session_info": {
    "session_id": "session_123",
    "questions_attempted": 12,
    "current_streak": 3,
    "session_duration": 25.5
  }
}
```

### 2. Submit Answer with Mastery Update
**POST** `/submit-answer/`

```javascript
// Request
{
  "session_id": "session_123",
  "question_id": 45,
  "answer": "Paris",
  "response_time": 15.2  // seconds
}

// Response
{
  "success": true,
  "result": {
    "correct": true,
    "correct_answer": "Paris",
    "explanation": "Paris is the capital and largest city of France.",
    "points_earned": 10
  },
  "mastery_update": {
    "overall_mastery": 0.68,
    "mastery_achieved": false,
    "mastery_level": "proficient",
    "subject_mastery": 0.65,
    "chapter_mastery": 0.70,
    "confidence": 0.74
  },
  "session_stats": {
    "questions_attempted": 13,
    "questions_correct": 10,
    "accuracy": 0.77,
    "current_streak": 4,
    "best_streak": 6
  },
  "next_question_available": true
}
```

### 3. Real-time Mastery Status
**GET** `/mastery/status/?session_id=session_123`

```javascript
// Response
{
  "success": true,
  "mastery_status": {
    "overall_mastery": 0.68,
    "mastery_achieved": false,
    "mastery_threshold": 0.8,
    "mastery_achieved_at": null
  },
  "detailed_analytics": {
    "overall_mastery": 0.68,
    "subject_masteries": [{
      "subject_id": 2,
      "subject_name": "Mathematics",
      "mastery_score": 0.65,
      "mastery_level": "proficient",
      "confidence": 0.72,
      "questions_attempted": 25,
      "accuracy": 0.76
    }],
    "chapter_masteries": [...],
    "learning_progression": [...]
  },
  "performance_trend": [...],
  "session_summary": {
    "duration_minutes": 25.5,
    "questions_attempted": 13,
    "accuracy": 0.77,
    "learning_velocity": 0.51,
    "estimated_time_to_mastery": 16
  }
}
```

### 4. Mastery Dashboard
**GET** `/mastery/dashboard/?user_id=1&subject_id=2&time_range=7`

```javascript
// Comprehensive analytics response
{
  "success": true,
  "dashboard": {
    "student_summary": {
      "student_id": 1,
      "username": "john_student",
      "total_sessions": 15,
      "subjects_studied": 3,
      "average_mastery": 0.72
    },
    "mastery_progression": [...],
    "subject_masteries": {...},
    "chapter_masteries": {...},
    "learning_insights": {...}
  },
  "metadata": {
    "time_range_days": 7,
    "generated_at": "2024-12-28T10:30:00Z",
    "total_mastery_records": 45,
    "subjects_with_mastery": 3
  }
}
```

## 💻 Frontend Implementation

### React/TypeScript Integration

```typescript
// types/adaptive.ts
export interface MasteryStatus {
  current_score: number;
  mastery_achieved: boolean;
  mastery_level: 'novice' | 'developing' | 'proficient' | 'advanced' | 'expert';
  confidence: number;
  questions_remaining: number;
}

export interface AdaptiveQuestion {
  id: number;
  question_text: string;
  options: string[];
  difficulty: string;
  chapter_name?: string;
}

export interface SessionInfo {
  session_id: string;
  questions_attempted: number;
  current_streak: number;
  session_duration: number;
}

// hooks/useAdaptiveLearning.ts
import { useState, useCallback } from 'react';

export const useAdaptiveLearning = (sessionId: string, userId: number, subjectId: number) => {
  const [currentQuestion, setCurrentQuestion] = useState<AdaptiveQuestion | null>(null);
  const [masteryStatus, setMasteryStatus] = useState<MasteryStatus | null>(null);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [loading, setLoading] = useState(false);

  const getNextQuestion = useCallback(async (chapterId?: number) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/adaptive/next-question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: userId,
          subject_id: subjectId,
          chapter_id: chapterId,
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setCurrentQuestion(data.question);
        setMasteryStatus(data.mastery_status);
        setSessionInfo(data.session_info);
      } else {
        console.error('Error getting next question:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    } finally {
      setLoading(false);
    }
  }, [sessionId, userId, subjectId]);

  const submitAnswer = useCallback(async (questionId: number, answer: string, responseTime: number) => {
    try {
      const response = await fetch('/api/v1/adaptive/submit-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          session_id: sessionId,
          question_id: questionId,
          answer: answer,
          response_time: responseTime,
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        // Update mastery status
        setMasteryStatus(prev => ({
          ...prev!,
          current_score: data.mastery_update.overall_mastery,
          mastery_achieved: data.mastery_update.mastery_achieved,
          mastery_level: data.mastery_update.mastery_level,
        }));
        
        // Update session info
        setSessionInfo(prev => ({
          ...prev!,
          questions_attempted: data.session_stats.questions_attempted,
          current_streak: data.session_stats.current_streak,
        }));
        
        return data;
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  }, [sessionId]);

  return {
    currentQuestion,
    masteryStatus,
    sessionInfo,
    loading,
    getNextQuestion,
    submitAnswer,
  };
};

// components/AdaptiveLearningInterface.tsx
import React, { useEffect, useState } from 'react';
import { useAdaptiveLearning } from '../hooks/useAdaptiveLearning';

interface Props {
  sessionId: string;
  userId: number;
  subjectId: number;
  chapterId?: number;
}

export const AdaptiveLearningInterface: React.FC<Props> = ({
  sessionId,
  userId,
  subjectId,
  chapterId,
}) => {
  const {
    currentQuestion,
    masteryStatus,
    sessionInfo,
    loading,
    getNextQuestion,
    submitAnswer,
  } = useAdaptiveLearning(sessionId, userId, subjectId);

  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [startTime, setStartTime] = useState<number>(Date.now());

  useEffect(() => {
    getNextQuestion(chapterId);
  }, [getNextQuestion, chapterId]);

  const handleSubmit = async () => {
    if (currentQuestion && selectedAnswer) {
      const responseTime = (Date.now() - startTime) / 1000;
      await submitAnswer(currentQuestion.id, selectedAnswer, responseTime);
      
      // Get next question after a brief delay
      setTimeout(() => {
        getNextQuestion(chapterId);
        setSelectedAnswer('');
        setStartTime(Date.now());
      }, 2000);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="adaptive-learning-container">
      {/* Mastery Progress Display */}
      <div className="mastery-display">
        <div className="mastery-score">
          Mastery: {Math.round((masteryStatus?.current_score || 0) * 100)}%
        </div>
        <div className="mastery-level">
          Level: {masteryStatus?.mastery_level || 'novice'}
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${(masteryStatus?.current_score || 0) * 100}%` }}
          />
        </div>
        {masteryStatus?.mastery_achieved && (
          <div className="mastery-achieved">🎉 Mastery Achieved!</div>
        )}
      </div>

      {/* Question Display */}
      {currentQuestion && (
        <div className="question-container">
          <h3>{currentQuestion.question_text}</h3>
          <div className="options">
            {currentQuestion.options.map((option, index) => (
              <label key={index}>
                <input
                  type="radio"
                  value={option}
                  checked={selectedAnswer === option}
                  onChange={(e) => setSelectedAnswer(e.target.value)}
                />
                {option}
              </label>
            ))}
          </div>
          <button onClick={handleSubmit} disabled={!selectedAnswer}>
            Submit Answer
          </button>
        </div>
      )}

      {/* Session Stats */}
      <div className="session-stats">
        <div>Questions: {sessionInfo?.questions_attempted || 0}</div>
        <div>Streak: {sessionInfo?.current_streak || 0}</div>
        <div>Duration: {Math.round(sessionInfo?.session_duration || 0)}min</div>
      </div>
    </div>
  );
};
```

### JavaScript (Vanilla) Integration

```javascript
// adaptive-learning.js
class AdaptiveLearningSystem {
  constructor(sessionId, userId, subjectId) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.subjectId = subjectId;
    this.currentQuestion = null;
    this.masteryStatus = null;
    this.startTime = Date.now();
  }

  async getNextQuestion(chapterId = null) {
    try {
      const response = await fetch('/api/v1/adaptive/next-question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          user_id: this.userId,
          subject_id: this.subjectId,
          chapter_id: chapterId,
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        this.currentQuestion = data.question;
        this.masteryStatus = data.mastery_status;
        this.displayQuestion(data.question);
        this.updateMasteryDisplay(data.mastery_status);
        this.updateSessionInfo(data.session_info);
      }
    } catch (error) {
      console.error('Error getting next question:', error);
    }
  }

  async submitAnswer(answer) {
    const responseTime = (Date.now() - this.startTime) / 1000;
    
    try {
      const response = await fetch('/api/v1/adaptive/submit-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          question_id: this.currentQuestion.id,
          answer: answer,
          response_time: responseTime,
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        this.showResult(data.result);
        this.updateMasteryDisplay(data.mastery_update);
        
        // Auto-load next question after delay
        setTimeout(() => {
          this.getNextQuestion();
          this.startTime = Date.now();
        }, 2000);
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  }

  displayQuestion(question) {
    const container = document.getElementById('question-container');
    container.innerHTML = `
      <h3>${question.question_text}</h3>
      <div class="options">
        ${question.options.map((option, index) => `
          <label>
            <input type="radio" name="answer" value="${option}">
            ${option}
          </label>
        `).join('')}
      </div>
      <button onclick="adaptiveSystem.submitSelectedAnswer()">Submit</button>
    `;
  }

  updateMasteryDisplay(masteryStatus) {
    const masteryPercent = Math.round(masteryStatus.current_score * 100);
    document.getElementById('mastery-score').textContent = `${masteryPercent}%`;
    document.getElementById('mastery-level').textContent = masteryStatus.mastery_level;
    document.getElementById('progress-fill').style.width = `${masteryPercent}%`;
    
    if (masteryStatus.mastery_achieved) {
      document.getElementById('mastery-achieved').style.display = 'block';
    }
  }

  submitSelectedAnswer() {
    const selected = document.querySelector('input[name="answer"]:checked');
    if (selected) {
      this.submitAnswer(selected.value);
    }
  }

  getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
}

// Usage
const adaptiveSystem = new AdaptiveLearningSystem('session_123', 1, 2);
adaptiveSystem.getNextQuestion();
```

## 🔧 Setup Instructions

### 1. Database Migration
```bash
# Generate migration
python manage.py makemigrations assessment

# Apply migration
python manage.py migrate

# Verify tables
python manage.py dbshell
.tables  # Should show new StudentMastery table
```

### 2. URL Configuration
```python
# In your main urls.py
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('api/v1/adaptive/', include('api.adaptive_urls')),
]
```

### 3. Settings Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ... existing apps
    'assessment',
    'api',
]

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    # Add your production domains
]

CORS_ALLOW_CREDENTIALS = True
```

## 📊 Analytics and Reporting

### Mastery Analytics Queries
```python
# Get student mastery progression
from assessment.models import StudentMastery, StudentSession

# Subject-wise mastery
subject_mastery = StudentMastery.objects.filter(
    student_session__user_id=user_id,
    subject_id=subject_id
).values('mastery_level').annotate(count=Count('id'))

# Learning velocity analysis
learning_velocity = StudentSession.objects.filter(
    user_id=user_id
).aggregate(
    avg_velocity=Avg('learning_velocity'),
    avg_mastery=Avg('current_mastery_score')
)

# Mastery achievement timeline
mastery_timeline = StudentSession.objects.filter(
    user_id=user_id,
    mastery_achieved=True
).values('subject__name', 'mastery_achieved_at', 'current_mastery_score')
```

## 🎯 Key Features Implemented

✅ **Real-time Mastery Tracking** - Instant updates as students progress  
✅ **BKT/DKT Integration** - Sophisticated knowledge modeling  
✅ **Foreign Key Analytics** - Proper relationships for reporting  
✅ **Session Management** - Complete session lifecycle tracking  
✅ **Performance Analytics** - Comprehensive learning insights  
✅ **Adaptive Orchestration** - Dynamic question difficulty adjustment  
✅ **Mastery Thresholds** - Configurable achievement criteria  
✅ **Progress Visualization** - Real-time progress indicators  

## 🔄 Integration Workflow

1. **Session Start** → Create/retrieve StudentSession
2. **Question Request** → Get adaptive question based on mastery
3. **Answer Submission** → Update mastery records with BKT/DKT
4. **Real-time Updates** → Frontend receives mastery progression
5. **Analytics Capture** → Store comprehensive session analytics
6. **Mastery Achievement** → Track and celebrate milestones

This system provides a complete foundation for adaptive learning with sophisticated mastery tracking that integrates seamlessly with your frontend while maintaining proper database relationships for analytics and reporting.