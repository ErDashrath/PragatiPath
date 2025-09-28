# PragatiPath API Endpoints Documentation

## Overview
This document provides comprehensive information about all working API endpoints in the PragatiPath adaptive learning system. The system consists of a Django backend (port 8000) and an Express.js frontend server (port 5000) that proxies certain requests.

## Base URLs
- **Django Backend**: `http://localhost:8000`
- **Frontend Server**: `http://localhost:5000`
- **Frontend Client**: Accessible through port 5000 with proxy

---

## 🔐 Authentication Endpoints

### POST `/api/login`
**Description**: User login  
**Server**: Express (port 5000)  
**Method**: POST  
**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "id": "string",
  "username": "string", 
  "userType": "student|admin",
  "name": "string"
}
```

### POST `/api/logout`
**Description**: User logout  
**Server**: Express (port 5000)  
**Method**: POST  
**Response**:
```json
{
  "message": "Logged out successfully"
}
```

### GET `/api/user`
**Description**: Get current user session (Proxied to Django)  
**Server**: Django (via Express proxy)  
**Method**: GET  
**Response**:
```json
{
  "id": "string",
  "username": "string",
  "userType": "string",
  "name": "string"
}
```

---

## 👨‍🎓 Student Management Endpoints

### GET `/api/student-profile/:userId`
**Description**: Get student profile by user ID  
**Server**: Express (port 5000)  
**Method**: GET  
**Response**:
```json
{
  "id": "string",
  "userId": "string",
  "name": "string",
  "email": "string",
  "fundamentals": {
    "listening": "number",
    "grasping": "number", 
    "retention": "number",
    "application": "number"
  }
}
```

### POST `/api/student-profile`
**Description**: Create new student profile  
**Server**: Express (port 5000)  
**Method**: POST  
**Request Body**:
```json
{
  "userId": "string",
  "name": "string",
  "email": "string"
}
```

### PUT `/api/student-profile/:userId`
**Description**: Update student profile  
**Server**: Express (port 5000)  
**Method**: PUT  
**Request Body**: Partial student profile data

---

## 📚 Module & Chapter Endpoints

### GET `/api/modules`
**Description**: Get all modules/subjects with chapters  
**Server**: Express with Django fallback  
**Method**: GET  
**Response**:
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string", 
    "icon": "string",
    "color": "string",
    "chapters": [
      {
        "id": "number",
        "title": "string",
        "status": "completed|in-progress|locked",
        "progress": "number"
      }
    ]
  }
]
```

### GET `/api/modules/:moduleId`
**Description**: Get specific module details  
**Server**: Express (port 5000)  
**Method**: GET

---

## 📝 Assessment Endpoints

### GET `/api/assessment/questions/:moduleId/:chapterId`
**Description**: Get assessment questions for specific module and chapter  
**Server**: Express with Django backend integration  
**Method**: GET  
**Query Parameters**:
- `difficulty`: "easy|moderate|difficult" (default: "moderate")
- `count`: number (default: 15)

**Response**:
```json
[
  {
    "id": "string",
    "moduleId": "string",
    "chapterId": "number",
    "questionText": "string",
    "options": ["string"],
    "difficulty": "number",
    "fundamentalType": "string",
    "questionType": "string"
  }
]
```

### POST `/api/assessment/session`
**Description**: Create new assessment session  
**Server**: Express (port 5000)  
**Method**: POST  
**Request Body**:
```json
{
  "userId": "string",
  "moduleId": "string", 
  "chapterId": "number",
  "questions": "array",
  "startTime": "datetime"
}
```

### PUT `/api/assessment/session/:sessionId`
**Description**: Update assessment session  
**Server**: Express (port 5000)  
**Method**: PUT  
**Request Body**: Partial session data

---

## 🎯 Django Core API Endpoints (Proxied)

### GET `/api/core/user`
**Description**: Get authenticated user details  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: GET

### POST `/api/core/*`
**Description**: Various core Django endpoints  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: Multiple

---

## 📊 Admin Dashboard Endpoints

### GET `/api/admin/class-overview`
**Description**: Get comprehensive class overview statistics  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: GET  
**Response**:
```json
{
  "totalStudents": "number",
  "activeThisWeek": "number", 
  "totalSessions": "number",
  "completedSessions": "number",
  "averageAccuracy": "number",
  "recentActivity": "number",
  "total_students": "number",
  "active_students": "number",
  "average_progress": "number",
  "completion_rate": "number", 
  "weekly_study_time": "number",
  "needingAttention": "number",
  "gapDistribution": {
    "listening": "number",
    "grasping": "number",
    "retention": "number", 
    "application": "number"
  },
  "lastUpdated": "datetime"
}
```

