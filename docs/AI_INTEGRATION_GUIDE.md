# AI-Enhanced Competitive Exam System with LangGraph + Gemini

## 🎯 Overview

The system now integrates **LangGraph** with **Google's Gemini API** to provide comprehensive AI-powered analysis for post-exam insights and practice mode assistance, while maintaining strict separation between exam mode (no AI help) and post-exam analysis.

## 🚀 Key Features

### 1. **Assessment Modes**
- **EXAM Mode**: Pure assessment without any AI assistance during questions
- **PRACTICE Mode**: AI hints available, immediate explanations after each answer
- **Mode tracking** throughout the session

### 2. **Post-Exam AI Analysis** (Available after exam completion)
- **Comprehensive Analysis**: Subject-wise performance breakdown
- **Detailed Explanations**: AI-generated explanations for all incorrect answers
- **Personalized Study Plan**: Customized recommendations based on BKT weak areas
- **Learning Insights**: Concept analysis and improvement strategies

### 3. **Practice Mode AI Assistance**
- **Graduated Hints**: 3 levels of hints (subtle → specific → detailed)
- **Immediate Explanations**: Detailed explanations after each answer
- **Learning Guidance**: Tips for concept understanding and improvement

### 4. **BKT Integration**
- AI analysis incorporates **Bayesian Knowledge Tracing** mastery data
- Personalized recommendations based on skill progression
- Mastery trend analysis and predictions

## 🏗️ Architecture

### LangGraph Workflow
```
Exam Session → Question Analysis → Subject Analysis → BKT Integration → Recommendations → Study Plan → Final Report
```

### Components
- **`PostExamAnalysisWorkflow`**: LangGraph workflow for comprehensive analysis
- **`GeminiAIService`**: Interface to Google's Gemini AI
- **`PracticeAIAssistant`**: AI assistant for practice mode
- **`ExamSession`** model: Tracks complete exam sessions
- **Enhanced Interaction** model: Tracks assessment modes and AI usage

## 📚 API Endpoints

### Core Assessment Endpoints

#### Start Enhanced Assessment
```http
POST /api/assessment/v2/assessment/start
```
```json
{
  "student_id": "uuid",
  "subject": "quantitative_aptitude",
  "assessment_mode": "EXAM",  // or "PRACTICE"
  "preferred_difficulty": "moderate"
}
```

#### Submit Enhanced Answer
```http
POST /api/assessment/v2/assessment/submit-answer
```
```json
{
  "student_id": "uuid",
  "session_id": "uuid",
  "question_id": "uuid",
  "answer": "a",
  "response_time": 45.0,
  "assessment_mode": "EXAM",
  "hints_used": 0
}
```

### Post-Exam Analysis Endpoints

#### Complete Exam
```http
POST /api/assessment/v2/exam/complete
```
```json
{
  "student_id": "uuid",
  "session_id": "uuid",
  "request_ai_analysis": true
}
```

#### Get Comprehensive AI Analysis
```http
GET /api/assessment/v2/exam/{session_id}/analysis
```
**Response includes:**
- Question-by-question analysis
- Subject-wise performance breakdown
- BKT mastery integration
- Personalized study recommendations
- Comprehensive study plan

#### Get Explanations for Wrong Answers
```http
GET /api/assessment/v2/exam/{session_id}/explanations
```
**Response includes:**
- Detailed explanations for each incorrect answer
- Why the student's answer was wrong
- Key concepts tested
- Improvement tips

### Practice Mode AI Assistance

#### Request Hint (Practice Mode Only)
```http
POST /api/assessment/v2/practice/hint
```
```json
{
  "student_id": "uuid",
  "session_id": "uuid",
  "question_id": "uuid",
  "hint_level": 1  // 1=subtle, 2=specific, 3=detailed
}
```

#### Get Practice Explanation (Practice Mode Only)
```http
POST /api/assessment/v2/practice/explanation
```
```json
{
  "student_id": "uuid",
  "session_id": "uuid",
  "question_id": "uuid",
  "student_answer": "a"
}
```

## 🔒 Mode-Based Access Control

### EXAM Mode Restrictions
- ❌ No hints during questions
- ❌ No immediate AI feedback
- ❌ No explanations during exam
- ✅ Full post-exam AI analysis available

### PRACTICE Mode Features
- ✅ Graduated hints available
- ✅ Immediate explanations after answers
- ✅ Learning guidance and tips
- ✅ Continuous AI support

