 # PragatiPath Database Schema - Table Names & Relationships

## 📊 Complete Table List

### Core Authentication & User Management
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `auth_user` | User (Django built-in) | id (AutoField) | User authentication and basic info |
| `student_profiles` | StudentProfile | id (AutoField) | Extended student profile data |

### Assessment Core Tables
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `subjects` | Subject | id (AutoField) | Academic subjects (Quant, LR, DI, VA) |
| `chapters` | Chapter | id (AutoField) | Subject chapters/topics |
| `adaptive_questions` | AdaptiveQuestion | id (UUIDField) | Question bank with IRT parameters |
| `student_sessions` | StudentSession | id (UUIDField) | Multi-student session tracking |
| `question_attempts` | QuestionAttempt | id (BigAutoField) | Individual question responses |
| `interactions` | Interaction | id (UUIDField) | Legacy interaction tracking |
| `exam_sessions` | ExamSession | id (UUIDField) | Complete exam session tracking |

### Student Performance & Analytics
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `student_mastery` | StudentMastery | id (AutoField) | Subject/chapter mastery levels |
| `student_progress` | StudentProgress | id (AutoField) | Daily progress tracking |
| `daily_study_stats` | DailyStudyStats | id (AutoField) | Daily study statistics |

### Machine Learning Models
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `student_model_bkt_skill_state` | BKTSkillState | id (AutoField) | Bayesian Knowledge Tracing states |
| `student_model_knowledge_state` | StudentKnowledgeState | id (AutoField) | Knowledge component states |
| `student_model_interaction_history` | InteractionHistory | id (AutoField) | ML interaction history |

### Adaptive Learning System
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `adaptive_submissions` | AdaptiveSubmission | id (UUIDField) | Adaptive assessment submissions |
| `adaptive_submission_analytics` | AdaptiveSubmissionAnalytics | id (AutoField) | Submission analytics data |

### Spaced Repetition System
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `srs_cards` | SRSCard | id (AutoField) | Spaced repetition flashcards |

### Legacy Tables (Backward Compatibility)
| Table Name | Model Class | Primary Key | Description |
|------------|-------------|-------------|-------------|
| `user_sessions` | UserSession | id (UUIDField) | Legacy user session tracking |
| `user_question_history` | UserQuestionHistory | id (AutoField) | Legacy question history |
| `user_subject_progress` | UserSubjectProgress | id (AutoField) | Legacy subject progress |
| `user_daily_stats` | UserDailyStats | id (AutoField) | Legacy daily statistics |

---

## 🔗 Database Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          PRAGATIPATH DATABASE SCHEMA                                │
│                         Foreign Key Relationships                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│    auth_user     │ ◄─────────────────────────────────────┐
│ ================ │                                       │
│ • id (PK)        │                                       │
│ • username       │                                       │
│ • email          │                                       │
│ • first_name     │                                       │
│ • last_name      │                                       │
└──────────────────┘                                       │
         │                                                 │
         │ 1:1                                             │ 1:N
         ▼                                                 │
┌──────────────────┐                                       │
│ student_profiles │                                       │
│ ================ │                                       │
│ • id (PK)        │                                       │
│ • user_id (FK)   │────────────────────┐                 │
│ • grade_level    │                    │                 │
│ • learning_style │                    │                 │
│ • preferences    │                    │                 │
└──────────────────┘                    │                 │
                                         │                 │
┌──────────────────┐                     │                 │
│    subjects      │                     │                 │
│ ================ │                     │                 │
│ • id (PK)        │                     │                 │
│ • code           │                     │                 │
│ • name           │                     │                 │
│ • description    │                     │                 │
└──────────────────┘                     │                 │
         │                               │                 │
         │ 1:N                           │                 │
         ▼                               │                 │
┌──────────────────┐                     │                 │
│     chapters     │                     │                 │
│ ================ │                     │                 │
│ • id (PK)        │                     │                 │
│ • subject_id(FK) │──────────────────┐  │                 │
│ • name           │                  │  │                 │
│ • order          │                  │  │                 │
└──────────────────┘                  │  │                 │
         │                            │  │                 │
         │ 1:N                        │  │                 │
         ▼                            │  │                 │
