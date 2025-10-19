import { useState, useEffect, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Clock, 
  Brain, 
  Target, 
  TrendingUp,
  CheckCircle,
  XCircle,
  Pause,
  Play,
  SkipForward,
  BarChart3,
  Lightbulb
} from "lucide-react";
import { 
  DynamicExamAPI, 
  DynamicExamSession, 
  AdaptiveQuestion, 
  QuestionResponse,
  SessionAnalytics,
  ExamTimingHelpers,
  ExamAnalyticsTracker
} from "@/lib/dynamic-exam-api";

interface DynamicExamInterfaceProps {
  examType: 'adaptive_subject' | 'practice_chapter' | 'scheduled_exam';
  examId: string; // Could be subjectCode, chapterId, or examId
  onExamComplete: (results: any) => void;
  onExamExit: () => void;
}

export default function DynamicExamInterface({ 
  examType, 
  examId, 
  onExamComplete, 
  onExamExit 
}: DynamicExamInterfaceProps) {
  
  const [session, setSession] = useState<DynamicExamSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AdaptiveQuestion | null>(null);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [isPaused, setIsPaused] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastAnswerFeedback, setLastAnswerFeedback] = useState<any>(null);
  const [analytics, setAnalytics] = useState<SessionAnalytics | null>(null);
  const [analyticsTracker, setAnalyticsTracker] = useState<ExamAnalyticsTracker | null>(null);
  const [confidenceLevel, setConfidenceLevel] = useState<number>(3);

  // Start exam session
  const startExamMutation = useMutation({
    mutationFn: async () => {
      let session: DynamicExamSession;
      
      switch (examType) {
        case 'adaptive_subject':
          session = await DynamicExamAPI.startAdaptiveSubjectTest(examId);
          break;
        case 'practice_chapter':
          session = await DynamicExamAPI.startPracticeChapterTest(examId);
          break;
        case 'scheduled_exam':
          session = await DynamicExamAPI.startScheduledExam(examId);
          break;
        default:
          throw new Error('Invalid exam type');
      }
      
      return session;
    },
    onSuccess: (session) => {
      setSession(session);
      setCurrentQuestion(session.current_question);
      setTimeRemaining(session.time_limit_minutes * 60);
      setAnalytics(session.session_analytics);
      setAnalyticsTracker(new ExamAnalyticsTracker(session.session_id));
    },
  });

  // Submit answer and get next question
  const submitAnswerMutation = useMutation({
    mutationFn: async (questionResponse: QuestionResponse) => {
      if (!session) throw new Error('No active session');
      return await DynamicExamAPI.submitAnswerAndGetNext(session.session_id, questionResponse);
    },
    onSuccess: (result) => {
      setLastAnswerFeedback(result.answer_feedback);
      setShowFeedback(true);
      setAnalytics(result.session_analytics);
      
      // Record analytics
      if (analyticsTracker && currentQuestion) {
        analyticsTracker.recordAnswer(
          result.answer_feedback.is_correct,
          currentQuestion.difficulty_level,
          currentQuestion.topic
        );
      }

      // Auto-proceed to next question after 3 seconds or when complete
      if (result.session_complete) {
        setTimeout(() => {
          completeExamMutation.mutate();
        }, 3000);
      } else {
        setTimeout(() => {
          setCurrentQuestion(result.next_question || null);
          setSelectedOptions([]);
          setShowFeedback(false);
          setConfidenceLevel(3);
          analyticsTracker?.startQuestion();
        }, 3000);
      }
    },
  });

  // Complete exam
  const completeExamMutation = useMutation({
    mutationFn: async () => {
      if (!session) throw new Error('No active session');
      return await DynamicExamAPI.completeExamSession(session.session_id);
    },
    onSuccess: (results) => {
      onExamComplete(results);
    },
  });

  // Timer effect
  useEffect(() => {
    if (!session || isPaused || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        const newTime = prev - 1;
        if (newTime <= 0) {
          completeExamMutation.mutate();
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [session, isPaused, timeRemaining]);

  // Start question timer when component mounts
  useEffect(() => {
    if (session && currentQuestion && analyticsTracker) {
      analyticsTracker.startQuestion();
    }
  }, [currentQuestion, analyticsTracker]);

  // Handle answer submission
  const handleSubmitAnswer = () => {
    if (!currentQuestion || selectedOptions.length === 0) return;

    const questionResponse: QuestionResponse = {
      question_id: currentQuestion.question_id,
      selected_options: selectedOptions,
      time_taken_seconds: ExamTimingHelpers.calculateTimeSpent(new Date().toISOString()),
      confidence_level: confidenceLevel,
      is_skipped: false
    };

    submitAnswerMutation.mutate(questionResponse);
  };

  // Handle skip question
  const handleSkipQuestion = () => {
    if (!currentQuestion) return;

    const questionResponse: QuestionResponse = {
      question_id: currentQuestion.question_id,
      selected_options: [],
      time_taken_seconds: ExamTimingHelpers.calculateTimeSpent(new Date().toISOString()),
      is_skipped: true
    };

    submitAnswerMutation.mutate(questionResponse);
  };

  // Handle pause/resume
  const handlePauseResume = async () => {
    if (!session) return;
    
    try {
      if (isPaused) {
        const resumedSession = await DynamicExamAPI.resumeSession(session.session_id);
        setSession(resumedSession);
        setIsPaused(false);
      } else {
        await DynamicExamAPI.pauseSession(session.session_id);
        setIsPaused(true);
      }
    } catch (error) {
      console.error('Error pausing/resuming session:', error);
    }
  };

  // Start exam on component mount
  useEffect(() => {
    startExamMutation.mutate();
  }, []);

  if (startExamMutation.isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Starting Dynamic Exam...</h3>
            <p className="text-muted-foreground">
              {examType === 'adaptive_subject' && 'Initializing adaptive subject test...'}
              {examType === 'practice_chapter' && 'Loading chapter practice questions...'}
              {examType === 'scheduled_exam' && 'Starting enhanced scheduled exam...'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!session || !currentQuestion) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <h3 className="text-lg font-semibold mb-2">Session Error</h3>
            <p className="text-muted-foreground mb-4">Unable to load exam session.</p>
            <Button onClick={onExamExit}>Return to Dashboard</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header with timer and controls */}
        <Card className="border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="text-lg font-semibold">
                    {ExamTimingHelpers.formatTimeRemaining(timeRemaining)}
                  </span>
                </div>
                <Badge variant="outline" className="flex items-center space-x-1">
                  <Brain className="h-3 w-3" />
                  <span>{currentQuestion.difficulty_level}</span>
                </Badge>
                {session.is_adaptive && (
                  <Badge variant="outline" className="flex items-center space-x-1">
                    <Target className="h-3 w-3" />
                    <span>Adaptive</span>
                  </Badge>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePauseResume}
                  disabled={showFeedback}
                >
                  {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                <Button variant="outline" size="sm" onClick={onExamExit}>
                  Exit
                </Button>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                <span>Question {currentQuestion.question_number} of {currentQuestion.total_questions}</span>
                <span>{analytics && Math.round((analytics.questions_correct / (analytics.questions_correct + analytics.questions_incorrect)) * 100) || 0}% correct</span>
              </div>
              <Progress 
                value={(currentQuestion.question_number / currentQuestion.total_questions) * 100} 
                className="h-2"
              />
            </div>
          </CardContent>
        </Card>

        {/* Question Card */}
        <Card className={showFeedback ? 'border-blue-200 bg-blue-50' : 'border-gray-200'}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">
                Question {currentQuestion.question_number}
              </CardTitle>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <span>📚 {currentQuestion.chapter}</span>
                <span>•</span>
                <span>🎯 {currentQuestion.topic}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Question Text */}
            <div className="text-lg leading-relaxed">
              {currentQuestion.question_text}
            </div>

            {/* Answer Options */}
            {!showFeedback && (
              <div className="space-y-3">
                {currentQuestion.options?.map((option) => (
                  <div
                    key={option.option_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedOptions.includes(option.option_id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      if (currentQuestion.question_type === 'mcq') {
                        setSelectedOptions([option.option_id]);
                      } else {
                        setSelectedOptions(prev => 
                          prev.includes(option.option_id)
                            ? prev.filter(id => id !== option.option_id)
                            : [...prev, option.option_id]
                        );
                      }
                    }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded border-2 ${
                        selectedOptions.includes(option.option_id)
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                      }`}>
                        {selectedOptions.includes(option.option_id) && (
                          <CheckCircle className="h-3 w-3 text-white" />
                        )}
                      </div>
                      <span>{option.option_text}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Feedback Display */}
            {showFeedback && lastAnswerFeedback && (
              <Alert className={lastAnswerFeedback.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                <div className="flex items-center space-x-2">
                  {lastAnswerFeedback.is_correct ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <span className="font-semibold">
                    {lastAnswerFeedback.is_correct ? 'Correct!' : 'Incorrect'}
                  </span>
                </div>
                <AlertDescription className="mt-2">
                  {lastAnswerFeedback.explanation}
                </AlertDescription>
                {lastAnswerFeedback.difficulty_adjustment && (
                  <div className="mt-2 text-sm flex items-center space-x-1">
                    <TrendingUp className="h-4 w-4" />
                    <span>Difficulty: {lastAnswerFeedback.difficulty_adjustment}</span>
                  </div>
                )}
              </Alert>
            )}

            {/* Confidence Level (only for adaptive exams) */}
            {session.is_adaptive && !showFeedback && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Confidence Level:</label>
                <div className="flex space-x-2">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <Button
                      key={level}
                      variant={confidenceLevel === level ? "default" : "outline"}
                      size="sm"
                      onClick={() => setConfidenceLevel(level)}
                    >
                      {level}
                    </Button>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  1 = Not confident, 5 = Very confident
                </p>
              </div>
            )}

            {/* Action Buttons */}
            {!showFeedback && (
              <div className="flex items-center justify-between pt-4">
                <Button
                  variant="outline"
                  onClick={handleSkipQuestion}
                  disabled={submitAnswerMutation.isPending}
                  className="flex items-center space-x-2"
                >
                  <SkipForward className="h-4 w-4" />
                  <span>Skip</span>
                </Button>
                
                <Button
                  onClick={handleSubmitAnswer}
                  disabled={selectedOptions.length === 0 || submitAnswerMutation.isPending}
                  className="flex items-center space-x-2 px-8"
                >
                  {submitAnswerMutation.isPending ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <CheckCircle className="h-4 w-4" />
                  )}
                  <span>Submit Answer</span>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Real-time Analytics */}
        {analytics && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Performance Analytics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {analytics.questions_correct}
                  </div>
                  <div className="text-sm text-muted-foreground">Correct</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {analytics.questions_incorrect}
                  </div>
                  <div className="text-sm text-muted-foreground">Incorrect</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.round(analytics.current_mastery_level * 100)}%
                  </div>
                  <div className="text-sm text-muted-foreground">Mastery</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.round(analytics.average_time_per_question)}s
                  </div>
                  <div className="text-sm text-muted-foreground">Avg Time</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}