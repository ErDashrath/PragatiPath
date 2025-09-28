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
    try {
      // First try regular assessment API
      const response = await fetch(`${API_BASE_URL}/history/students/${studentUsername}/assessment/${sessionId}`);
      if (response.ok) {
        return response.json();
      }
    } catch (error) {
      console.log('Regular assessment API failed, trying adaptive session API...');
    }

    try {
      // Fallback to adaptive session details API
      const adaptiveResponse = await fetch(`http://127.0.0.1:8000/history/session-details/${sessionId}/`);
      if (adaptiveResponse.ok) {
        const adaptiveData = await adaptiveResponse.json();
        
        if (adaptiveData.success) {
          // Transform adaptive session data to match DetailedAssessmentResult interface
          const sessionDetails = adaptiveData.session_details;
          const questionAttempts = adaptiveData.question_attempts || [];
          
          return {
            session_info: {
              session_id: sessionDetails.session_id,
              subject_name: sessionDetails.subject || 'Unknown',
              chapter_name: sessionDetails.chapter,
              session_type: sessionDetails.session_type,
              session_name: sessionDetails.session_name,
              status: sessionDetails.status,
              questions_attempted: sessionDetails.performance?.questions_attempted || 0,
              questions_correct: sessionDetails.performance?.questions_correct || 0,
              percentage_score: sessionDetails.performance?.percentage_score || 0,
              total_score: sessionDetails.performance?.total_score || 0,
              max_possible_score: sessionDetails.performance?.questions_attempted * 10 || 0,
              grade: this.calculateGrade(sessionDetails.performance?.percentage_score || 0),
              session_start_time: sessionDetails.created_at,
              session_end_time: sessionDetails.ended_at,
              session_duration_seconds: sessionDetails.duration_minutes ? sessionDetails.duration_minutes * 60 : 0,
              time_limit_minutes: sessionDetails.time_limit_minutes
            },
            question_attempts: questionAttempts.map((attempt: any, index: number) => ({
              question_number: index + 1,
              question_text: attempt.question_text || 'Question text not available',
              question_type: attempt.question_type || 'multiple_choice',
              options: attempt.options || {
                'A': attempt.option_a || 'Option A',
                'B': attempt.option_b || 'Option B', 
                'C': attempt.option_c || 'Option C',
                'D': attempt.option_d || 'Option D'
              },
              student_answer: attempt.student_answer || 'N/A',
              correct_answer: attempt.correct_answer || 'N/A',
              is_correct: attempt.is_correct || false,
              time_spent_seconds: attempt.time_spent || 0,
              points_earned: attempt.points_earned || (attempt.is_correct ? 10 : 0),
              question_points: 10,
              difficulty_level: attempt.difficulty || 'medium',
              topic: attempt.topic || attempt.skill_id || 'General',
              subtopic: attempt.subtopic || '',
              explanation: attempt.explanation || 'No explanation available',
              confidence_level: attempt.confidence_level
            })),
            performance_analysis: {
              topics_performance: this.calculateTopicsPerformance(questionAttempts),
              difficulty_performance: this.calculateDifficultyPerformance(questionAttempts),
              average_time_per_question: questionAttempts.length > 0 ? 
                questionAttempts.reduce((sum: number, q: any) => sum + (q.time_spent || 0), 0) / questionAttempts.length : 0,
              fastest_correct_answer: this.getFastestCorrect(questionAttempts),
              slowest_correct_answer: this.getSlowestCorrect(questionAttempts),
              strengths: this.identifyStrengths(questionAttempts, sessionDetails),
              improvement_areas: this.identifyImprovementAreas(questionAttempts, sessionDetails)
            },
            recommendations: this.generateRecommendations(sessionDetails, questionAttempts)
          };
        }
      }
    } catch (error) {
      console.error('Adaptive session API also failed:', error);
    }

    throw new Error('Failed to fetch detailed assessment result from both regular and adaptive APIs');
  }

  // Helper methods for data transformation
  private static calculateGrade(percentage: number): string {
    if (percentage >= 95) return 'A+';
    if (percentage >= 85) return 'A';
    if (percentage >= 75) return 'B';
    if (percentage >= 65) return 'C';
    if (percentage >= 50) return 'D';
    return 'F';
  }

  private static calculateTopicsPerformance(attempts: any[]): Record<string, { correct: number; total: number; accuracy: number }> {
    const topics: Record<string, { correct: number; total: number }> = {};
    
    attempts.forEach(attempt => {
      const topic = attempt.topic || attempt.skill_id || 'General';
      if (!topics[topic]) {
        topics[topic] = { correct: 0, total: 0 };
      }
      topics[topic].total++;
      if (attempt.is_correct) {
        topics[topic].correct++;
      }
    });

    const result: Record<string, { correct: number; total: number; accuracy: number }> = {};
    Object.keys(topics).forEach(topic => {
      result[topic] = {
        ...topics[topic],
        accuracy: topics[topic].total > 0 ? (topics[topic].correct / topics[topic].total) * 100 : 0
      };
    });

    return result;
  }

  private static calculateDifficultyPerformance(attempts: any[]): Record<string, { correct: number; total: number; accuracy: number }> {
    const difficulties: Record<string, { correct: number; total: number }> = {};
    
    attempts.forEach(attempt => {
      const difficulty = attempt.difficulty || 'medium';
      if (!difficulties[difficulty]) {
        difficulties[difficulty] = { correct: 0, total: 0 };
      }
      difficulties[difficulty].total++;
      if (attempt.is_correct) {
        difficulties[difficulty].correct++;
      }
    });

    const result: Record<string, { correct: number; total: number; accuracy: number }> = {};
    Object.keys(difficulties).forEach(difficulty => {
      result[difficulty] = {
        ...difficulties[difficulty],
        accuracy: difficulties[difficulty].total > 0 ? (difficulties[difficulty].correct / difficulties[difficulty].total) * 100 : 0
      };
    });

    return result;
  }

  private static getFastestCorrect(attempts: any[]): number {
    const correctAttempts = attempts.filter(a => a.is_correct && a.time_spent > 0);
    return correctAttempts.length > 0 ? Math.min(...correctAttempts.map(a => a.time_spent)) : 0;
  }

  private static getSlowestCorrect(attempts: any[]): number {
    const correctAttempts = attempts.filter(a => a.is_correct && a.time_spent > 0);
    return correctAttempts.length > 0 ? Math.max(...correctAttempts.map(a => a.time_spent)) : 0;
  }

  private static identifyStrengths(attempts: any[], sessionDetails: any): string[] {
    const strengths: string[] = [];
    const accuracy = sessionDetails.performance?.percentage_score || 0;
    
    if (accuracy >= 80) {
      strengths.push('Excellent overall performance');
    }
    
    const topicPerformance = this.calculateTopicsPerformance(attempts);
    Object.entries(topicPerformance).forEach(([topic, perf]) => {
      if (perf.accuracy >= 75 && perf.total >= 2) {
        strengths.push(`Strong performance in ${topic}`);
      }
    });

    const avgTime = attempts.length > 0 ? 
      attempts.reduce((sum, q) => sum + (q.time_spent || 0), 0) / attempts.length : 0;
    if (avgTime > 0 && avgTime < 45) {
      strengths.push('Good time management');
    }

    return strengths.length > 0 ? strengths : ['Keep practicing to build your strengths!'];
  }

  private static identifyImprovementAreas(attempts: any[], sessionDetails: any): string[] {
    const areas: string[] = [];
    const accuracy = sessionDetails.performance?.percentage_score || 0;
    
    if (accuracy < 60) {
      areas.push('Focus on understanding core concepts');
    }

    const topicPerformance = this.calculateTopicsPerformance(attempts);
    Object.entries(topicPerformance).forEach(([topic, perf]) => {
      if (perf.accuracy < 50 && perf.total >= 2) {
        areas.push(`Need more practice with ${topic}`);
      }
    });

    const avgTime = attempts.length > 0 ? 
      attempts.reduce((sum, q) => sum + (q.time_spent || 0), 0) / attempts.length : 0;
    if (avgTime > 90) {
      areas.push('Work on improving response time');
    }

    return areas;
  }

  private static generateRecommendations(sessionDetails: any, attempts: any[]): string[] {
    const recommendations: string[] = [];
    const accuracy = sessionDetails.performance?.percentage_score || 0;

    if (accuracy < 70) {
      recommendations.push('Review the fundamental concepts before attempting more questions.');
      recommendations.push('Practice similar questions to build confidence in this topic.');
    }

    if (sessionDetails.adaptive_insights?.difficulty_adjustments > 0) {
      recommendations.push('Great job! The system adapted to your skill level during the session.');
    }

    const topicPerformance = this.calculateTopicsPerformance(attempts);
    const weakTopics = Object.entries(topicPerformance)
      .filter(([_, perf]) => perf.accuracy < 60)
      .map(([topic]) => topic);

    if (weakTopics.length > 0) {
      recommendations.push(`Focus additional study time on: ${weakTopics.join(', ')}`);
    }

    recommendations.push('Continue using adaptive learning to get personalized question recommendations.');
    
    return recommendations;
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