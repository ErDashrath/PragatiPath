# 🧠 BKT/DKT Integration with Adaptive Question Fetching

## 🎯 Overview

Our adaptive learning system now integrates **Bayesian Knowledge Tracing (BKT)** and **Deep Knowledge Tracing (DKT)** algorithms to provide intelligent, personalized question selection based on each student's real-time knowledge state.

## 🔄 How It Works

### **1. Knowledge State Tracking**

#### **BKT (Bayesian Knowledge Tracing)**
- **Purpose**: Probabilistic modeling of skill mastery
- **Parameters**:
  - `P(L0)`: Initial probability of knowing the skill
  - `P(T)`: Learning rate (transition from unknown to known)
  - `P(G)`: Guess rate (correct answer without knowing)
  - `P(S)`: Slip rate (wrong answer despite knowing)
  - `P(L)`: Current probability of knowing the skill
- **Updates**: After each question attempt using Bayesian inference

#### **DKT (Deep Knowledge Tracing)** 
- **Purpose**: Neural network-based sequence modeling
- **Architecture**: LSTM with 128 hidden units, 2 layers
- **Input**: Skill ID + correctness for last 100 interactions
- **Output**: 50 skill mastery probabilities (0-1 scale)
- **Service**: Runs as FastAPI microservice on port 8001

### **2. Intelligent Algorithm Selection**

The system automatically chooses the best algorithm based on data availability:

```python
# Algorithm Selection Logic
if total_attempts < 5:
    return 'bkt'  # Better for cold start
elif dkt_service_unavailable:
    return 'bkt'  # Reliable fallback
elif high_confidence_dkt and sufficient_data:
    return 'dkt'  # Neural patterns
else:
    return 'ensemble'  # Combine both
```

### **3. Adaptive Question Selection**

#### **BKT-Based Selection**
- **Weak Skills Focus**: 70% of questions target skills with P(L) < 0.6
- **Reinforcement**: 30% for skills with medium mastery (0.6-0.95)
- **Difficulty Mapping**:
  - Weak skills → Easy/Medium questions
  - Medium skills → Medium/Hard questions

#### **DKT-Based Selection**
- **Pattern Recognition**: Uses neural network predictions
- **Sequence-Aware**: Considers learning trajectory
- **Skill Mapping**: Maps questions to 50 skill categories (0-49)

#### **Ensemble Selection**
- **Hybrid Approach**: Combines BKT (50%) + DKT (50%) recommendations
- **Deduplication**: Removes overlapping questions
- **Confidence Weighting**: Prioritizes higher-confidence predictions

### **4. Real-Time Adaptation**

The system updates knowledge state after each question:

```python
# After each answer submission:
1. Update BKT parameters using Bayesian inference
2. Trigger DKT update via microservice (async)
3. Recalculate skill mastery probabilities
4. Adjust next question difficulty/topic
5. Log adaptive metadata for analysis
```

## 🚀 API Endpoints

### **Core Assessment APIs (Enhanced)**

#### **Start Assessment** - `/api/full-assessment/start`
```json
{
  "student_username": "student123",
  "subject_code": "MATH",
  "chapter_id": "algebra_basics",
  "question_count": 10,
  "assessment_type": "ADAPTIVE"
}
```
**Enhancement**: Now uses `AdaptiveQuestionSelector` instead of random selection.

#### **Submit Answer** - `/api/competitive/v1/assessment/submit-answer`  
```json
{
  "student_id": "student123",
  "question_id": "q456",
  "answer": "B",
  "is_correct": true,
  "response_time": 15.5
}
```
**Enhancement**: Updates both BKT and DKT knowledge states.

### **New Adaptive APIs**

#### **Get Knowledge State** - `/api/adaptive/knowledge-state`
```json
{
  "student_id": "student123",
  "subject_code": "MATH"
}
```
**Returns**: Complete BKT parameters + DKT predictions

#### **Get Adaptive Recommendations** - `/api/adaptive/recommendations`
```json
{
  "student_id": "student123", 
  "subject_code": "MATH",
  "count": 5,
  "assessment_type": "ADAPTIVE"
}
```
**Returns**: Personalized question list with selection reasoning

