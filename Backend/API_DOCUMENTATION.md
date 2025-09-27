# 🚀 Production-Ready Adaptive Learning API Documentation

## Overview

This API provides **clean JSON-only endpoints** for frontend integration with the adaptive learning system. All responses are in pure JSON format with proper CORS headers and industry-standard HTTP status codes.

**Base URL:** `http://localhost:8000/api/v1/`
**Content-Type:** `application/json`
**CORS:** Enabled for all origins

---

## 🔐 Authentication Endpoints

### Register Student
```http
POST /api/v1/auth/register/
```

**Request Body:**
```json
{
    "username": "student123",
    "password": "securepass123",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Registration successful",
    "data": {
        "user_id": 1,
        "username": "student123",
        "full_name": "John Doe",
        "email": "student@example.com"
    },
    "timestamp": "2024-12-26T10:30:00Z"
}
```

**Error Response (409):**
```json
{
    "success": false,
    "error": {
        "code": "USERNAME_EXISTS",
        "message": "Username already exists"
    },
    "timestamp": "2024-12-26T10:30:00Z"
}
```

### Login Student
```http
POST /api/v1/auth/login/
```

**Request Body:**
```json
{
    "username": "student123",
    "password": "securepass123"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": 1,
        "username": "student123",
        "full_name": "John Doe",
        "email": "student@example.com",
        "token": "auth_token_here"
    }
}
```

---

## 📚 Content Management Endpoints

### Get Available Subjects
```http
GET /api/v1/content/subjects/
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Subjects retrieved successfully",
    "data": {
        "subjects": [
            {
                "code": "quantitative_aptitude",
                "name": "Quantitative Aptitude",
                "description": "Mathematical and numerical ability",
                "total_questions": 152,
                "chapters": [
                    {
                        "id": 1,
                        "name": "Percentages",
                        "chapter_number": 1,
                        "description": "Percentage calculations",
                        "question_count": 50
                    }
                ]
            }
        ],
        "total_subjects": 4,
        "total_questions": 552
    }
}
```

---

## 🎯 Adaptive Learning Session Endpoints

### Start Adaptive Session
```http
POST /api/v1/adaptive/session/start/
```

**Request Body:**
```json
{
    "student_id": 1,
    "subject_code": "quantitative_aptitude",
    "chapter_id": 1,
    "max_questions": 15
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Adaptive session started successfully",
    "data": {
        "session_id": "uuid-here",
        "subject_name": "Quantitative Aptitude",
        "chapter_name": "Percentages",
        "initial_mastery": 0.450,
        "mastery_level": "proficient",
        "starting_difficulty": "moderate",
        "max_questions": 15
    }
}
```

### Get Next Question
```http
GET /api/v1/adaptive/session/{session_id}/question/
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Question retrieved successfully",
    "data": {
        "question": {
            "id": "question-uuid",
            "text": "If 25% of a number is 120, what is 40% of the same number?",
            "options": [
                "192",
                "200", 
                "180",
                "160"
            ],
            "difficulty": "moderate",
            "topic": "Percentages",
            "chapter": "Percentages"
        },
        "session_progress": {
            "questions_attempted": 5,
            "max_questions": 15,
            "current_mastery": 0.678,
            "mastery_level": "proficient",
            "current_difficulty": "moderate"
        }
    }
}
```

**Session Complete Response (200):**
```json
{
    "success": true,
    "message": "Session completed successfully", 
    "data": {
        "session_complete": true,
        "final_stats": {
            "total_questions": 15,
            "accuracy": 73.3,
            "final_mastery": 0.782,
            "mastery_level": "advanced"
        }
    }
}
```

### Submit Answer
```http
POST /api/v1/adaptive/session/submit-answer/
```

**Request Body:**
```json
{
    "session_id": "session-uuid",
    "question_id": "question-uuid",
    "student_answer": "a",
    "response_time": 23.5
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Answer submitted successfully",
    "data": {
        "result": {
            "is_correct": true,
            "correct_answer": "a",
            "explanation": "To find 40% of the number: (120 ÷ 25%) × 40% = 480 × 0.4 = 192"
        },
        "mastery_update": {
            "new_mastery": 0.723,
            "mastery_change": 0.078,
            "mastery_level": "advanced",
            "level_description": "Advanced"
        },
        "difficulty_update": {
            "next_difficulty": "difficult",
            "difficulty_changed": true,
            "consecutive_correct": 2,
            "consecutive_incorrect": 0
        },
        "performance_insights": {
            "trend": "strong_performance",
            "questions_attempted": 6,
            "bkt_progression": {
                "P_L": 0.723,
                "skill_growth": 0.078
            }
        }
    }
}
```

### Get Session Analytics
```http
GET /api/v1/adaptive/session/{session_id}/analytics/
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Session analytics retrieved successfully",
    "data": {
        "session_summary": {
            "session_id": "session-uuid",
            "student_id": 1,
            "subject_code": "quantitative_aptitude",
            "total_questions": 12,
            "questions_correct": 9,
            "questions_incorrect": 3,
            "accuracy_percentage": 75.0,
            "session_complete": true
        },
        "mastery_analysis": {
            "initial_mastery": 0.350,
            "final_mastery": 0.720,
            "improvement": 0.370,
            "initial_level": "developing",
            "final_level": "advanced",
            "progression_chart": [0.35, 0.42, 0.58, 0.63, 0.70, 0.72]
        },
        "difficulty_analysis": {
            "progression_history": ["easy", "easy", "moderate", "moderate", "difficult"],
            "difficulty_stats": {
                "starting_difficulty": "easy",
                "ending_difficulty": "difficult", 
                "highest_difficulty_reached": "difficult",
                "progression_changes": 3,
                "difficulty_counts": {
                    "easy": 2,
                    "moderate": 3,
                    "difficult": 7
                }
            }
        },
        "performance_history": [
            {
                "question_number": 1,
                "is_correct": true,
                "mastery": 0.42,
                "difficulty": "easy"
            }
        ],
        "personalized_recommendations": [
            "Strong understanding demonstrated. Practice more difficult questions.",
            "Focus on speed and accuracy with challenging problems."
        ],
        "session_duration": {
            "total_seconds": 920,
            "total_minutes": 15.3,
            "average_time_per_question": 76.7
        }
    }
}
```

