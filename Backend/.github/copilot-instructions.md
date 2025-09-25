# Adaptive Learning System - AI Coding Guide

## Architecture Overview
This is a multi-algorithm adaptive learning platform combining **4 learning algorithms**: BKT (Bayesian Knowledge Tracing), DKT (Deep Knowledge Tracing), IRT (Item Response Theory), and SM-2 (Spaced Repetition). The system uses **Django + Django Ninja** for APIs with a separate **FastAPI DKT microservice**.

### Key Components
- **Django Apps**: `core` (student profiles), `assessment` (questions/interactions), `practice` (SRS), `analytics`, `student_model` (BKT/DKT integration)
- **DKT Microservice**: `dkt-service/` - FastAPI service (port 8001) with LSTM-based knowledge tracing
- **Frontend API Layer**: `frontend_api.py` - React-optimized endpoints combining all algorithms

## Critical Data Models

### StudentProfile (`core/models.py`)
```python
# JSON fields store algorithm state:
bkt_parameters = {"skill_id": {"P_L0": 0.1, "P_T": 0.3, "P_G": 0.2, "P_S": 0.1, "P_L": 0.4}}
dkt_hidden_state = [0.1, 0.2, 0.3, ...]  # Neural network state vector
current_level = {"algebra": 2, "geometry": 1}  # Per-skill progression
subject_progress = {"quantitative_aptitude": {"current_difficulty": "easy", "level": 2}}
```

### AdaptiveQuestion (`assessment/models.py`)
- Uses **CSV-compatible format**: `answer` field (a/b/c/d), `difficulty_level` (very_easy/easy/moderate/difficult)
- Multiple subject support: `quantitative_aptitude`, `logical_reasoning`, `data_interpretation`, `verbal_ability`
- **IRT parameters**: `difficulty`, `discrimination`, `guessing` fields for mathematical modeling

### Interaction (`assessment/models.py`)
- **Assessment modes**: `EXAM` (no AI help) vs `PRACTICE` (AI assistance available)
- Links student responses to BKT/DKT updates via `session_id`

## Algorithm Integration Patterns

### BKT Updates
```python
# Always update BKT parameters after interactions
from student_model.bkt import BKTModel
bkt = BKTModel()
updated_params = bkt.update_mastery(student_profile.bkt_parameters, interaction_data)
student_profile.bkt_parameters = updated_params
```

### DKT Service Communication
```python
# DKT runs on port 8001 - check service health first
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.post("http://localhost:8001/dkt/infer", json=payload) as response:
        dkt_result = await response.json()
```

### Question Selection Logic
1. **IRT-based difficulty**: Use `difficulty` parameter and student ability for optimal challenge
2. **Level-based progression**: Check `current_level` and `level_lock_status` before serving questions
3. **Subject routing**: Use `subject_progress` for competitive exam flows

## Development Workflows

### Running the System
```bash
# Django backend (port 8000)
python manage.py runserver

# DKT microservice (port 8001) - separate terminal
cd dkt-service
python start.py
# OR: start_dkt_service.bat (Windows)
```

### Database Changes
```bash
python manage.py makemigrations
python manage.py migrate
# Always test with sample data after model changes
```

### Testing AI Integration
- Use `working_ai_test.py` for Gemini API testing (requires `GOOGLE_API_KEY`)
- Use `final_comprehensive_test.py` for end-to-end algorithm testing
- DKT service has fallback mock mode when PyTorch unavailable

## API Patterns

### Django Ninja Router Structure
```python
# All APIs follow this pattern in each app's api.py:
from ninja import Router
router = Router()

@router.post("/endpoint", response=SchemaClass)
def endpoint_function(request, ...):
    # Implementation
```

### Frontend Integration
- Use `frontend_api.py` endpoints for React/UI consumption
- All responses include `success`, `message`, `data` structure
- Dashboard endpoints combine multiple algorithms: `/frontend/dashboard/student/{id}`

