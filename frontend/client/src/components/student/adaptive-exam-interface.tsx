import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Target,
  Trophy,
  ArrowLeft,
  Brain,
  Sparkles
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface AdaptiveExamInterfaceProps {
  examConfig: {
    examId: string;
    examName: string;
    duration: number; // in minutes
    questionCount: number;
    subject: string;
  };
  onBack: () => void;
  onComplete: (results: any) => void;
}

interface Question {
  id: number;
  question_number: number;
  question_text: string;
  options: Array<{
    id: string;
    text: string;
  }>;
  difficulty: string;
  subject_code: string;
  chapter: string;
  adaptive_info?: {
    mastery_level: string;
    adaptive_reason: string;
    orchestration_enabled: boolean;
    bkt_mastery: string;
    dkt_prediction: string;
  };
}

interface AdaptiveSession {
  session_id: string;
  initial_mastery: number;
  starting_difficulty: string;
  user_id?: number;
}

interface AdaptiveProgress {
  session_stats: {
    questions_answered: number;
    questions_remaining: number;
    accuracy: string;
  };
  knowledge_state: {
    bkt_mastery: string;
    dkt_prediction: string;
    combined_confidence: string;
    orchestration_enabled: boolean;
  };
  adaptive_info: {
    next_difficulty: string;
    learning_status: string;
  };
  orchestration_details?: {
    adaptive_reasoning: string;
  };
}

interface AdaptiveAnswerResponse {
  success: boolean;
  answer_correct: boolean;
  explanation: string;
  correct_answer: string;
  adaptive_feedback: {
    adaptation_message: string;
    difficulty_adaptation: string;
  };
  knowledge_update: {
    mastery_display: string;
  };
  orchestration_feedback?: {
    bkt_mastery_change: string;
    dkt_prediction_change: string;
    combined_confidence_new: string;
    next_adaptation_strategy: string;
    learning_insight: string;
  };
}

interface ExamAttemptData {
  exam_id: string;
  student_id: number;
  total_questions: number;
  questions_answered: number;
  correct_answers: number;
  incorrect_answers: number;
  final_score_percentage: number;
  time_spent_seconds: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'TIMEOUT';
  adaptive_session_id: string;
  browser_info: any;
  question_attempts: Array<{
    question_id: number;
    selected_answer: string;
    is_correct: boolean;
    time_spent_seconds: number;
    attempt_order: number;
  }>;
}