---

## 👤 Student Dashboard Endpoints

### Get Student Dashboard
```http
GET /api/v1/students/{student_id}/dashboard/
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Student dashboard retrieved successfully",
    "data": {
        "student_info": {
            "student_id": 1,
            "username": "john_doe",
            "full_name": "John Doe",
            "email": "john@example.com"
        },
        "overall_statistics": {
            "overall_mastery": 0.678,
            "skills_tracked": 5,
            "mastery_level_distribution": {
                "expert": 1,
                "advanced": 2, 
                "proficient": 1,
                "developing": 1
            },
            "total_sessions": 12
        },
        "recent_sessions": [
            {
                "session_id": "session-uuid",
                "subject_code": "quantitative_aptitude",
                "subject_name": "Quantitative Aptitude", 
                "chapter": "Percentages",
                "date": "2024-12-26T10:30:00Z",
                "questions_attempted": 12,
                "accuracy": 75.0,
                "duration_minutes": 15.3
            }
        ],
        "mastery_by_skill": {
            "quantitative_aptitude_chapter_1": {
                "mastery_score": 0.745,
                "mastery_level": "advanced",
                "last_updated": "2024-12-26T10:30:00Z",
                "questions_attempted": 45,
                "session_id": "session-uuid"
            }
        }
    }
}
```

---

## 🔍 System Health Endpoint

### Health Check
```http
GET /api/v1/health/
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "API is healthy",
    "data": {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-12-26T10:30:00Z",
        "components": {
            "database": "connected",
            "adaptive_engine": "operational",
            "bkt_service": "operational",
            "dkt_service": "operational"
        },
        "features": [
            "adaptive_learning",
            "bkt_integration",
            "dkt_integration", 
            "difficulty_progression",
            "mastery_tracking",
            "session_analytics"
        ]
    }
}
```

---

## 🚨 Error Response Format

All errors follow this consistent format:

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message"
    },
    "timestamp": "2024-12-26T10:30:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `AUTHENTICATION_FAILED` | 401 | Invalid credentials |
| `ACCOUNT_DISABLED` | 403 | User account disabled |
| `STUDENT_NOT_FOUND` | 404 | Student does not exist |
| `USERNAME_EXISTS` | 409 | Username already taken |
| `EMAIL_EXISTS` | 409 | Email already registered |
| `SERVER_ERROR` | 500 | Internal server error |

---

## 🌐 Frontend Integration Examples

### React/TypeScript

```typescript
interface ApiResponse<T> {
    success: boolean;
    message?: string;
    data?: T;
    error?: {
        code: string;
        message: string;
    };
}

const api = {
    baseUrl: 'http://localhost:8000/api/v1',
    
    async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    
    async get<T>(endpoint: string): Promise<ApiResponse<T>> {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        return response.json();
    }
};

// Usage
const startSession = async () => {
    const result = await api.post('/adaptive/session/start/', {
        student_id: 1,
        subject_code: 'quantitative_aptitude',
        max_questions: 15
    });
    
    if (result.success) {
        console.log('Session started:', result.data.session_id);
    } else {
        console.error('Error:', result.error?.message);
    }
};
```

### JavaScript/Fetch

```javascript
class AdaptiveLearningAPI {
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
    }
    
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        return response.json();
    }
    
    async startSession(studentId, subjectCode, maxQuestions = 15) {
        return this.request('POST', '/adaptive/session/start/', {
            student_id: studentId,
            subject_code: subjectCode,
            max_questions: maxQuestions
        });
    }
    
    async getNextQuestion(sessionId) {
        return this.request('GET', `/adaptive/session/${sessionId}/question/`);
    }
    
    async submitAnswer(sessionId, questionId, answer, responseTime) {
        return this.request('POST', '/adaptive/session/submit-answer/', {
            session_id: sessionId,
            question_id: questionId,
            student_answer: answer,
            response_time: responseTime
        });
    }
}

// Usage
const api = new AdaptiveLearningAPI();

api.startSession(1, 'quantitative_aptitude')
   .then(result => {
       if (result.success) {
           console.log('Session started:', result.data);
       }
   });
```

---

## ✅ Production Features

- ✅ **Pure JSON Responses** - No HTML/doctype content
- ✅ **CORS Enabled** - Ready for frontend integration
- ✅ **Proper HTTP Status Codes** - Industry standard codes
- ✅ **Comprehensive Error Handling** - Consistent error format
- ✅ **Request Validation** - Input sanitization and validation
- ✅ **Database Transactions** - Data consistency guaranteed
- ✅ **BKT/DKT Integration** - Advanced knowledge tracking
- ✅ **Dynamic Difficulty** - Real-time difficulty adjustment
- ✅ **Mastery Tracking** - Industry-standard mastery levels
- ✅ **Session Analytics** - Comprehensive progress tracking
- ✅ **Performance Insights** - Personalized recommendations

## 🚀 Ready for Production!

Your adaptive learning API is now production-ready with clean JSON endpoints, proper error handling, and comprehensive features for frontend integration!