### Error Handling
- Always include try/catch blocks for algorithm calls
- Provide fallbacks when services unavailable (especially DKT microservice)
- Use logging: `logger.error(f"Error in {component}: {e}")`

## AI-Specific Features

### LangGraph Workflows (`assessment/ai_analysis.py`)
- **Post-exam analysis**: Uses Gemini API with structured workflows
- **Practice mode assistance**: Graduated hints and explanations
- Always check `GOOGLE_API_KEY` environment variable availability

### Assessment Modes
- **EXAM mode**: Pure algorithmic question selection, no AI hints
- **PRACTICE mode**: AI explanations, hints, and post-answer analysis available

## Configuration Management
- Use `python-decouple` for environment variables in `settings.py`
- **Redis caching**: Required for session management and performance
- **CORS setup**: Pre-configured for React development (ports 3000, 5000, 5173, 8080)

## Common Pitfalls
1. **DKT service dependency**: Always check service health before calling
2. **JSON field updates**: Must save `StudentProfile` after modifying JSON fields
3. **UUID consistency**: All models use UUID primary keys, not integers
4. **Algorithm state sync**: BKT parameters must be updated after each interaction
5. **Session management**: Use `session_id` to link interactions for proper algorithm updates

## API Architecture & Serialization Patterns

### Django Ninja Schema Design
All APIs use **Pydantic schemas** for request/response validation:
```python
# Standard pattern for all endpoints
class RequestSchema(Schema):
    student_id: str  # Always UUID strings, not integers
    required_field: str
    optional_field: Optional[str] = None

class ResponseSchema(Schema):
    success: bool
    data: Dict[str, Any]
    timestamp: datetime
```

### Critical API Endpoint Patterns

#### Main Assessment Orchestration (`assessment/api.py`)
- **POST `/assessment/submit-answer`** - **Core endpoint** orchestrating all 4 algorithms
- Uses `AssessmentSubmissionSchema` with `student_id`, `question_id`, `answer`, `response_time`
- Returns `AssessmentSubmissionResponseSchema` with algorithm results from BKT, DKT, IRT, SM-2
- **Always wrapped in `transaction.atomic()`** for consistency

#### BKT Algorithm APIs (`student_model/api.py`)
- **POST `/student-model/student/{student_id}/bkt/update`** - Update BKT parameters
- **GET `/student-model/student/{student_id}/bkt/states/all`** - Get all skill states
- Uses `BKTParametersSchema` with P_L0, P_T, P_G, P_S, P_L fields
- **Key pattern**: Always check `User.DoesNotExist` and return 404

#### SM-2 Spaced Repetition (`practice/api.py`)
- **GET `/practice/api/v1/practice/{student_id}/due-cards`** - Get cards due for review
- **POST `/practice/api/v1/practice/review`** - Process SM-2 review with quality score 0-5
- Uses WaniKani-style stages: `apprentice_1` through `burned`
- **Critical**: All SM-2 operations use `SM2Scheduler` class instance

#### Competitive Exam Flow (`assessment/competitive_api_v1.py`)
- **POST `/competitive/v1/assessment/start-subject`** - Subject-specific assessments
- **POST `/competitive/v1/assessment/submit-answer`** - Level-locked progression system
- Uses `subject_progress` JSON field for per-subject advancement tracking
- **Level progression**: Requires BKT mastery ≥ threshold + 3 consecutive correct

### Frontend API Layer (`frontend_api.py`)
- **GET `/frontend/dashboard/student/{student_id}`** - React-optimized dashboard combining all algorithms
- **POST `/frontend/assessment/start-session`** - Unified assessment session management
- **Always returns** `APIResponse` format: `{success, message, data, timestamp}`
- Pre-configured for React ports: 3000, 5000, 5173, 8080