┌──────────────────┐                  │  │                 │
│adaptive_questions│                  │  │                 │
│ ================ │                  │  │                 │
│ • id (PK-UUID)   │                  │  │                 │
│ • subject_fk(FK) │──────────────────┘  │                 │
│ • chapter_id(FK) │─────────────────────┘                 │
│ • question_text  │                                       │
│ • difficulty     │                                       │
│ • answer         │                                       │
│ • option_a       │                                       │
│ • option_b       │                                       │
│ • option_c       │                                       │
│ • option_d       │                                       │
└──────────────────┘                                       │
         │                                                 │
         │ 1:N                                             │
         ▼                                                 │
┌──────────────────┐          ┌──────────────────┐         │
│ student_sessions │          │  question_attempts│         │
│ ================ │          │ ================= │         │
│ • id (PK-UUID)   │          │ • id (PK)         │         │
│ • student_id(FK) │──────────┼─│ • student_id(FK) │─────────┘
│ • subject_id(FK) │──────────┐ │ • question_id(FK)│──────────┐
│ • chapter_id(FK) │──────────┼─│ • session_id(FK) │──────────┼─┐
│ • session_type   │          │ │ • is_correct     │          │ │
│ • status         │          │ │ • response_time  │          │ │
│ • mastery_score  │          │ │ • student_answer │          │ │
│ • questions_data │          │ │ • attempt_number │          │ │
└──────────────────┘          │ └──────────────────┘          │ │
         │                    │           │                   │ │
         │                    │           │ 1:N               │ │
         │                    │           ▼                   │ │
         │                    │ ┌──────────────────┐          │ │
         │                    │ │  interactions    │          │ │
         │                    │ │ ================ │          │ │
         │                    │ │ • id (PK-UUID)   │          │ │
         │                    │ │ • student_id(FK) │──────────┘ │
         │                    │ │ • question_id(FK)│────────────┘
         │                    │ │ • is_correct     │
         │                    │ │ • response_time  │
         │                    │ │ • session_id     │
         │                    │ │ • hints_used     │
         │                    │ └──────────────────┘
         │                    │
         │ 1:N                │
         ▼                    │
┌──────────────────┐          │
│ student_mastery  │          │
│ ================ │          │
│ • id (PK)        │          │
│ • student_id(FK) │──────────┘
│ • subject_id(FK) │───────────────────────┐
│ • chapter_id(FK) │───────────────────────┼─┐
│ • mastery_level  │                       │ │
│ • confidence     │                       │ │
│ • last_practiced │                       │ │
└──────────────────┘                       │ │
                                           │ │
┌──────────────────┐                       │ │
│ exam_sessions    │                       │ │
│ ================ │                       │ │
│ • id (PK-UUID)   │                       │ │
│ • student_id(FK) │───────────────────────┘ │
│ • subject        │                         │
│ • status         │                         │
│ • questions_attempted │                    │
│ • questions_correct   │                    │
│ • mastery_score      │                     │
└──────────────────┘                        │
                                            │
┌─────────────────────────────────────────────┐│
│         MACHINE LEARNING MODELS            ││
├─────────────────────────────────────────────┤│
│ student_model_bkt_skill_state              ││
│ • student_id (FK) ──────────────────────────┘│
│ • skill_id                                  │
│ • knowledge_state                           │
│ • learning_rate                             │
├─────────────────────────────────────────────┤
│ student_model_knowledge_state               │
│ • student_id (FK) ──────────────────────────┘
│ • knowledge_components (JSON)               │
│ • mastery_probabilities (JSON)              │
├─────────────────────────────────────────────┤
│ student_model_interaction_history           │
│ • student_id (FK) ──────────────────────────┐
│ • question_id (FK) ─────────────────────────┼─┐
│ • interaction_data (JSON)                   │ │
└─────────────────────────────────────────────┘ │
                                               │