#### **Get Next Question** - `/api/adaptive/next-question`
```json
{
  "student_id": "student123",
  "session_id": "session_456",
  "previous_answers": [...]
}
```
**Returns**: Next optimal question based on recent performance

#### **Real-time Update** - `/api/adaptive/realtime/update-knowledge`
```json
{
  "student_id": "student123",
  "question_id": "q789", 
  "is_correct": true,
  "interaction_data": {...}
}
```
**Effect**: Immediately updates BKT/DKT knowledge state

## 📊 Selection Algorithms in Detail

### **BKT Selection Strategy**

```python
def bkt_based_selection(questions, knowledge_state, count):
    bkt_state = knowledge_state['bkt_state']
    
    # Identify skill categories
    weak_skills = [skill for skill, params in bkt_state.items() 
                   if params.P_L < 0.6]
    medium_skills = [skill for skill, params in bkt_state.items() 
                     if 0.6 <= params.P_L < 0.95]
    strong_skills = [skill for skill, params in bkt_state.items() 
                     if params.P_L >= 0.95]
    
    # Allocate questions
    weak_count = int(count * 0.7)      # 70% for weak skills
    medium_count = int(count * 0.2)    # 20% for medium skills  
    review_count = count - weak_count - medium_count  # 10% for review
    
    return select_questions_by_priority(weak_skills, medium_skills, strong_skills)
```

### **DKT Selection Strategy**

```python
def dkt_based_selection(questions, knowledge_state, count):
    skill_predictions = knowledge_state['dkt_state']['skill_predictions']
    
    # Find skills needing attention
    weak_skill_indices = [i for i, pred in enumerate(skill_predictions) 
                         if pred < 0.7]
    
    # Map questions to DKT skill space
    selected_questions = []
    for question in questions:
        skill_id = map_question_to_skill_id(question)
        if skill_id in weak_skill_indices:
            selected_questions.append(question)
    
    return selected_questions[:count]
```

### **Ensemble Strategy**

```python
def ensemble_selection(questions, knowledge_state, count):
    # Get recommendations from both algorithms
    bkt_questions = bkt_based_selection(questions, knowledge_state, count//2)
    dkt_questions = dkt_based_selection(questions, knowledge_state, count//2)
    
    # Merge with deduplication
    final_questions = merge_and_deduplicate(bkt_questions, dkt_questions)
    
    # Add metadata about selection method
    for q in final_questions:
        q['selection_method'] = 'bkt' if q in bkt_questions else 'dkt'
    
    return final_questions
```

## 🎯 Skill Mapping

### **Subject-Skill Mapping**
```python
SUBJECT_SKILLS = {
    'MATH': [
        'algebra_basics', 'algebra_equations', 'algebra_inequalities',
        'geometry_basics', 'geometry_areas', 'geometry_angles', 
        'arithmetic_fractions', 'arithmetic_decimals',
        'statistics_mean', 'statistics_probability'
    ],
    'PHY': [
        'mechanics_motion', 'mechanics_forces', 'mechanics_energy',
        'thermodynamics_heat', 'electricity_circuits', 
        'waves_sound', 'modern_physics'
    ],
    'CHEM': [
        'atomic_structure', 'periodic_table', 'chemical_bonding',
        'acids_bases', 'organic_chemistry', 'physical_chemistry'
    ]
}
```

### **Question-to-Skill Mapping**
```python
def map_question_to_skill_id(question):
    # Map difficulty to skill range
    difficulty_mapping = {
        'very_easy': 0,   # Skills 0-9
        'easy': 10,       # Skills 10-19  
        'medium': 20,     # Skills 20-29
        'hard': 30,       # Skills 30-39
        'very_hard': 40   # Skills 40-49
    }
    
    base_skill = difficulty_mapping.get(question.difficulty_level, 25)
    topic_variation = hash(question.topic) % 10 if question.topic else 0
    
    return min(49, base_skill + topic_variation)
```

## 📈 Performance & Adaptation

