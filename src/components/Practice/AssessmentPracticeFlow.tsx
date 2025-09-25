import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Clock, CheckCircle, XCircle, Brain, Target, TrendingUp, ArrowRight, RotateCcw } from 'lucide-react';

// API Integration with Backend Orchestration
const API_BASE = 'http://localhost:8000';

interface Question {
  id: string;
  text: string;
  type: string;
  options: string[];
  difficulty: number;
  estimated_time: number;
  skill_id: string;
  subject: string;
}

interface BKTParameters {
  P_L: number;
  P_T: number;
  P_G: number;
  P_S: number;
  level: number;
}

interface AlgorithmResults {
  bkt: {
    status: string;
    new_mastery: number;
    parameters: BKTParameters;
    level_progression?: any;
  };
  dkt: {
    status: string;
    mastery_prediction: number;
    hidden_state_updated: boolean;
  };
  irt: {
    status: string;
    question_selected: boolean;
    selection_criteria: string;
  };
  sm2: {
    status: string;
    card_updated: boolean;
    stage_changed: boolean;
    new_interval: number;
  };
}

interface AssessmentResponse {
  success: boolean;
  interaction_id: string;
  was_correct: boolean;
  feedback: string;
  next_question: Question | null;
  algorithm_results: AlgorithmResults;
  performance_metrics: {
    total_interactions: number;
    recent_accuracy: number;
    session_interactions: number;
    avg_response_time: number;
    current_streak: number;
  };
  updated_student_state: {
    student_id: string;
    bkt_parameters: Record<string, BKTParameters>;
    fundamentals: Record<string, number>;
    level_progression: {
      current_level: number;
      unlocked_levels: number[];
      consecutive_correct: number;
      mastery_threshold: number;
    };
  };
  recommendations: string[];
}

interface AssessmentPracticeFlowProps {
  studentId: string;
  subject: string;
  topic: string;
  mode: 'assessment' | 'practice';
  onClose: () => void;
  onComplete: (results: any) => void;
}