┌─────────────────────────────────────────────┐ │
│         SPACED REPETITION SYSTEM           │ │
├─────────────────────────────────────────────┤ │
│ srs_cards                                   │ │
│ • user_id (FK) ─────────────────────────────┘ │
│ • question_id (FK) ───────────────────────────┘
│ • next_review_date                           │
│ • repetition_count                           │
│ • ease_factor                                │
│ • interval_days                              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         ADAPTIVE SUBMISSION SYSTEM          │
├─────────────────────────────────────────────┤
│ adaptive_submissions                        │
│ • student_id (FK) ──────────────────────────┐
│ • questions_data (JSON)                     │
│ • responses_data (JSON)                     │
│ • mastery_evolution (JSON)                  │
├─────────────────────────────────────────────┤
│ adaptive_submission_analytics               │
│ • submission_id (FK) ───────────────────────┘
│ • performance_metrics (JSON)                │
│ • improvement_analysis (JSON)               │
└─────────────────────────────────────────────┘
```

---

## 🔧 Foreign Key Constraints Summary

### Primary Relationships
```sql
-- Core User Relationships
ALTER TABLE student_profiles ADD CONSTRAINT fk_student_profiles_user 
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE;

-- Subject-Chapter Hierarchy
ALTER TABLE chapters ADD CONSTRAINT fk_chapters_subject 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE;

-- Question Relationships
ALTER TABLE adaptive_questions ADD CONSTRAINT fk_questions_subject 
    FOREIGN KEY (subject_fk) REFERENCES subjects(id) ON DELETE CASCADE;
ALTER TABLE adaptive_questions ADD CONSTRAINT fk_questions_chapter 
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE;

-- Session & Attempt Relationships
ALTER TABLE student_sessions ADD CONSTRAINT fk_sessions_student 
    FOREIGN KEY (student_id) REFERENCES auth_user(id) ON DELETE CASCADE;
ALTER TABLE student_sessions ADD CONSTRAINT fk_sessions_subject 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE;
ALTER TABLE student_sessions ADD CONSTRAINT fk_sessions_chapter 
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL;

ALTER TABLE question_attempts ADD CONSTRAINT fk_attempts_student 
    FOREIGN KEY (student_id) REFERENCES auth_user(id) ON DELETE CASCADE;
ALTER TABLE question_attempts ADD CONSTRAINT fk_attempts_question 
    FOREIGN KEY (question_id) REFERENCES adaptive_questions(id) ON DELETE CASCADE;
ALTER TABLE question_attempts ADD CONSTRAINT fk_attempts_session 
    FOREIGN KEY (session_id) REFERENCES student_sessions(id) ON DELETE CASCADE;

-- Mastery Tracking
ALTER TABLE student_mastery ADD CONSTRAINT fk_mastery_student 
    FOREIGN KEY (student_id) REFERENCES auth_user(id) ON DELETE CASCADE;
ALTER TABLE student_mastery ADD CONSTRAINT fk_mastery_subject 
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE;
ALTER TABLE student_mastery ADD CONSTRAINT fk_mastery_chapter 
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE;
```

### Index Strategy for Performance
```sql
-- Core Performance Indexes
CREATE INDEX idx_student_sessions_student_status ON student_sessions(student_id, status);
CREATE INDEX idx_question_attempts_session_timestamp ON question_attempts(session_id, timestamp);
CREATE INDEX idx_questions_subject_difficulty ON adaptive_questions(subject_fk, difficulty_level);
CREATE INDEX idx_mastery_student_subject ON student_mastery(student_id, subject_id);
CREATE INDEX idx_interactions_student_timestamp ON interactions(student_id, timestamp);
```

---

## 📈 Data Flow Architecture

### 1. **User Registration & Profile Setup**
```
auth_user → student_profiles → student_mastery (initial setup)
```

### 2. **Assessment Session Flow**
```
student_sessions → question_attempts → interactions → student_mastery (update)
```

### 3. **Adaptive Learning Pipeline**
```
question_attempts → BKT/DKT models → adaptive_questions (next selection)
```

### 4. **Performance Analytics**
```
question_attempts → daily_study_stats → student_progress → mastery tracking
```

---

## 🎯 Key Design Principles

1. **Cascade Deletion**: User deletion removes all associated data
2. **UUID Primary Keys**: For sessions and questions (better for distributed systems)
3. **JSON Fields**: For flexible data storage (responses, analytics)
4. **Proper Indexing**: Optimized for common query patterns
5. **Foreign Key Integrity**: Maintains referential integrity across tables
6. **Backward Compatibility**: Legacy tables maintained during migration

This schema supports the complete adaptive learning workflow from user registration through performance analytics and machine learning model updates.