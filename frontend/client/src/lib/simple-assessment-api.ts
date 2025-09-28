// Simple Assessment API - Works like adaptive learning but for chapter assessments
export interface AssessmentSession {
  success: boolean;
  message: string;
  session_id: string;
  student_id: string;
  user_id: number;
  subject: string;
  chapter: string;
  question_count: number;
  session_type: 'assessment';
}

export interface AssessmentQuestion {
  success: boolean;
  question: {
    question_id: string; // UUID string
    question_number: number;
    question_text: string;
    options: Record<string, string>;
    difficulty: string;
    chapter: string;
    time_limit_seconds: number;
    assessment_info: {
      progress: string;
      chapter: string;
      assessment_type: string;
    };
  };
  session_progress: {
    current_question: number;
    total_questions: number;
    progress_percentage: number;
  };
}

export interface AssessmentAnswer {
  success: boolean;
  is_correct: boolean;
  correct_answer: string;
  question_number: number;
  total_questions: number;
  current_score: number;
  accuracy: number;
  session_complete: boolean;
  final_results?: {
    total_questions: number;
    correct_answers: number;
    accuracy: number;
    duration_seconds: number;
  };
}

export class SimpleAssessmentAPI {
  private static BASE_URL = 'http://localhost:8000/simple';

  // Start a new assessment session (like adaptive learning)
  static async startAssessment(data: {
    student_name: string;
    subject: string;
    chapter: string;
    question_count: number;
  }): Promise<AssessmentSession> {
    console.log('🚀 Starting assessment session with data:', data);
    console.log('📍 Making request to:', `${this.BASE_URL}/start-assessment/`);

    const response = await fetch(`${this.BASE_URL}/start-assessment/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📊 Response status:', response.status, response.ok ? 'OK' : 'ERROR');
    console.log('📋 Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Assessment start failed:', response.status, errorText);
      throw new Error(`Failed to start assessment: ${response.status} ${errorText}`);
    }

    const result = await response.json();
    console.log('✅ Assessment started successfully:', result);
    
    return result;
  }

  // Get the next question (like adaptive learning)
  static async getQuestion(sessionId: string): Promise<AssessmentQuestion> {
    console.log('🔍 Getting question for session:', sessionId);
    console.log('📍 Making request to:', `${this.BASE_URL}/get-assessment-question/?session_id=${sessionId}`);

    const response = await fetch(`${this.BASE_URL}/get-assessment-question/?session_id=${sessionId}`);

    console.log('📊 Response status:', response.status, response.ok ? 'OK' : 'ERROR');

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Get question failed:', response.status, errorText);
      throw new Error(`Failed to get question: ${response.status} ${errorText}`);
    }

    const result = await response.json();
    
    // Check if session is complete
    if (!result.success && result.session_complete) {
      console.log('✅ Assessment session completed');
      throw new Error('SESSION_COMPLETE');
    }

    console.log('✅ Question received:', result);
    return result;
  }

  // Submit an answer (like adaptive learning)
  static async submitAnswer(data: {
    session_id: string;
    question_id: string; // UUID string
    selected_answer: string;
    time_spent: number;
  }): Promise<AssessmentAnswer> {
    console.log('📝 Submitting answer:', data);
    console.log('📍 Making request to:', `${this.BASE_URL}/submit-assessment-answer/`);

    const response = await fetch(`${this.BASE_URL}/submit-assessment-answer/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📊 Response status:', response.status, response.ok ? 'OK' : 'ERROR');

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Submit answer failed:', response.status, errorText);
      throw new Error(`Failed to submit answer: ${response.status} ${errorText}`);
    }

    const result = await response.json();
    console.log('✅ Answer submitted:', result);
    
    return result;
  }

  // Health check
  static async healthCheck() {
    try {
      const response = await fetch(`${this.BASE_URL}/health/`);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export assessment utilities
export class AssessmentUtils {
  static getDifficultyColor(difficulty: string): string {
    switch (difficulty.toLowerCase()) {
      case 'easy':
      case 'very_easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
      case 'difficult':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  }

  static getDifficultyEmoji(difficulty: string): string {
    switch (difficulty.toLowerCase()) {
      case 'easy':
      case 'very_easy':
        return '🟢';
      case 'medium':
      case 'moderate':
        return '🟡';
      case 'hard':
      case 'difficult':
        return '🔴';
      default:
        return '🔵';
    }
  }

  static formatProgress(current: number, total: number): string {
    return `${current}/${total} (${Math.round((current / total) * 100)}%)`;
  }

  static formatAccuracy(accuracy: number): string {
    return `${accuracy.toFixed(1)}%`;
  }
}