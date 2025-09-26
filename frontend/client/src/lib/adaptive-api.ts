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

// Types for adaptive learning system
export interface AdaptiveStudent {
  student_name: string;
  subject: SubjectCode | string; // Allow both for backward compatibility
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
  difficulty: string;
  difficulty_display: string;
  question_text: string;
  options: Array<{
    id: string;
    text: string;
  }>;
  correct_answer: string;
  explanation: string;
  adaptive_info: {
    mastery_level: number;
    skill_id: string;
    adaptive_reason: string;
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
    overall_progress: string;
    skill_level: string;
  };
  adaptive_info: {
    difficulty_trend: string;
    next_difficulty: string;
    learning_status: string;
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

// Adaptive Learning API client
export class AdaptiveLearningAPI {
  
  /**
   * Start a new adaptive learning session
   */
  static async startSession(data: AdaptiveStudent): Promise<AdaptiveSession> {
    console.log('🚀 Starting session with data:', data);
    console.log('📍 Making request to:', `${ADAPTIVE_API_BASE}/start-session`);
    
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
    
    return response.json();
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