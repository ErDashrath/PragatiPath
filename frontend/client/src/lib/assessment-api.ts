// API service for the complete assessment system
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Types for the assessment system
export interface Subject {
  id: number;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at?: string;
}

export interface Chapter {
  id: number;
  subject_id: number;
  name: string;
  description: string;
  chapter_number: number;
  is_active: boolean;
}

export interface Question {
  question_id: string;
  question_number: number;
  question_text: string;
  question_type: string;
  options: Record<string, string>;
  estimated_time_seconds: number;
  topic: string;
  subtopic: string;
  difficulty_level: string;
}

export interface AssessmentStartRequest {
  student_username: string;
  subject_code: string;
  chapter_id?: number;
  assessment_type: string;
  question_count: number;
  time_limit_minutes?: number;
}

export interface AssessmentStartResponse {
  assessment_id: string;
  student_username: string;
  subject_name: string;
  chapter_name?: string;
  question_count: number;
  time_limit_minutes?: number;
  status: string;
  created_at: string;
}

export interface AssessmentQuestionsResponse {
  assessment_id: string;
  questions: Question[];
  current_question_number: number;
  total_questions: number;
  time_remaining_minutes?: number;
}

export interface AnswerSubmissionRequest {
  assessment_id: string;
  question_id: string;
  selected_answer: string;
  time_taken_seconds: number;
  confidence_level?: number;
}

export interface AnswerSubmissionResponse {
  success: boolean;
  question_number: number;
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
  points_earned: number;
  next_question_available: boolean;
}

export interface QuestionResult {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  time_taken_seconds: number;
  points_earned: number;
  topic: string;
  difficulty_level: string;
}

export interface AssessmentResult {
  assessment_id: string;
  student_username: string;
  subject_name: string;
  chapter_name?: string;
  total_questions: number;
  questions_attempted: number;
  questions_correct: number;
  accuracy_percentage: number;
  total_time_seconds: number;
  total_points_earned: number;
  max_possible_points: number;
  grade: string;
  performance_analysis: any;
  question_results: QuestionResult[];
  completion_time: string;
}

// Assessment API functions
export class AssessmentAPI {
  // Get all subjects
  static async getSubjects(): Promise<Subject[]> {
    const response = await fetch(`${API_BASE_URL}/multi-student/subjects/`);
    if (!response.ok) throw new Error('Failed to fetch subjects');
    return response.json();
  }

  // Get chapters for a subject  
  static async getChapters(subjectId: number): Promise<Chapter[]> {
    const response = await fetch(`${API_BASE_URL}/multi-student/subjects/${subjectId}/chapters/`);
    if (!response.ok) throw new Error('Failed to fetch chapters');
    return response.json();
  }

  // Start a new assessment
  static async startAssessment(data: AssessmentStartRequest): Promise<AssessmentStartResponse> {
    const response = await fetch(`${API_BASE_URL}/full-assessment/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to start assessment');
    return response.json();
  }

  // Get assessment questions
  static async getAssessmentQuestions(assessmentId: string): Promise<AssessmentQuestionsResponse> {
    const response = await fetch(`${API_BASE_URL}/full-assessment/questions/${assessmentId}`);
    if (!response.ok) throw new Error('Failed to fetch questions');
    return response.json();
  }

  // Submit an answer
  static async submitAnswer(data: AnswerSubmissionRequest): Promise<AnswerSubmissionResponse> {
    const response = await fetch(`${API_BASE_URL}/full-assessment/submit-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to submit answer');
    return response.json();
  }

  // Complete assessment and get results
  static async completeAssessment(assessmentId: string): Promise<AssessmentResult> {
    const response = await fetch(`${API_BASE_URL}/full-assessment/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assessment_id: assessmentId }),
    });
    if (!response.ok) throw new Error('Failed to complete assessment');
    return response.json();
  }

  // Get student's past results
  static async getStudentResults(username: string): Promise<AssessmentResult[]> {
    const response = await fetch(`${API_BASE_URL}/full-assessment/student-results/${username}`);
    if (!response.ok) throw new Error('Failed to fetch student results');
    return response.json();
  }

  // Health check
  static async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/full-assessment/health`);
    if (!response.ok) throw new Error('API health check failed');
    return response.json();
  }
}