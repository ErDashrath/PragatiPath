// Adaptive Learning API service for direct frontend integration
const ADAPTIVE_API_BASE = '/simple'; // Use frontend proxy instead of direct backend

// Available subjects matching backend
export const AVAILABLE_SUBJECTS = {
  quantitative_aptitude: 'Quantitative Aptitude',
  logical_reasoning: 'Logical Reasoning', 
  data_interpretation: 'Data Interpretation',
  verbal_ability: 'Verbal Ability'
} as const;

export type SubjectCode = keyof typeof AVAILABLE_SUBJECTS;

// Custom error for session completion
export class SessionCompleteError extends Error {
  public sessionStats: any;
  
  constructor(message: string, sessionStats?: any) {
    super(message);
    this.name = 'SessionCompleteError';
    this.sessionStats = sessionStats;
  }
}

// Types for adaptive learning system
export interface AdaptiveStudent {
  student_name: string;
  subject: SubjectCode | string; // Allow both for backward compatibility
  question_count?: number; // Optional question count with default fallback
}

export interface AdaptiveSession {
  success: boolean;
  session_id: string;
  student_id: string;
  student_name: string;
  subject: string;
  next_action: string;
}

export interface AdaptiveQuestion {
  success: boolean;
  question_id: string;
  session_id: string;
  question_number: number;
  subject: string;
  subject_display: string;
  difficulty: string;
  difficulty_display: string;
  question_text: string;
  options: Array<{
    id: string;
    text: string;
  }>;
  correct_answer: string;
  explanation: string;
  topic?: string;
  subtopic?: string;
  adaptive_info: {
    mastery_level: number;
    skill_id: string;
    adaptive_reason: string;
    orchestration_enabled: boolean;
    bkt_mastery: number;
    dkt_prediction: number;
    real_question: boolean;
  };
  message: string;
  next_action: string;
}

export interface AdaptiveAnswerRequest {
  session_id: string;
  question_id: string;
  selected_answer: string;
  time_spent: number;
}

export interface AdaptiveAnswerResponse {
  success: boolean;
  answer_correct: boolean;
  correct_answer: string;
  selected_answer: string;
  explanation: string;
  knowledge_update: {
    bkt_updated: boolean;
    dkt_updated: boolean;
    new_mastery_level: number;
    dkt_prediction: number;
    mastery_display: string;
  };
  session_progress: {
    total_questions: number;
    correct_answers: number;
    accuracy: string;
    questions_remaining: number;
  };
  adaptive_feedback: {
    mastery_change: string;
    difficulty_adaptation: string;
    adaptation_message: string;
  };
  orchestration_feedback?: {
    bkt_mastery_change: string;
    dkt_prediction_change: string;
    combined_confidence_new: string;
    next_adaptation_strategy: string;
    learning_insight?: string;
  };
  message: string;
  next_action: string;
}

export interface AdaptiveProgress {
  success: boolean;
  session_id: string;
  student_name: string;
  subject: string;
  session_stats: {
    questions_answered: number;
    correct_answers: number;
    accuracy: string;
    questions_remaining: number;
  };
  knowledge_state: {
    bkt_mastery: string;
    dkt_prediction: string;
    combined_confidence: string;
    overall_progress: string;
    skill_level: string;
    orchestration_enabled: boolean;
  };
  adaptive_info: {
    difficulty_trend: string;
    next_difficulty: string;
    learning_status: string;
    bkt_dkt_integrated: boolean;
    orchestration_active: boolean;
  };
  orchestration_details: {
    langraph_active: boolean;
    bkt_mastery_raw: number;
    dkt_prediction_raw: number;
    combined_confidence_raw: number;
    adaptive_reasoning: string;
  };
  message: string;
}

export interface AdaptiveHealthResponse {
  success: boolean;
  status: string;
  message: string;
  services: {
    django: string;
    database: string;
    bkt_service: string;
    dkt_service: string;
  };
  endpoints: string[];
  ready_for_frontend: boolean;
}

// Unified Practice History interfaces
export interface UnifiedPracticeSession {
  session_id: string;
  type: 'practice';
  subject: string;
  session_date: string;
  stage: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  success_rate: number;
  total_reviews: number;
  mastery_level: string;
  mastery_score: number;
  question_text: string;
  next_review: string | null;
  is_due: boolean;
  priority_score: number;
}