const AssessmentPracticeFlow: React.FC<AssessmentPracticeFlowProps> = ({
  studentId,
  subject,
  topic,
  mode,
  onClose,
  onComplete
}) => {
  const [loading, setLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [sessionData, setSessionData] = useState<any>(null);
  const [progress, setProgress] = useState({ current: 0, total: 10 });
  const [responseTime, setResponseTime] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const [sessionResults, setSessionResults] = useState<AssessmentResponse[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastResponse, setLastResponse] = useState<AssessmentResponse | null>(null);
  const [aiInsights, setAiInsights] = useState<string>('');

  // Start assessment/practice session
  const startSession = useCallback(async () => {
    setLoading(true);
    try {
      const endpoint = mode === 'assessment' 
        ? `/api/frontend/assessment/start-session`
        : `/api/assessment/v2/practice/start`;
      
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          subject: subject,
          assessment_mode: mode,
          question_count: mode === 'assessment' ? 10 : 15,
          topic_focus: topic
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to start ${mode}`);
      }

      const data = await response.json();
      setSessionData(data);
      setCurrentQuestion(data.current_question || data.next_question);
      setProgress({ current: 1, total: data.progress?.total || 10 });
      setQuestionStartTime(Date.now());
    } catch (error) {
      console.error(`Error starting ${mode}:`, error);
      alert(`Failed to start ${mode}. Please try again.`);
    } finally {
      setLoading(false);
    }
  }, [studentId, subject, topic, mode]);

  // Submit answer using main orchestration endpoint
  const submitAnswer = useCallback(async () => {
    if (!selectedAnswer || !currentQuestion) return;

    setLoading(true);
    const currentTime = Date.now();
    const timeTaken = (currentTime - questionStartTime) / 1000; // Convert to seconds
    setResponseTime(timeTaken);

    try {
      // Use the main orchestration endpoint that integrates BKT, DKT, IRT, and SM-2
      const response = await fetch(`${API_BASE}/api/assessment/submit-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          question_id: currentQuestion.id,
          answer: selectedAnswer,
          skill_id: topic, // Use topic as skill_id for BKT tracking
          subject: subject,
          response_time: timeTaken,
          session_id: sessionData?.session_id,
          metadata: {
            mode: mode,
            attempt_number: 1,
            hint_used: false
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit answer');
      }

      const result: AssessmentResponse = await response.json();
      
      setLastResponse(result);
      setSessionResults(prev => [...prev, result]);
      setShowFeedback(true);

      // Generate AI insights based on performance
      if (result.algorithm_results.bkt.status === 'success') {
        generateAIInsights(result);
      }

      // Auto-advance after showing feedback
      setTimeout(() => {
        if (result.next_question) {
          setCurrentQuestion(result.next_question);
          setSelectedAnswer('');
          setShowFeedback(false);
          setQuestionStartTime(Date.now());
          setProgress(prev => ({ ...prev, current: prev.current + 1 }));
        } else {
          // Session complete
          completeSession();
        }
      }, 3000);

    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [selectedAnswer, currentQuestion, questionStartTime, studentId, topic, subject, sessionData, mode]);

  // Generate AI insights based on BKT/DKT results
  const generateAIInsights = useCallback(async (result: AssessmentResponse) => {
    try {
      const bktMastery = result.algorithm_results.bkt.new_mastery;
      const dktPrediction = result.algorithm_results.dkt.mastery_prediction;
      const recentAccuracy = result.performance_metrics.recent_accuracy;
      
      let insights = '';
      
      if (bktMastery >= 0.8) {
        insights = '🎉 Excellent mastery! You\'re ready for advanced topics.';
      } else if (bktMastery >= 0.6) {
        insights = '📈 Good progress! Focus on consistent practice.';
      } else {
        insights = '💪 Keep practicing! Review fundamentals for better understanding.';
      }

      // Add specific recommendations
      if (result.recommendations.length > 0) {
        insights += `\n\n📋 Recommendations:\n${result.recommendations.join('\n')}`;
      }

      setAiInsights(insights);
    } catch (error) {
      console.error('Error generating AI insights:', error);
    }
  }, []);

  // Complete session and show results
  const completeSession = useCallback(async () => {
    try {
      // Calculate session metrics
      const totalQuestions = sessionResults.length;
      const correctAnswers = sessionResults.filter(r => r.was_correct).length;
      const accuracy = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;
      const avgResponseTime = sessionResults.reduce((sum, r) => sum + responseTime, 0) / totalQuestions;
      
      // Get final BKT mastery levels
      const finalMastery = lastResponse?.algorithm_results.bkt.new_mastery || 0;
      
      const results = {
        mode,
        subject,
        topic,
        totalQuestions,
        correctAnswers,
        accuracy,
        avgResponseTime,
        finalMastery,
        bktProgression: sessionResults.map(r => r.algorithm_results.bkt.new_mastery),
        algorithmInsights: {
          bkt: `Mastery improved to ${(finalMastery * 100).toFixed(1)}%`,
          dkt: `Neural prediction confidence: ${((lastResponse?.algorithm_results.dkt.mastery_prediction || 0) * 100).toFixed(1)}%`,
          sm2: `Spaced repetition optimized for ${sessionResults.filter(r => r.algorithm_results.sm2.card_updated).length} cards`,
          irt: `Adaptive difficulty matching based on ability estimation`
        }
      };

      onComplete(results);
    } catch (error) {
      console.error('Error completing session:', error);
    }
  }, [sessionResults, lastResponse, mode, subject, topic, onComplete, responseTime]);

  useEffect(() => {
    startSession();
  }, [startSession]);

  if (loading && !currentQuestion) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardContent className="p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold">Preparing {mode === 'assessment' ? 'Assessment' : 'Practice Session'}...</h3>
            <p className="text-gray-600">Initializing BKT, DKT, IRT, and SM-2 algorithms...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (showFeedback && lastResponse) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {lastResponse.was_correct ? (
              <CheckCircle className="h-6 w-6 text-green-500" />
            ) : (
              <XCircle className="h-6 w-6 text-red-500" />
            )}
            {lastResponse.was_correct ? 'Correct!' : 'Incorrect'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-800 mb-3">{lastResponse.feedback}</p>
          </div>

          {/* Algorithm Results */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Brain className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">BKT Mastery</span>
              </div>
              <div className="text-lg font-bold text-blue-600">
                {(lastResponse.algorithm_results.bkt.new_mastery * 100).toFixed(1)}%
              </div>
            </div>

            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Target className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium">DKT Prediction</span>
              </div>
              <div className="text-lg font-bold text-purple-600">
                {(lastResponse.algorithm_results.dkt.mastery_prediction * 100).toFixed(1)}%
              </div>
            </div>

            <div className="bg-green-50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Accuracy</span>
              </div>
              <div className="text-lg font-bold text-green-600">
                {(lastResponse.performance_metrics.recent_accuracy * 100).toFixed(1)}%
              </div>
            </div>

            <div className="bg-orange-50 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="h-4 w-4 text-orange-600" />
                <span className="text-sm font-medium">Response Time</span>
              </div>
              <div className="text-lg font-bold text-orange-600">
                {responseTime.toFixed(1)}s
              </div>
            </div>
          </div>

          {/* AI Insights */}
          {aiInsights && (
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-2">🤖 AI Insights</h4>
              <div className="text-blue-700 whitespace-pre-line">{aiInsights}</div>
            </div>
          )}

          <div className="flex items-center justify-center">
            <div className="animate-pulse text-gray-600">
              Loading next question...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2">
            {mode === 'assessment' ? '📝' : '🏋️'} {subject} - {topic}
          </CardTitle>
          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
        <div className="space-y-2">
          <Progress value={(progress.current / progress.total) * 100} className="w-full" />
          <p className="text-sm text-gray-600">
            Question {progress.current} of {progress.total}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {currentQuestion && (
          <>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">{currentQuestion.text}</h3>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                <Badge variant="outline">
                  Difficulty: {(currentQuestion.difficulty * 100).toFixed(0)}%
                </Badge>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  ~{currentQuestion.estimated_time}s
                </span>
              </div>
            </div>

            <div className="space-y-3">
              {currentQuestion.options.map((option, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedAnswer === option
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedAnswer(option)}
                >
                  <label className="cursor-pointer flex items-center gap-3">
                    <input
                      type="radio"
                      name="answer"
                      value={option}
                      checked={selectedAnswer === option}
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                      className="text-blue-600"
                    />
                    <span>{option}</span>
                  </label>
                </div>
              ))}
            </div>

            <div className="flex justify-end">
              <Button
                onClick={submitAnswer}
                disabled={!selectedAnswer || loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <ArrowRight className="h-4 w-4" />
                )}
                Submit Answer
              </Button>
            </div>
          </>
        )}

        {/* Session Progress Indicators */}
        <div className="grid grid-cols-3 gap-4 pt-4 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {sessionResults.filter(r => r.was_correct).length}
            </div>
            <div className="text-sm text-gray-600">Correct</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {sessionResults.filter(r => !r.was_correct).length}
            </div>
            <div className="text-sm text-gray-600">Incorrect</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {sessionResults.length > 0 ? 
                ((sessionResults.filter(r => r.was_correct).length / sessionResults.length) * 100).toFixed(0) : 
                0}%
            </div>
            <div className="text-sm text-gray-600">Accuracy</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AssessmentPracticeFlow;