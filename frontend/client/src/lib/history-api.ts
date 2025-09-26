// API service for assessment history
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface AssessmentHistoryItem {
  session_id: string;
  subject_name: string;
  chapter_name?: string;
  session_type: string;
  session_name: string;
  status: string;
  questions_attempted: number;
  questions_correct: number;
  percentage_score: number;
  total_score: number;
  max_possible_score: number;
  grade: string;
  session_start_time: string;
  session_end_time?: string;
  session_duration_seconds: number;
  time_limit_minutes?: number;
}

export interface StudentHistoryStats {
  total_assessments: number;
  completed_assessments: number;
  total_questions_attempted: number;
  total_questions_correct: number;
  overall_accuracy: number;
  average_session_time: number;
  best_accuracy: number;
  most_recent_session?: string;
  subjects_attempted: string[];
  favorite_subject?: string;
}

export interface DetailedAssessmentResult {
  session_info: AssessmentHistoryItem;
  question_attempts: Array<{
    question_number: number;
    question_text: string;
    question_type: string;
    options: Record<string, string>;
    student_answer: string;
    correct_answer: string;
    is_correct: boolean;
    time_spent_seconds: number;
    points_earned: number;
    question_points: number;
    difficulty_level: string;
    topic: string;
    subtopic: string;
    explanation: string;
    confidence_level?: number;
  }>;
  performance_analysis: {
    topics_performance: Record<string, { correct: number; total: number; accuracy: number }>;
    difficulty_performance: Record<string, { correct: number; total: number; accuracy: number }>;
    average_time_per_question: number;
    fastest_correct_answer: number;
    slowest_correct_answer: number;
    strengths: string[];
    improvement_areas: string[];
  };
  recommendations: string[];
}

export class HistoryAPI {
  // Get student's complete assessment history
  static async getStudentHistory(studentUsername: string): Promise<AssessmentHistoryItem[]> {
    const response = await fetch(`${API_BASE_URL}/history/students/${studentUsername}/history`);
    if (!response.ok) throw new Error('Failed to fetch assessment history');
    return response.json();
  }

  // Get student's overall statistics
  static async getStudentStats(studentUsername: string): Promise<StudentHistoryStats> {
    const response = await fetch(`${API_BASE_URL}/history/students/${studentUsername}/stats`);
    if (!response.ok) throw new Error('Failed to fetch student statistics');
    return response.json();
  }

  // Get detailed results for a specific assessment
  static async getDetailedAssessmentResult(
    studentUsername: string, 
    sessionId: string
  ): Promise<DetailedAssessmentResult> {
    const response = await fetch(`${API_BASE_URL}/history/students/${studentUsername}/assessment/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch detailed assessment result');
    return response.json();
  }

  // Get history for a specific subject
  static async getSubjectHistory(
    studentUsername: string, 
    subjectName: string
  ): Promise<AssessmentHistoryItem[]> {
    const response = await fetch(`${API_BASE_URL}/history/students/${studentUsername}/subjects/${encodeURIComponent(subjectName)}/history`);
    if (!response.ok) throw new Error('Failed to fetch subject history');
    return response.json();
  }
}