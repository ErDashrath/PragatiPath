# Adaptive Learning System - Project Summary

## 🎯 Project Overview
A comprehensive Django-based adaptive learning system with advanced knowledge tracing algorithms, built using Django Ninja API framework and microservice architecture.

## 🏗️ System Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   Frontend Client   │───▶│   Django Server     │───▶│  DKT Microservice│
│                     │    │   (Port 8000)       │    │   (Port 8001)    │
└─────────────────────┘    └─────────────────────┘    └──────────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │    PostgreSQL       │
                           │    Database         │
                           └─────────────────────┘
```

## 📁 Project Structure

```
StrawHatsH2/
├── adaptive_learning/          # Django main project
│   ├── settings.py            # Configuration
│   ├── urls.py               # Main URL routing with Django Ninja
│   └── celery.py             # Celery configuration
├── core/                     # Core models and utilities
│   └── models.py            # 4 core models (StudentProfile, etc.)
├── student_model/           # BKT & DKT algorithms
│   ├── api.py              # Django Ninja API endpoints
│   └── bkt.py              # BKT implementation
├── assessment/              # Question delivery & IRT
├── analytics/              # Learning analytics
├── practice/               # SRS practice system
├── dkt-service/            # DKT microservice
│   ├── main.py            # FastAPI application
│   ├── dkt_model.py       # LSTM implementation
│   └── requirements.txt   # PyTorch, FastAPI deps
└── manage.py              # Django management
```

## 🧠 Core Algorithms Implemented

### 1. Bayesian Knowledge Tracing (BKT)
- **Location**: `student_model/bkt.py`
- **Framework**: Pure Python with mathematical implementation
- **Features**:
  - P(L0): Initial knowledge probability
  - P(T): Learning transition rate
  - P(G): Guess rate
  - P(S): Slip rate
  - Real-time Bayesian updates
  - Mastery threshold tracking

### 2. Deep Knowledge Tracing (DKT)
- **Location**: `dkt-service/dkt_model.py`
- **Framework**: PyTorch LSTM
- **Architecture**:
  - 2-layer LSTM with 128 hidden units
  - Input: 100-dim (50 skills × 2 features)
  - Output: 50 skill mastery probabilities
  - Dropout regularization
- **Deployment**: Separate FastAPI microservice

### 3. Spaced Repetition System (SRS)
- **Location**: `core/models.py` (SRSCard model)
- **Algorithm**: SM-2 algorithm
- **Features**:
  - WaniKani-style stages (Apprentice → Guru → Master)
  - Difficulty factor adjustment
  - Optimal review scheduling

## 🚀 API Endpoints (Django Ninja)

### BKT Endpoints
- `POST /api/student_model/student/{id}/bkt/update` - Update BKT parameters
- `GET /api/student_model/student/{id}/bkt/state/{skill_id}` - Get BKT state
- `GET /api/student_model/student/{id}/bkt/states/all` - All BKT states
- `GET /api/student_model/student/{id}/bkt/mastered` - Mastered skills

### DKT Endpoints
- `POST /api/student_model/dkt/update` - Update DKT knowledge state
- `GET /api/student_model/dkt/predict/{student_id}` - Get DKT predictions
- `GET /api/student_model/dkt/health` - Check DKT service health

### Algorithm Comparison
- `GET /api/student_model/algorithms/compare/{student_id}` - Compare BKT vs DKT

## 🎛️ Database Models

### 1. StudentProfile
```python
class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.OneToOneField(User)
    bkt_parameters = models.JSONField()      # BKT skill states
    dkt_hidden_state = models.JSONField()    # DKT LSTM hidden state
    fundamentals_scores = models.JSONField() # Skill mastery scores
    preferences = models.JSONField()         # Learning preferences
```

### 2. AdaptiveQuestion  
- IRT parameters (difficulty, discrimination, guessing)
- Skill/knowledge component mappings
- Question metadata and content

### 3. Interaction
- Student-question interaction tracking
- Response correctness and timing
- Used for both BKT and DKT training

### 4. SRSCard
- Spaced repetition card states
- SM-2 algorithm parameters
- Review scheduling

## 🔧 Technology Stack

### Backend
- **Django 5.2.6**: Main web framework
- **Django Ninja**: Modern API framework with automatic OpenAPI
- **FastAPI**: DKT microservice framework
- **PyTorch**: LSTM neural networks for DKT
- **PostgreSQL**: Primary database (with SQLite fallback)
- **Redis**: Caching and session storage
- **Celery**: Background task processing

### ML/AI Libraries
- **PyTorch**: Deep learning framework
- **NumPy**: Numerical computing
- **Pydantic**: Data validation and serialization

### API & Integration
- **aiohttp**: Async HTTP client for microservice communication
- **requests**: Synchronous HTTP client
- **uvicorn**: ASGI server for FastAPI

## 🚦 Getting Started

### 1. Start Django Application
```bash
cd StrawHatsH2
python manage.py migrate
python manage.py runserver  # Runs on http://127.0.0.1:8000
```

### 2. Start DKT Microservice
```bash
cd dkt-service
start_dkt_service.bat  # Windows
# OR
python start.py       # Cross-platform
```

### 3. Access APIs
- **Django Ninja API Docs**: http://127.0.0.1:8000/api/docs
- **DKT Service Docs**: http://127.0.0.1:8001/docs
- **Health Check**: http://127.0.0.1:8000/api/student_model/status

## 🔄 Key Features

### 1. Intelligent Fallbacks
- DKT service unavailable → Falls back to BKT
- Database issues → Graceful degradation
- Missing dependencies → Mock mode

### 2. Real-time Learning Analytics
- Live BKT parameter updates
- LSTM-based knowledge state tracking
- Skill mastery progression monitoring

### 3. Microservice Architecture
- Scalable DKT processing
- Independent deployment
- Service health monitoring

### 4. Comprehensive API
- RESTful endpoints with Django Ninja
- Automatic OpenAPI documentation
- Pydantic data validation
- Error handling and logging

## 📈 Advanced Features

### Algorithm Comparison Engine
Compares BKT vs DKT predictions and recommends optimal algorithm based on:
- Data availability
- Prediction agreement
- Student interaction history

### Adaptive Question Selection
Uses knowledge tracing results to:
- Select optimal difficulty questions
- Focus on weak knowledge components
- Optimize learning efficiency

### Spaced Repetition Integration
Combines knowledge tracing with spaced repetition for:
- Long-term retention optimization
- Review scheduling
- Forgetting curve modeling

## 🎯 Use Cases

1. **Personalized Learning Platforms**
2. **Intelligent Tutoring Systems**
3. **Adaptive Assessment Tools**
4. **Educational Analytics Dashboards**
5. **Skill Certification Systems**

## 🚀 Next Steps

1. **Frontend Integration**: Connect React/Vue frontend
2. **Real-time Features**: WebSocket support for live updates
3. **Advanced Analytics**: Learning path visualization
4. **A/B Testing**: Algorithm performance comparison
5. **Production Deployment**: Docker, Kubernetes, monitoring

## 📊 Performance Features

- **Async Processing**: Non-blocking DKT inference
- **Caching**: Redis-based response caching
- **Batch Processing**: Multiple student inference
- **Load Balancing**: Microservice scalability
- **Health Monitoring**: Service status tracking

This adaptive learning system provides a solid foundation for building sophisticated educational applications with state-of-the-art knowledge tracing algorithms and modern web technologies.