## 🛠️ Setup & Configuration

### 1. Install Dependencies
```bash
pip install langgraph langchain-google-genai python-dotenv
```

### 2. Environment Configuration
Update `.env` file:
```env
# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here
# Get your API key from: https://makersuite.google.com/app/apikey

# LangGraph/LangChain settings
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your-langchain-api-key-here-if-needed
LANGCHAIN_PROJECT=adaptive-learning-system
```

### 3. Database Migration
```bash
python manage.py makemigrations assessment
python manage.py migrate
```

### 4. Get Google API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 🧪 Testing

### Run Comprehensive Test
```bash
python test_ai_enhanced_system.py
```

**Test Coverage:**
- ✅ EXAM mode with no AI assistance
- ✅ Post-exam comprehensive analysis
- ✅ PRACTICE mode with AI hints
- ✅ Mode-based access restrictions
- ✅ BKT integration
- ✅ Error handling

## 📊 AI Analysis Features

### Question-Level Analysis
- **Detailed Explanations**: Why correct answer is right
- **Mistake Analysis**: Why student's answer was wrong
- **Concept Identification**: Key concepts tested
- **Improvement Tips**: Specific suggestions for each question

### Subject-Level Analysis
- **Performance Breakdown**: Strength and weakness areas
- **Mastery Assessment**: Current mastery level description
- **Learning Strategies**: Specific improvement approaches
- **Topic Recommendations**: What to study next

### Comprehensive Study Plan
- **Immediate Actions**: What to do right now
- **Weekly Schedule**: Structured learning plan
- **Priority Subjects**: Focus areas based on performance
- **Milestone Targets**: Achievable goals with timelines
- **Resource Recommendations**: Suggested study materials

## 🔄 Integration with Existing System

### BKT Integration
- AI analysis incorporates BKT mastery scores
- Recommendations based on skill progression
- Mastery trend analysis for personalized guidance

### Level Progression
- AI considers current level and unlocked difficulties
- Recommendations adapt to student's progression stage
- Study plan aligns with mastery-based advancement

### Question Database
- All existing questions compatible
- Subject and difficulty level integration
- Statistics and interaction tracking maintained

## 📈 Performance Monitoring

### AI Analysis Tracking
- `ExamSession.ai_analysis_requested`: Analysis request flag
- `ExamSession.ai_analysis_completed`: Completion status
- `ExamSession.ai_analysis_data`: Stored analysis results

### Practice Mode Tracking
- `Interaction.hints_requested`: Hints used per question
- `Interaction.ai_explanation_viewed`: Explanation usage
- `Interaction.assessment_mode`: Mode tracking

## 🎓 Educational Philosophy

### Exam Mode (No AI Help)
- **Pure Assessment**: Measure true understanding without assistance
- **Fair Evaluation**: Equal conditions for all students
- **Authentic Experience**: Simulates real exam conditions

### Post-Exam Analysis (Comprehensive AI)
- **Deep Learning**: Understand mistakes and concepts
- **Personalized Guidance**: Tailored to individual needs
- **Continuous Improvement**: Data-driven study recommendations

### Practice Mode (AI Assistance)
- **Guided Learning**: Support during the learning process
- **Immediate Feedback**: Learn from mistakes instantly
- **Confidence Building**: Hints help overcome challenging questions

## 🔮 Future Enhancements

### Planned Features
- **Voice-to-Text**: Explain concepts verbally
- **Visual Explanations**: Diagrams and charts for complex topics
- **Adaptive Difficulty**: AI-driven question selection
- **Peer Comparison**: Anonymous performance benchmarking
- **Progress Gamification**: Achievement system with AI insights

### Advanced AI Integration
- **Learning Path Optimization**: AI-optimized study sequences
- **Concept Mapping**: Visual representation of knowledge gaps
- **Predictive Analytics**: Forecast exam performance
- **Natural Language Queries**: Ask AI specific questions about topics

---

## 🚀 Quick Start

1. **Setup API Key**: Add your Gemini API key to `.env`
2. **Run Migrations**: Apply database changes
3. **Start Server**: `python manage.py runserver 8000`
4. **Run Test**: `python test_ai_enhanced_system.py`
5. **Take Exam**: Complete an exam with no AI help
6. **Get Analysis**: Receive comprehensive AI-powered insights

**The system maintains the integrity of assessments while providing powerful AI-driven learning support where appropriate.**