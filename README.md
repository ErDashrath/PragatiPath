# 🎯 PragatiPath - AI-Powered Adaptive Learning System

## 📖 Overview

PragatiPath is a comprehensive Django-based adaptive learning system designed for competitive exam preparation. It combines cutting-edge AI algorithms with modern web technologies to provide personalized learning experiences. The system features advanced knowledge tracing algorithms, AI-powered assistance, and microservice architecture for scalable deployment.

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

## 🧠 Core AI Algorithms

### 1. Bayesian Knowledge Tracing (BKT)
- **Purpose**: Traditional probabilistic approach for knowledge assessment
- **Features**: Real-time Bayesian updates, mastery threshold tracking
- **Parameters**: P(L0), P(T), P(G), P(S)
- **Use Case**: Cold start situations, reliable baseline predictions

### 2. Deep Knowledge Tracing (DKT)
- **Purpose**: Neural network-based LSTM approach for complex pattern recognition
- **Architecture**: 2-layer LSTM with 128 hidden units
- **Features**: Sequence modeling, advanced pattern detection
- **Deployment**: Separate FastAPI microservice

### 3. Item Response Theory (IRT)
- **Purpose**: Adaptive question selection based on student ability
- **Features**: Automatic parameter generation, difficulty-based filtering
- **Integration**: Works with BKT for optimal question recommendation

### 4. Spaced Repetition System (SRS)
- **Algorithm**: SM-2 implementation with WaniKani-style stages
- **Features**: Optimal review scheduling, difficulty factor adjustment
- **Stages**: Apprentice → Guru → Master progression

## 🤖 AI Integration Features

### Assessment Modes
- **EXAM Mode**: Pure testing environment without AI assistance
- **PRACTICE Mode**: AI-powered hints and real-time explanations
- **POST-EXAM Mode**: Comprehensive analysis with study recommendations

### LangGraph + Gemini AI
- **Post-Exam Analysis**: Detailed performance insights
- **Intelligent Hints**: Graduated difficulty assistance
- **Personalized Explanations**: Context-aware learning support
- **Study Plan Generation**: AI-powered recommendations

## 📊 Competitive Exam Support

### Subjects Supported
- **Quantitative Aptitude**: 19 questions
- **Logical Reasoning**: 60 questions
- **Data Interpretation**: 50 questions
- **Verbal Ability**: 50 questions

### Difficulty Levels
- Very Easy (Level 1)
- Easy (Level 2)
- Moderate (Level 3)
- Difficult (Level 4)

### Question Management
- CSV import system with flexible header mapping
- Batch processing for large datasets
- Subject-wise progression tracking
- Performance analytics

## 🚀 API Endpoints

### Assessment API (v2)
- `POST /api/assessment/v2/assessment/start` - Start assessment with mode selection
- `POST /api/assessment/v2/exam/complete` - Complete exam and request AI analysis
- `GET /api/assessment/v2/exam/{session_id}/analysis` - Get post-exam AI analysis
- `POST /api/assessment/v2/practice/hint` - Request AI hints (Practice mode only)

### Student Model API
- `POST /api/student_model/student/{id}/bkt/update` - Update BKT parameters
- `GET /api/student_model/student/{id}/bkt/states/all` - All BKT states
- `POST /api/student_model/dkt/update` - Update DKT knowledge state
- `GET /api/student_model/algorithms/compare/{student_id}` - Compare BKT vs DKT

### Subject Management
- `POST /api/assessment/subject-questions` - Get questions by subject
- `GET /api/assessment/subjects` - List all subjects with counts
- `GET /api/assessment/subjects/{subject}/stats` - Subject statistics

## 🛠️ Technology Stack

### Backend
- **Django 5.2.6**: Main web framework
- **Django Ninja**: Modern API framework with automatic OpenAPI
- **FastAPI**: DKT microservice framework
- **PostgreSQL**: Primary database (with SQLite fallback)
- **Redis**: Caching and session storage
- **Celery**: Background task processing

### AI/ML Libraries
- **PyTorch**: LSTM neural networks for DKT
- **NumPy**: Numerical computing
- **LangGraph**: AI workflow orchestration
- **Google Gemini**: Advanced language model integration

