# PragatiPath - AI-Powered Adaptive Learning System

## Architecture Overview

This is a **multi-algorithm adaptive learning platform** combining 4 learning algorithms: **BKT** (Bayesian Knowledge Tracing), **DKT** (Deep Knowledge Tracing), **IRT** (Item Response Theory), and **SM-2** (Spaced Repetition). The system uses **Django + Django Ninja** for APIs with a separate **FastAPI DKT microservice**.

### System Structure
```
Backend/ (Django + Django Ninja APIs)
├── adaptive_learning/          # Main Django project
├── core/                      # Student profiles with JSON algorithm state
├── assessment/                # Questions, exams, sessions  
├── student_model/             # BKT/DKT algorithm implementations
├── dkt-service/              # FastAPI microservice (port 8001)
├── orchestration/            # LangGraph + Gemini AI integration
└── frontend_api.py           # React-optimized endpoints

frontend/client/src/ (React + TypeScript + Vite)
├── pages/                    # Main dashboard pages
├── components/               # Reusable UI components
└── lib/                     # API clients and utilities
```

## Critical Data Models & JSON State Management

### StudentProfile (`core/models.py`)
**Core insight**: Algorithm state is stored in JSON fields, not separate tables.
```python
class StudentProfile(models.Model):
    # JSON fields store algorithm state - MUST save after updating!
    bkt_parameters = JSONField(default=dict)  # {"skill_id": {"P_L0": 0.1, "P_T": 0.3, "P_G": 0.2, "P_S": 0.1, "P_L": 0.4}}
    dkt_hidden_state = JSONField(default=list)  # [0.1, 0.2, 0.3, ...] Neural network state
    fundamentals = JSONField(default=dict)  # {"listening": 0.8, "grasping": 0.7}
    current_level = JSONField(default=dict)  # {"algebra": 2, "geometry": 1} Per-skill progression
```

### EnhancedExam System (`assessment/models.py`)
**Key pattern**: Exams have lifecycle management with automatic status transitions.
```python
# Status flow: DRAFT → SCHEDULED → ACTIVE → COMPLETED
class EnhancedExam(models.Model):
    status = models.CharField(choices=EXAM_STATUS, default='DRAFT')
    scheduled_start_time = models.DateTimeField(null=True, blank=True)  
    scheduled_end_time = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_active(self):
        # Critical: Check both status AND time window
        return self.status == 'ACTIVE' and self.scheduled_start_time <= now <= self.scheduled_end_time
```

### AdaptiveQuestion Format (`assessment/models.py`)
**Important**: Uses CSV-compatible format with specific field mapping:
```python
# CSV import format: answer field uses 'a'/'b'/'c'/'d', NOT 'A'/'B'/'C'/'D'
answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, default='a')
difficulty_level = models.CharField(choices=['very_easy', 'easy', 'moderate', 'difficult'])
subject = models.CharField(choices=SUBJECT_CHOICES)  # quantitative_aptitude, logical_reasoning, etc.
```

## Development Workflows

### Running the Complete System
```bash
# Backend (Terminal 1) - Django on port 8000
cd Backend
python manage.py runserver

# DKT Microservice (Terminal 2) - FastAPI on port 8001  
cd Backend/dkt-service
python main.py
# OR: start_dkt_service.bat (Windows)

# Frontend (Terminal 3) - Vite on port 5173
cd frontend
npm run dev
```

### Algorithm Integration Patterns

**Always update algorithm state after interactions:**
```python
# BKT Update Pattern
from student_model.bkt import BKTModel
bkt = BKTModel()
updated_params = bkt.update_mastery(student_profile.bkt_parameters, interaction_data)
student_profile.bkt_parameters = updated_params
student_profile.save()  # CRITICAL: Must save after JSON field changes

# DKT Service Communication (with fallback)
try:
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8001/dkt/infer", json=payload) as response:
            dkt_result = await response.json()
except:
    # Fallback to BKT or mock data
    dkt_result = {"predictions": [0.5] * num_skills}
```

## API Architecture Patterns