export interface UnifiedAdaptiveSession {
  session_id: string;
  type: 'adaptive';
  subject: string;
  session_date: string;
  duration_minutes: number;
  questions_attempted: number;
  questions_correct: number;
  accuracy: string;
  mastery_scores: {
    bkt_mastery: string;
    bkt_mastery_raw: number;
    dkt_prediction: string;
    dkt_prediction_raw: number;
    mastery_level: string;
  };
  session_summary: string;
  adaptive_info: {
    difficulty_progression: string[];
    mastery_progression: number[];
    final_difficulty: string;
  };
}

export interface UnifiedPracticeHistory {
  success: boolean;
  student_id: string;
  student_name: string;
  total_sessions: number;
  practice_sessions: UnifiedPracticeSession[];
  adaptive_sessions: UnifiedAdaptiveSession[];
  combined_sessions: (UnifiedPracticeSession | UnifiedAdaptiveSession)[];
  summary_stats: {
    total_practice_cards: number;
    total_adaptive_sessions: number;
    practice_mastery_avg: number;
    adaptive_mastery_avg: number;
  };
  learning_insights: string[];
}

// Adaptive Learning API client
export class AdaptiveLearningAPI {
  
  /**
   * Start a new adaptive learning session
   */
  static async startSession(data: AdaptiveStudent): Promise<AdaptiveSession> {
    console.log('🚀 Starting session with data:', data);
    console.log('📍 Making request to:', `${ADAPTIVE_API_BASE}/start-session/`);
    
    const response = await fetch(`${ADAPTIVE_API_BASE}/start-session/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    console.log('📊 Response status:', response.status, response.statusText);
    console.log('📋 Response headers:', response.headers);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`Failed to start adaptive session: ${errorText}`);
    }
    
    const result = await response.json();
    console.log('✅ Session started successfully:', result);
    return result;
  }

  /**
   * Get adaptive question based on current mastery level
   */
  static async getAdaptiveQuestion(sessionId: string): Promise<AdaptiveQuestion> {
    console.log('🔍 Getting question for session:', sessionId);
    console.log('📍 Making request to:', `${ADAPTIVE_API_BASE}/get-question?session_id=${sessionId}`);
    
    const response = await fetch(`${ADAPTIVE_API_BASE}/get-question/${sessionId}/`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get adaptive question');
    }

    const result = await response.json();
    
    // Check if session is complete
    if (result.session_complete) {
      throw new SessionCompleteError(result.message || 'Session complete!', result.session_stats);
    }
    
    return result;
  }

  /**
   * Submit answer and get adaptive feedback
   */
  static async submitAnswer(data: AdaptiveAnswerRequest): Promise<AdaptiveAnswerResponse> {
    const response = await fetch(`${ADAPTIVE_API_BASE}/submit-answer/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to submit answer');
    }
    
    return response.json();
  }

  /**
   * Get session progress and learning analytics
   */
  static async getProgress(sessionId: string): Promise<AdaptiveProgress> {
    const response = await fetch(`${ADAPTIVE_API_BASE}/session-progress/${sessionId}/`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get progress');
    }
    
    return response.json();
  }

  /**
   * Check adaptive learning system health
   */
  static async healthCheck(): Promise<AdaptiveHealthResponse> {
    const response = await fetch(`${ADAPTIVE_API_BASE}/health/`);
    
    if (!response.ok) {
      throw new Error('Adaptive learning system health check failed');
    }
    
    return response.json();
  }