### GET `/api/admin/students`
**Description**: Get all student profiles with performance data  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: GET  
**Response**:
```json
[
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "created_at": "datetime",
    "last_active": "datetime",
    "total_sessions": "number",
    "completed_sessions": "number", 
    "accuracy": "number",
    "is_active": "boolean",
    "listening_score": "number",
    "grasping_score": "number",
    "retention_score": "number",
    "application_score": "number",
    "overall_progress": "number",
    "priority_score": "number"
  }
]
```

### GET `/api/admin/student-performance/:studentId`
**Description**: Get detailed performance data for specific student  
**Server**: Django (port 8000)  
**Method**: GET  
**Response**:
```json
{
  "student_id": "string",
  "username": "string",
  "full_name": "string",
  "total_sessions": "number",
  "total_questions": "number", 
  "total_correct": "number",
  "overall_accuracy": "number",
  "recent_sessions": [
    {
      "session_id": "string",
      "session_name": "string",
      "subject": "string",
      "created_at": "datetime",
      "status": "string",
      "total_questions": "number",
      "correct_answers": "number", 
      "accuracy": "number",
      "duration_minutes": "number"
    }
  ]
}
```

### GET `/api/admin/system-stats`
**Description**: Get comprehensive system statistics  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: GET  
**Response**:
```json
{
  "users": {
    "total": "number",
    "students": "number", 
    "active_week": "number"
  },
  "sessions": {
    "total": "number",
    "today": "number",
    "week": "number",
    "month": "number"
  },
  "questions": {
    "total": "number",
    "today": "number"
  },
  "subjects": [
    {
      "name": "string",
      "sessions": "number",
      "questions_attempted": "number",
      "accuracy": "number"
    }
  ],
  "last_updated": "datetime"
}
```

---

## 🔄 Simple API Endpoints (Proxied)

### GET `/simple/*`
**Description**: Simple API endpoints  
**Server**: Django (port 8000) - Proxied via Express  
**Method**: Multiple

---

## 🧪 Testing Endpoints

### GET `/auth-test`
**Description**: Authentication testing page  
**Server**: Express (port 5000)  
**Method**: GET  
**Response**: HTML test page

---

## 📊 Backend-Only Django Endpoints

### GET `/api/assessment/subjects-with-chapters`
**Description**: Get subjects with their chapters  
**Server**: Django (port 8000)  
**Method**: GET  
**Response**:
```json
{
  "success": "boolean",
  "subjects": [
    {
      "subject_code": "string",
      "subject_name": "string", 
      "chapters": [
        {
          "id": "number",
          "name": "string"
        }
      ]
    }
  ]
}
```

### POST `/api/assessment/chapter-questions`
**Description**: Get chapter-specific questions  
**Server**: Django (port 8000)  
**Method**: POST  
**Request Body**:
```json
{
  "student_id": "string",
  "subject": "string",
  "chapter_id": "number",
  "difficulty_level": "string",
  "count": "number"
}
```

---

## 🔧 Configuration & Status

### Proxy Configuration
The Express server (port 5000) automatically proxies these request patterns to Django (port 8000):
- `/api/core/*`
- `/simple/*` 
- `/api/user`
- `/api/admin/*`

### Authentication
- Express server handles basic login/logout with in-memory session
- Django handles core user management and session authentication
- Admin endpoints require proper authentication

### CORS Configuration
- Django backend allows requests from `http://localhost:5000`
- All origins allowed in development: `CORS_ALLOW_ALL_ORIGINS = True`

---

## 📈 Data Flow

1. **Frontend Client** (React) → **Express Server** (port 5000)
2. **Express Server** → **Django Backend** (port 8000) for proxied endpoints
3. **Express Server** → **Local Storage/Database** for non-proxied endpoints

## 🚀 Usage Examples

### Get Class Overview (Admin)
```javascript
fetch('/api/admin/class-overview')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Login User
```javascript
fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
})
.then(response => response.json());
```

### Get Assessment Questions
```javascript
fetch('/api/assessment/questions/quantitative_aptitude/1?difficulty=moderate&count=15')
  .then(response => response.json())
  .then(questions => console.log(questions));
```

---

## 🔍 Testing Commands

### Test Django Backend Directly
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/admin/students" -Method GET
```

### Test Through Frontend Proxy
```powershell  
Invoke-WebRequest -Uri "http://localhost:5000/api/admin/students" -Method GET
```

### Test Express Endpoints
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/modules" -Method GET
```

---

*Last updated: September 28, 2025*  
*System Status: ✅ All endpoints operational*