### Django Ninja Router Structure
**Pattern**: All APIs follow this structure across apps:
```python
from ninja import Router
router = Router()

@router.post("/endpoint", response=SchemaClass)
def endpoint_function(request, payload: RequestSchema):
    try:
        # Implementation with transaction.atomic() for multi-model updates
        with transaction.atomic():
            # Update models
            return {"success": True, "data": result}
    except Exception as e:
        raise HttpError(500, f"Operation failed: {str(e)}")
```

### Frontend API Response Format (`frontend_api.py`)
**Standard**: All frontend endpoints return this exact format:
```python
class APIResponse(Schema):
    success: bool
    message: str  
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Usage
return api_success_response(data, "Operation completed")
return api_error_response("Error message", "ERROR_CODE", 400)
```

## Critical Issues & Solutions

### Exam Session Management
**Problem**: 14/15 student attempts are stuck in "IN_PROGRESS" status
**Solution**: Implement session timeout and proper completion:
```python
# Add to cron job or periodic task
def fix_stuck_sessions():
    from django.utils import timezone
    timeout_threshold = timezone.now() - timedelta(hours=3)
    
    StudentExamAttempt.objects.filter(
        status='IN_PROGRESS',
        started_at__lt=timeout_threshold
    ).update(status='TIMEOUT', submitted_at=timezone.now())
```

### UUID vs Integer ID Handling
**Important**: All models use UUID primary keys, but some legacy code expects integers:
```python
# Correct pattern for ID handling
def get_student_by_id(student_id):
    if isinstance(student_id, int):
        # Convert integer user ID to StudentProfile UUID
        user = User.objects.get(id=student_id)
        return user.student_profile
    return StudentProfile.objects.get(id=student_id)
```

## AI Features Integration

### LangGraph Workflows (`assessment/ai_analysis.py`)
**Environment requirement**: Must have `GOOGLE_API_KEY` set for Gemini API
```python
# Pattern for AI-enhanced endpoints
@router.post("/assessment/submit-answer")
def submit_with_ai_analysis(request, payload):
    # 1. Process answer with algorithms (BKT, DKT, IRT)
    # 2. If PRACTICE mode, generate AI hints
    # 3. If POST_EXAM mode, trigger LangGraph analysis
    
    if assessment_mode == 'PRACTICE':
        ai_hint = await generate_contextual_hint(question, student_state)
    elif assessment_mode == 'POST_EXAM':
        analysis = await trigger_langgraph_workflow(session_data)
```

### Assessment Mode Logic
```python
# Three distinct modes with different AI behavior:
EXAM = "EXAM"        # Pure algorithmic, no AI assistance
PRACTICE = "PRACTICE"  # AI hints and explanations available  
POST_EXAM = "POST_EXAM"  # Comprehensive AI analysis after completion
```

## Database & CSV Operations

### Question Import System
**Command**: `python manage.py import_exam_csv sample_data/questions.csv --subject logical_reasoning`
**Critical mapping**: CSV headers must match model fields exactly:
```csv
question_text,option_a,option_b,option_c,option_d,answer,difficulty,tags
"Question text","Option A","Option B","Option C","Option D","c","Easy","Logic"
```

### Performance Considerations
- Use `select_related()` for ForeignKeys, `prefetch_related()` for ManyToMany
- Algorithm updates require `transaction.atomic()` for consistency
- DKT service calls should always have timeout and fallback logic

## Common Pitfalls

1. **JSON field updates**: Must call `save()` after modifying JSON fields on models
2. **DKT service dependency**: Always check service health before calling endpoints  
3. **UUID consistency**: Don't mix integer IDs with UUID fields in queries
4. **Algorithm state sync**: BKT parameters must be updated after each interaction
5. **Session management**: Use `session_id` to link interactions for proper updates
6. **CORS configuration**: Pre-configured for React ports (3000, 5173, 8080) in settings

## Testing & Debugging

### Database Analysis
```python
# Quick system health check
python check_exam_db.py  # Shows counts, status distribution, stuck sessions
```

### Algorithm Testing  
```python
# Test individual algorithms
python final_comprehensive_test.py  # End-to-end algorithm testing
python working_ai_test.py  # Gemini API integration (requires GOOGLE_API_KEY)
```

**Current system status**: 562 questions, 18 exams, 105 students - functional but needs stuck session cleanup