### DKT Microservice Integration
```python
# Health check pattern before DKT calls
dkt_health = requests.get("http://localhost:8001/health", timeout=5)
if dkt_health.status_code == 200:
    # Use DKT service
else:
    # Fallback to BKT or stored fundamentals
```

### Serialization Utilities (`api_serializers.py`)
- **`get_student_by_id()`** - Handles both UUID and integer student IDs
- **`serialize_bkt_states()`** - Converts BKT parameters to API format
- **Mock data patterns** for development/testing scenarios
- **Always handle** `StudentProfile.DoesNotExist` gracefully

### Error Handling Patterns
```python
try:
    # Algorithm operations
except StudentProfile.DoesNotExist:
    raise HttpError(404, f"Student {student_id} not found")
except Exception as e:
    logger.error(f"Error in {operation}: {e}")
    raise HttpError(500, f"{operation} failed: {str(e)}")
```

### UUID vs Integer ID Handling
- **All models use UUID primary keys** (`UUIDField`)
- **Legacy support**: Some endpoints accept integer user IDs, convert to StudentProfile UUID
- **Frontend APIs**: Always expect and return string UUIDs
- **Database queries**: Use `select_for_update()` for concurrent algorithm updates

## CSV Data Structure & Import Patterns

### CSV File Format (`sample_data/*.csv`)
All competitive exam questions follow standardized CSV structure:
```csv
id,question_text,option_a,option_b,option_c,option_d,answer,difficulty,tags
1,"Question text here","Option A","Option B","Option C","Option D","c","Easy","Table Chart"
```

### Subject Categories
- **`data_interpretation.csv`** - Charts, graphs, tables (51 questions)
- **`reasoning.csv`** - Logic, patterns, coding-decoding (51 questions)  
- **`verbal.csv`** - Language, comprehension (51 questions)
- **Missing**: `quantitative_aptitude.csv` (mathematical problems)

### CSV Import System (`assessment/management/commands/import_exam_csv.py`)
```bash
# Import command pattern
python manage.py import_exam_csv sample_data/data_interpretation.csv --subject data_interpretation
python manage.py import_exam_csv sample_data/reasoning.csv --subject logical_reasoning
python manage.py import_exam_csv sample_data/verbal.csv --subject verbal_ability

# Advanced options
--clear-existing  # Remove existing questions first
--dry-run         # Preview without importing
--batch-size 100  # Batch processing size
```

### CSV-to-Model Mapping
- **Flexible headers**: Supports both `option_a/b/c/d` and `a/b/c/d` formats
- **Difficulty mapping**: `"Very easy"` → `very_easy`, `"Moderate"` → `moderate`
- **Auto-generated fields**: UUID IDs, IRT parameters, skill mapping
- **Subject assignment**: Maps to `AdaptiveQuestion.subject` enum choices
- **Level conversion**: `very_easy=1, easy=2, moderate=3, difficult=4`

### IRT Parameter Generation
```python
# Auto-generated based on difficulty level
irt_params = {
    'very_easy': {'difficulty': -1.5, 'discrimination': 0.8, 'guessing': 0.3},
    'easy': {'difficulty': -0.5, 'discrimination': 1.0, 'guessing': 0.25},
    'moderate': {'difficulty': 0.0, 'discrimination': 1.2, 'guessing': 0.2},
    'difficult': {'difficulty': 1.0, 'discrimination': 1.5, 'guessing': 0.1}
}
```

### CSV Serialization Utilities (`api_serializers.py`)
- **Mock data fallbacks** for development without database
- **UUID/integer conversion** via `get_student_by_id()`
- **BKT state serialization** via `serialize_bkt_states()`
- **Performance metrics** via `serialize_student_performance()`
- **Always handle missing data gracefully** with default values

## Testing Approach
- Unit tests for individual algorithms (`test_*.py` files)
- Integration tests for multi-algorithm workflows
- API tests using Django Ninja's built-in testing tools
- Mock DKT service when PyTorch unavailable in test environments