### API & Integration
- **aiohttp**: Async HTTP client for microservice communication
- **Pydantic**: Data validation and serialization
- **uvicorn**: ASGI server for FastAPI

## 📁 Project Structure

```
PragatiPath/
├── Backend/                    # Django main application
│   ├── adaptive_learning/      # Django project settings
│   ├── core/                   # Core models and utilities
│   ├── student_model/          # BKT & DKT algorithms
│   ├── assessment/             # Question delivery & IRT
│   ├── analytics/              # Learning analytics
│   └── practice/               # SRS practice system
├── frontend/                   # Frontend application
├── api_tests/                  # API test suite
├── docs/                       # Project documentation
└── assessment/                 # Assessment utilities
```

## 🚦 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite included)
- Redis (for caching)
- Google Gemini API key (for AI features)

### 1. Environment Setup
```bash
# Clone the repository
cd PragatiPath

# Install dependencies
pip install -r Backend/requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Google API key to .env
```

### 2. Database Setup
```bash
cd Backend
python manage.py migrate
python manage.py create_test_students --count 5
```

### 3. Import Questions
```bash
# Import competitive exam questions
python manage.py import_exam_csv data.csv --subject quantitative_aptitude
```

### 4. Start Services
```bash
# Start Django application
python manage.py runserver 8000

# Start DKT microservice (in separate terminal)
cd dkt-service
python start.py
```

### 5. Access APIs
- **Django Ninja API Docs**: http://127.0.0.1:8000/api/docs
- **DKT Service Docs**: http://127.0.0.1:8001/docs
- **Health Check**: http://127.0.0.1:8000/api/student_model/status

## 🔧 Configuration

### Environment Variables
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/pragatipath

# Google Gemini AI Configuration
GOOGLE_API_KEY=your-gemini-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
```

## 📈 Key Features

### ✅ Intelligent Algorithm Selection
- Automatic switching between BKT and DKT based on data availability
- Ensemble approach when algorithms disagree
- Fallback mechanisms for high reliability

### ✅ Subject-Wise Progression
- Independent tracking per subject
- Level-based question unlocking
- Mastery threshold management

### ✅ AI-Powered Learning
- Context-aware hints and explanations
- Post-exam analysis with insights
- Personalized study plan generation

### ✅ Comprehensive Analytics
- Real-time performance tracking
- Algorithm comparison and recommendations
- Learning path visualization

## 🧪 Testing

### Run Test Suite
```bash
# Run comprehensive API tests
cd api_tests
python test_complete_workflow.py

# Test AI integration
python test_langraph_orchestration.py

# Test algorithm integration
python test_bkt_dkt_integration.py
```

### Test Data
- **179 imported questions** across 4 subjects
- **Test students** with various skill levels
- **Sample assessments** for each subject

## 🎯 Use Cases

1. **Competitive Exam Preparation**: JEE, NEET, CAT, GATE
2. **Personalized Learning Platforms**: Adaptive content delivery
3. **Intelligent Tutoring Systems**: AI-powered assistance
4. **Educational Analytics**: Performance insights and recommendations
5. **Skill Assessment Tools**: Competency evaluation

## 🚀 Advanced Features

### Algorithm Comparison Engine
- Real-time BKT vs DKT performance analysis
- Recommendation engine for optimal algorithm selection
- Ensemble predictions for improved accuracy

### Microservice Architecture
- Scalable DKT processing
- Independent service deployment
- Health monitoring and fallbacks

### Comprehensive Session Management
- Complete exam session lifecycle tracking
- Mode-based feature restrictions
- AI usage analytics

## 📊 Performance & Scalability

- **Async Processing**: Non-blocking AI inference
- **Caching**: Redis-based response optimization
- **Batch Processing**: Multiple student inference
- **Load Balancing**: Microservice scalability
- **Health Monitoring**: Service status tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for competitive exam preparation
- Inspired by modern adaptive learning research
- Powered by cutting-edge AI algorithms
- Designed for scalable educational technology

---

**PragatiPath**: Empowering personalized learning through AI-driven adaptive assessment and practice systems! 🎓✨