### **Real-Time Knowledge Updates**

1. **Answer Submission** → BKT parameter update (immediate)
2. **BKT Update** → Skill mastery recalculation
3. **DKT Update** → Microservice call (async, non-blocking)
4. **Next Question** → Selection based on updated state

### **Adaptation Triggers**

- **Mastery Achieved**: P(L) ≥ 0.95 → Move to harder skills
- **Struggle Detected**: 3 consecutive wrong → Easier questions  
- **Pattern Recognition**: DKT detects learning plateau → Topic switch
- **Confidence Drop**: Low DKT confidence → Fall back to BKT

### **Fallback Mechanisms**

```python
# Robust error handling
try:
    # Try adaptive selection with BKT/DKT
    questions = adaptive_selector.select_questions(...)
except DKTServiceUnavailable:
    # Fall back to BKT only
    questions = bkt_only_selection(...)
except BKTError:
    # Fall back to difficulty-based selection
    questions = difficulty_based_selection(...)
except Exception:
    # Ultimate fallback: random selection
    questions = random_selection(...)
```

## 🔧 Configuration & Tuning

### **BKT Parameters**
- **Default P(L0)**: 0.1 (10% initial knowledge)
- **Default P(T)**: 0.3 (30% learning rate)
- **Default P(G)**: 0.2 (20% guess rate)
- **Default P(S)**: 0.1 (10% slip rate)
- **Mastery Threshold**: 0.95 (95% confidence)

### **DKT Configuration**
- **Service URL**: `http://localhost:8001`
- **Sequence Length**: 100 interactions
- **Hidden Units**: 128
- **Skills**: 50 categories
- **Timeout**: 5 seconds

### **Adaptive Selection Tuning**
- **Cold Start Threshold**: 5 attempts
- **Confidence Threshold**: 0.7
- **Weak Skills Allocation**: 70%
- **Review Allocation**: 10%

## 🧪 Testing & Validation

### **Run Integration Tests**
```bash
python test_bkt_dkt_integration.py
```

This comprehensive test suite verifies:
- ✅ BKT algorithm functionality
- ✅ DKT microservice connectivity  
- ✅ Adaptive question selection
- ✅ Real-time knowledge tracking
- ✅ Algorithm comparison logic
- ✅ Fallback mechanisms

### **Monitor Performance**
```bash
# Check adaptive algorithm status
curl http://localhost:8000/api/adaptive/algorithms/status

# Get student knowledge state
curl -X POST http://localhost:8000/api/adaptive/knowledge-state \
  -d '{"student_id":"1","subject_code":"MATH"}'

# Debug selection process
curl http://localhost:8000/api/adaptive/debug/selection-trace/1
```

## 🎉 Benefits Achieved

### **For Students**
- **Personalized Learning**: Questions matched to current knowledge level
- **Optimal Difficulty**: Not too easy, not too hard - in the "zone of proximal development"
- **Efficient Practice**: Focus time on skills that need improvement
- **Real-time Feedback**: Immediate adaptation to performance

### **For Educators**  
- **Progress Tracking**: Detailed analytics on skill mastery
- **Intervention Alerts**: Identify students needing help
- **Curriculum Insights**: Understand which topics are challenging
- **Data-Driven Decisions**: Evidence-based teaching strategies

### **For System**
- **Higher Engagement**: Students stay motivated with appropriate challenges
- **Better Outcomes**: Faster skill acquisition through targeted practice  
- **Scalability**: Automated personalization for any number of students
- **Robustness**: Multiple fallback mechanisms ensure reliability

## 🚀 What's Next

### **Immediate Enhancements**
- [ ] Multi-skill questions mapping
- [ ] Learning style adaptation
- [ ] Spaced repetition scheduling
- [ ] Peer comparison insights

### **Advanced Features**
- [ ] Emotional state integration
- [ ] Collaborative filtering recommendations
- [ ] Metacognitive skill tracking
- [ ] Predictive intervention system

The BKT/DKT integration transforms static question delivery into an intelligent, adaptive system that grows smarter with each student interaction! 🧠✨