  /**
   * Complete and save session to history with mastery tracking
   */
  static async completeSession(data: {
    session_id: string;
    completion_reason?: string;
  }): Promise<{
    success: boolean;
    message: string;
    completion_data: {
      completion_reason: string;
      session_duration_minutes: number;
      questions_completed: number;
      accuracy_rate: string;
      final_mastery: {
        bkt_mastery: string;
        bkt_mastery_raw: number;
        dkt_prediction: string;
        dkt_prediction_raw: number;
        combined_confidence: string;
        combined_confidence_raw: number;
        mastery_level: string;
        mastery_achieved: boolean;
      };
      performance_summary: {
        total_questions: number;
        correct_answers: number;
        accuracy: number;
        subject: string;
        orchestration_enabled: boolean;
      };
      next_steps: {
        recommendation: string;
        suggested_difficulty: string;
        mastery_progress: string;
      };
    };
  }> {
    const requestData = {
      session_id: data.session_id,
      completion_reason: data.completion_reason || 'finished'
    };

    const response = await fetch(`${ADAPTIVE_API_BASE}/complete-session/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to complete session');
    }
    
    return response.json();
  }

  /**
   * Get session history with mastery progression
   */
  static async getSessionHistory(userId: number): Promise<{
    success: boolean;
    student_id: string;
    student_name: string;
    total_sessions: number;
    sessions: Array<{
      session_id: string;
      subject: string;
      session_date: string;
      duration_minutes: number;
      questions_attempted: number;
      accuracy: string;
      mastery_scores: {
        bkt_mastery: string;
        bkt_mastery_raw: number;
        dkt_prediction: string;
        dkt_prediction_raw: number;
        combined_confidence: string;
        combined_confidence_raw: number;
        mastery_level: string;
        mastery_achieved: boolean;
      };
      performance: {
        total_questions: number;
        correct_answers: number;
        accuracy_rate: number;
      };
    }>;
    mastery_progression: {
      latest_mastery: any;
      mastery_trend: string;
    };
  }> {
    const response = await fetch(`${ADAPTIVE_API_BASE}/session-history/${userId}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get session history');
    }
    
    return response.json();
  }

  /**
   * Get unified practice history (SM-2 + Adaptive Learning)
   * This fixes the fetching problem by bridging practice and adaptive learning systems
   */
  static async getUnifiedPracticeHistory(userId: number): Promise<UnifiedPracticeHistory> {
    console.log('🔍 Fetching unified practice history for user:', userId);
    console.log('📍 Making request to:', `${ADAPTIVE_API_BASE}/practice-history/${userId}/`);
    
    const response = await fetch(`${ADAPTIVE_API_BASE}/practice-history/${userId}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    console.log('📊 Unified practice history response status:', response.status);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Unified practice history error:', error);
      throw new Error(error.message || 'Failed to get unified practice history');
    }
    
    const result = await response.json();
    console.log('✅ Unified practice history loaded:', {
      total_sessions: result.total_sessions,
      practice_sessions: result.practice_sessions?.length,
      adaptive_sessions: result.adaptive_sessions?.length,
      insights: result.learning_insights?.length
    });
    
    return result;
  }
}

// Utility functions for adaptive learning
export class AdaptiveLearningUtils {
  
  /**
   * Format mastery level for display
   */
  static formatMasteryLevel(level: number): string {
    return `${Math.round(level * 100)}%`;
  }

  /**
   * Get difficulty color for UI
   */
  static getDifficultyColor(difficulty: string): string {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'hard':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }

  /**
   * Get difficulty emoji
   */
  static getDifficultyEmoji(difficulty: string): string {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return '🟢';
      case 'medium':
        return '🟡';
      case 'hard':
        return '🔴';
      default:
        return '⚪';
    }
  }

  /**
   * Calculate time per question
   */
  static formatTimeSpent(seconds: number): string {
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  }

  /**
   * Get learning status message
   */
  static getLearningStatusMessage(mastery: number): string {
    if (mastery >= 0.8) return "Excellent! You're mastering this topic! 🎉";
    if (mastery >= 0.6) return "Great progress! Keep it up! 📈";
    if (mastery >= 0.4) return "Good work! You're getting there! 💪";
    if (mastery >= 0.2) return "Building foundations... Stay focused! 🎯";
    return "Just getting started! Let's learn together! 🌱";
  }

  /**
   * Get recommendation based on performance
   */
  static getRecommendation(accuracy: number, mastery: number): string {
    if (accuracy >= 0.8 && mastery >= 0.7) {
      return "Ready for advanced topics!";
    } else if (accuracy >= 0.6) {
      return "Continue with current difficulty.";
    } else if (accuracy < 0.4) {
      return "Let's try easier questions to build confidence.";
    } else {
      return "Good progress! Keep practicing.";
    }
  }
}