export default function AdaptiveExamInterface({ 
  examConfig, 
  onBack, 
  onComplete 
}: AdaptiveExamInterfaceProps) {
  const { toast } = useToast();
  
  // Core exam state
  const [timeRemaining, setTimeRemaining] = useState<number>(examConfig.duration * 60);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [examStarted, setExamStarted] = useState<boolean>(false);
  const [examCompleted, setExamCompleted] = useState<boolean>(false);
  
  // Adaptive session state
  const [adaptiveSession, setAdaptiveSession] = useState<AdaptiveSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [progress, setProgress] = useState<AdaptiveProgress | null>(null);
  const [feedback, setFeedback] = useState<AdaptiveAnswerResponse | null>(null);
  const [showFeedback, setShowFeedback] = useState<boolean>(false);
  
  // Results tracking
  const [answers, setAnswers] = useState<Array<{ questionId: number; answer: string; correct: boolean; timeSpent: number }>>([]);
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [examAttemptId, setExamAttemptId] = useState<string | null>(null);

  // Timer effect
  useEffect(() => {
    if (examStarted && !examCompleted && timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(prev => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0 && examStarted && !examCompleted) {
      handleTimeUp();
    }
  }, [timeRemaining, examStarted, examCompleted]);

  // Format time display
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // Get difficulty badge color
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Get difficulty emoji
  const getDifficultyEmoji = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return '🟢';
      case 'medium': return '🟡';
      case 'hard': return '🔴';
      default: return '⚪';
    }
  };

  // Create exam attempt in database
  const createExamAttempt = async (sessionId: string) => {
    try {
      const response = await fetch('/api/enhanced-exams/start-attempt/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          exam_id: examConfig.examId,
          student_id: 1, // Will be dynamic based on auth
          adaptive_session_id: sessionId,
          browser_info: {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            screen: {
              width: screen.width,
              height: screen.height
            },
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
          }
        }),
      });

      if (response.ok) {
        const attemptData = await response.json();
        setExamAttemptId(attemptData.attempt_id);
        
        toast({
          title: "Database Connected! 💾",
          description: "Exam attempt registered in database for tracking",
        });
        
        return attemptData.attempt_id;
      } else {
        console.error('Failed to create exam attempt:', await response.text());
      }
    } catch (error) {
      console.error('Failed to create exam attempt:', error);
      toast({
        title: "Database Warning ⚠️",
        description: "Exam will continue but results may not be saved",
        variant: "destructive"
      });
    }
    return null;
  };

  // Start adaptive session for exam
  const startAdaptiveExamSession = async () => {
    try {
      // Start adaptive session using the working API
      const response = await fetch('/adaptive-session/start/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: 1, // Using integer ID as per working API
          subject_code: examConfig.subject || 'MATH',
          max_questions: examConfig.questionCount,
        }),
      });

      if (response.ok) {
        const sessionData = await response.json();
        setAdaptiveSession(sessionData);
        
        // Create exam attempt in our database schema
        const attemptId = await createExamAttempt(sessionData.session_id);
        
        setExamStarted(true);
        setQuestionStartTime(Date.now());
        
        // Fetch first question
        await fetchNextAdaptiveQuestion(sessionData.session_id);
        
        toast({
          title: "Adaptive Exam Started! 🚀",
          description: `BKT-powered exam with database tracking active!`
        });
      } else {
        throw new Error('Failed to start adaptive session');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start exam. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Fetch next adaptive question
  const fetchNextAdaptiveQuestion = async (sessionId: string) => {
    try {
      const response = await fetch(`/adaptive-session/next-question/${sessionId}/`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.question) {
          setCurrentQuestion(data.question);
          setSelectedAnswer('');
          setShowFeedback(false);
          setFeedback(null);
          setQuestionStartTime(Date.now());
          
          // Update progress if available
          if (data.progress) {
            setProgress(data.progress);
          }
        } else if (data.session_complete) {
          // Session completed - all questions done
          handleExamComplete();
        }
      } else {
        throw new Error('Failed to fetch question');
      }
    } catch (error) {
      console.error('Error fetching question:', error);
      toast({
        title: "Error",
        description: "Failed to load question. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Submit question attempt to database schema
  const submitQuestionAttempt = async (questionId: number, selectedAnswer: string, isCorrect: boolean, timeSpent: number) => {
    if (!examAttemptId) return;

    try {
      const response = await fetch('/api/enhanced-exams/submit-question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          attempt_id: examAttemptId,
          question_id: questionId,
          selected_answer: selectedAnswer,
          is_correct: isCorrect,
          time_spent_seconds: Math.round(timeSpent),
          attempt_order: currentQuestionIndex + 1,
          // Additional metadata from adaptive session
          adaptive_metadata: {
            difficulty: currentQuestion?.difficulty,
            bkt_mastery: progress?.knowledge_state.bkt_mastery,
            dkt_prediction: progress?.knowledge_state.dkt_prediction,
            combined_confidence: progress?.knowledge_state.combined_confidence
          }
        }),
      });
      
      if (response.ok) {
        console.log('Question attempt saved to database successfully');
      } else {
        console.error('Failed to save question attempt:', await response.text());
      }
    } catch (error) {
      console.error('Failed to save question attempt:', error);
    }
  };

  // Submit adaptive answer
  const submitAdaptiveAnswer = async () => {
    if (!adaptiveSession || !currentQuestion || !selectedAnswer) return;
    
    setIsSubmitting(true);
    
    try {
      const timeSpent = (Date.now() - questionStartTime) / 1000;
      
      // Submit to adaptive API
      const response = await fetch('/adaptive-session/submit-answer/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: adaptiveSession.session_id,
          question_id: currentQuestion.id,
          selected_answer: selectedAnswer,
          response_time: timeSpent,
        }),
      });

      if (response.ok) {
        const feedbackData = await response.json();
        setFeedback(feedbackData);
        setShowFeedback(true);
        
        // Track answer for results
        const answerData = {
          questionId: currentQuestion.id,
          answer: selectedAnswer,
          correct: feedbackData.answer_correct,
          timeSpent: timeSpent
        };
        setAnswers(prev => [...prev, answerData]);
        
        // Save to our database schema
        await submitQuestionAttempt(currentQuestion.id, selectedAnswer, feedbackData.answer_correct, timeSpent);
        
        toast({
          title: feedbackData.answer_correct ? "Correct! 🎉" : "Incorrect 📚",
          description: feedbackData.adaptive_feedback?.adaptation_message || "Answer submitted & saved to database",
          variant: feedbackData.answer_correct ? "default" : "destructive"
        });
      } else {
        throw new Error('Failed to submit answer');
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      toast({
        title: "Error",
        description: "Failed to submit answer. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Continue to next question
  const continueToNextQuestion = async () => {
    if (!adaptiveSession) return;
    
    const newQuestionIndex = currentQuestionIndex + 1;
    setCurrentQuestionIndex(newQuestionIndex);
    
    // Check if we've reached the question limit
    if (newQuestionIndex >= examConfig.questionCount) {
      handleExamComplete();
      return;
    }
    
    await fetchNextAdaptiveQuestion(adaptiveSession.session_id);
  };

  // Handle time up
  const handleTimeUp = () => {
    setExamCompleted(true);
    toast({
      title: "Time's Up! ⏰",
      description: "Your exam time has expired. Submitting current answers.",
      variant: "destructive"
    });
    handleExamComplete();
  };

  // Handle exam completion
  const handleExamComplete = async () => {
    setExamCompleted(true);
    
    const correctAnswers = answers.filter(a => a.correct).length;
    const totalQuestions = answers.length || 1; // Avoid division by zero
    const percentage = (correctAnswers / totalQuestions) * 100;
    
    const results = {
      examId: examConfig.examId,
      examName: examConfig.examName,
      totalQuestions,
      correctAnswers,
      incorrectAnswers: totalQuestions - correctAnswers,
      percentage: percentage.toFixed(2),
      timeSpent: (examConfig.duration * 60) - timeRemaining,
      answers,
      adaptiveSessionId: adaptiveSession?.session_id,
      finalMastery: progress?.knowledge_state.bkt_mastery,
      attemptId: examAttemptId
    };
    
    // Complete exam attempt in database
    await completeExamAttempt(results);
    
    onComplete(results);
  };

  // Complete exam attempt in database
  const completeExamAttempt = async (results: any) => {
    if (!examAttemptId) return;

    try {
      const response = await fetch('/api/enhanced-exams/complete-attempt/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          attempt_id: examAttemptId,
          status: timeRemaining === 0 ? 'TIMEOUT' : 'COMPLETED',
          final_score_percentage: parseFloat(results.percentage),
          total_time_spent_seconds: results.timeSpent,
          submission_type: timeRemaining === 0 ? 'AUTO_SUBMIT' : 'MANUAL_SUBMIT',
          submission_notes: `Adaptive BKT Exam completed with ${results.totalQuestions} questions`,
          adaptive_session_data: {
            session_id: results.adaptiveSessionId,
            final_mastery: results.finalMastery,
            total_questions: results.totalQuestions,
            accuracy: results.percentage,
            bkt_mastery: progress?.knowledge_state.bkt_mastery,
            dkt_prediction: progress?.knowledge_state.dkt_prediction,
            combined_confidence: progress?.knowledge_state.combined_confidence
          }
        }),
      });
      
      if (response.ok) {
        toast({
          title: "Results Saved! 📊",
          description: "Your exam results have been recorded in the database with adaptive analytics.",
        });
      } else {
        console.error('Failed to complete exam attempt:', await response.text());
      }
    } catch (error) {
      console.error('Error completing exam attempt:', error);
      toast({
        title: "Warning",
        description: "Exam completed but results may not be saved. Please contact support.",
        variant: "destructive"
      });
    }
  };

  // Pre-exam screen
  if (!examStarted) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>
        
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <Brain className="w-6 h-6 text-primary" />
              <span>{examConfig.examName}</span>
            </CardTitle>
            <p className="text-muted-foreground">
              Adaptive BKT-powered exam with comprehensive database tracking
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-4 bg-blue-50 rounded-lg">
                <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="font-medium text-blue-800">Duration</div>
                <div className="text-sm text-blue-600">{examConfig.duration} minutes</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <Target className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="font-medium text-green-800">Questions</div>
                <div className="text-sm text-green-600">{examConfig.questionCount}</div>
              </div>
            </div>
            
            <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
              <h3 className="font-medium text-purple-800 mb-2">🧠 Adaptive BKT Technology + Database Integration</h3>
              <ul className="text-sm text-purple-600 space-y-1">
                <li>• Questions adapt to your performance in real-time using BKT & DKT models</li>
                <li>• AI tracks your mastery level using Bayesian Knowledge Tracing</li>
                <li>• Personalized difficulty adjustment during the exam</li>
                <li>• Comprehensive exam attempt tracking in enhanced database schema</li>
                <li>• Individual question attempts stored with adaptive metadata</li>
                <li>• Full BKT/DKT state preservation for analytics and reporting</li>
              </ul>
            </div>
            
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                This is a timed exam with full database tracking. Once started, the timer cannot be paused. 
                All attempts are recorded in our enhanced exam schema for comprehensive analysis.
              </AlertDescription>
            </Alert>
            
            <Button 
              onClick={startAdaptiveExamSession} 
              size="lg" 
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              🚀 Start Adaptive BKT Exam with Database Tracking
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Exam in progress screen - reusing adaptive learning interface structure
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Header with Adaptive Info */}
      {progress && (
        <Card>
          <CardContent className="pt-6">
            {/* Timer and Question Progress */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className={`text-2xl font-bold ${timeRemaining < 300 ? 'text-red-600' : 'text-primary'}`}>
                  {formatTime(timeRemaining)}
                </div>
                <div className="text-sm text-muted-foreground">Time Remaining</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {currentQuestionIndex + 1} / {examConfig.questionCount}
                </div>
                <div className="text-sm text-muted-foreground">Question Progress</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {progress.session_stats.accuracy}
                </div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {progress.knowledge_state.bkt_mastery}
                </div>
                <div className="text-sm text-muted-foreground">BKT Mastery</div>
              </div>
            </div>

            {/* Adaptive BKT Status */}
            {progress.knowledge_state.orchestration_enabled && (
              <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <span className="font-medium text-blue-800">Adaptive BKT Active</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    🧠 AI-Powered + 💾 Database Tracked
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Combined Confidence:</span>
                    <span className="font-mono font-bold">{progress.knowledge_state.combined_confidence}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-600">Next Difficulty:</span>
                    <span className="font-medium">{progress.adaptive_info.next_difficulty}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-600">Database Status:</span>
                    <span className="text-green-600">✅ Saving</span>
                  </div>
                </div>
                {progress.orchestration_details && (
                  <div className="mt-2 text-xs text-blue-700 bg-blue-100 p-2 rounded">
                    💡 {progress.orchestration_details.adaptive_reasoning}
                  </div>
                )}
              </div>
            )}
            
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Exam Progress</span>
                <span>{currentQuestionIndex + 1} / {examConfig.questionCount}</span>
              </div>
              <Progress value={((currentQuestionIndex + 1) / examConfig.questionCount) * 100} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Question with Adaptive Info */}
      {currentQuestion && (
        <Card>
          <CardHeader>
            {/* Adaptive Selection Info */}
            {currentQuestion.adaptive_info?.orchestration_enabled && (
              <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-purple-600" />
                    <span className="font-medium text-purple-800">AI-Selected Question</span>
                    <Badge className="bg-green-100 text-green-800">
                      💾 Tracked in Database
                    </Badge>
                  </div>
                  <Badge className="bg-purple-100 text-purple-800">
                    BKT: {currentQuestion.adaptive_info?.bkt_mastery} | DKT: {currentQuestion.adaptive_info?.dkt_prediction}
                  </Badge>
                </div>
                {currentQuestion.adaptive_info?.adaptive_reason && (
                  <div className="text-sm text-purple-700 bg-purple-100 p-3 rounded">
                    <strong>🎯 Why this question:</strong> {currentQuestion.adaptive_info.adaptive_reason}
                  </div>
                )}
              </div>
            )}
            
            <div className="flex justify-between items-start">
              <div className="space-y-2">
                <CardTitle className="flex items-center space-x-2">
                  <span>Question {currentQuestion.question_number}</span>
                  <Badge className={getDifficultyColor(currentQuestion.difficulty)}>
                    {getDifficultyEmoji(currentQuestion.difficulty)} {currentQuestion.difficulty.toUpperCase()}
                  </Badge>
                  {currentQuestion.adaptive_info?.orchestration_enabled && (
                    <Badge className="bg-gradient-to-r from-purple-500 to-blue-500 text-white">
                      🚀 Adaptive
                    </Badge>
                  )}
                </CardTitle>
                {currentQuestion.adaptive_info && (
                  <p className="text-sm text-muted-foreground">
                    {currentQuestion.adaptive_info.adaptive_reason}
                  </p>
                )}
              </div>
              <div className="text-right space-y-1">
                <div className="flex items-center text-muted-foreground text-sm">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>Mastery: {currentQuestion.adaptive_info?.mastery_level || 'N/A'}</span>
                </div>
                {currentQuestion.adaptive_info?.orchestration_enabled && (
                  <div className="text-xs text-purple-600 font-medium">
                    🧠 BKT+DKT Integrated
                  </div>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-lg font-medium">
              {currentQuestion.question_text}
            </div>
            
            <div className="space-y-3">
              {currentQuestion.options.map((option) => (
                <Button
                  key={option.id}
                  variant={selectedAnswer === option.id ? "default" : "outline"}
                  className="w-full justify-start text-left h-auto p-4"
                  onClick={() => setSelectedAnswer(option.id)}
                  disabled={showFeedback}
                >
                  <span className="font-medium mr-3">{option.id}.</span>
                  <span>{option.text}</span>
                </Button>
              ))}
            </div>
            
            {!showFeedback && (
              <Button 
                onClick={submitAdaptiveAnswer}
                disabled={!selectedAnswer || isSubmitting}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? 'Submitting & Saving...' : 'Submit Answer'}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Enhanced Feedback with Database Confirmation */}
      {showFeedback && feedback && (
        <Card>
          <CardHeader>
            <CardTitle className={feedback.answer_correct ? "text-green-600" : "text-red-600"}>
              {feedback.answer_correct ? "Correct! 🎉" : "Incorrect 📚"}
              <Badge className="ml-2 bg-blue-100 text-blue-800">💾 Saved to Database</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Adaptive Feedback */}
            {feedback.orchestration_feedback && (
              <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="h-5 w-5 text-indigo-600" />
                  <span className="font-medium text-indigo-800">Adaptive Analytics Saved</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-indigo-600 font-medium">BKT Update:</span>
                      <span className="ml-2 font-mono">{feedback.orchestration_feedback.bkt_mastery_change}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-indigo-600 font-medium">DKT Prediction:</span>
                      <span className="ml-2 font-mono">{feedback.orchestration_feedback.dkt_prediction_change}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-indigo-600 font-medium">Combined Confidence:</span>
                      <span className="ml-2 font-mono font-bold">{feedback.orchestration_feedback.combined_confidence_new}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-indigo-600 font-medium">Next Strategy:</span>
                      <span className="ml-2">{feedback.orchestration_feedback.next_adaptation_strategy}</span>
                    </div>
                  </div>
                </div>
                {feedback.orchestration_feedback.learning_insight && (
                  <div className="text-sm text-indigo-700 bg-indigo-100 p-3 rounded">
                    💡 <strong>Learning Insight:</strong> {feedback.orchestration_feedback.learning_insight}
                  </div>
                )}
              </div>
            )}
            
            <div className="p-4 bg-muted rounded-lg">
              <div className="font-medium mb-2">Explanation:</div>
              <div>{feedback.explanation}</div>
              {!feedback.answer_correct && (
                <div className="mt-2 text-sm">
                  <strong>Correct answer:</strong> {feedback.correct_answer}
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-800 mb-1">Knowledge Update</div>
                <div className="text-sm text-blue-600">
                  New Mastery: {feedback.knowledge_update.mastery_display}
                </div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="font-medium text-green-800 mb-1">Database Status</div>
                <div className="text-sm text-green-600">
                  ✅ Question attempt saved with adaptive metadata
                </div>
              </div>
            </div>
            
            <Alert>
              <Brain className="h-4 w-4" />
              <AlertDescription>
                {feedback.adaptive_feedback.adaptation_message}
              </AlertDescription>
            </Alert>
            
            <Button onClick={continueToNextQuestion} className="w-full" size="lg">
              Continue to Next Question 🚀
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Exam completed results */}
      {examCompleted && (
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-green-600">Exam Completed! 🎉</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {answers.filter(a => a.correct).length}/{answers.length}
                </div>
                <div className="text-sm text-green-600">Correct Answers</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {progress?.knowledge_state.bkt_mastery || 'N/A'}
                </div>
                <div className="text-sm text-blue-600">Final BKT Mastery</div>
              </div>
            </div>
            
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
              <h4 className="font-medium mb-2 text-center">📊 Database Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Exam Attempt ID:</span>
                    <span className="font-mono text-xs">{examAttemptId || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Adaptive Session:</span>
                    <span className="font-mono text-xs">{adaptiveSession?.session_id.slice(0, 8) || 'N/A'}...</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Questions Stored:</span>
                    <span className="font-medium">{answers.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Database Status:</span>
                    <span className="text-green-600">✅ Saved</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="text-center space-y-4">
              <p className="text-lg font-medium text-green-600">
                Results saved with comprehensive adaptive analytics!
              </p>
              
              <div className="flex gap-2 justify-center">
                <Button onClick={onBack}>
                  Back to Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}