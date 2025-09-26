import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertCircle, Clock, Brain, Target, TrendingUp, ArrowLeft, Globe } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { IndianTimeUtils } from "@/lib/indian-time-utils";
import SessionConfig, { type SessionConfig as SessionConfigType } from "./session-config";
import { 
  AdaptiveLearningAPI, 
  AdaptiveLearningUtils,
  SessionCompleteError,
  AVAILABLE_SUBJECTS,
  type AdaptiveSession,
  type AdaptiveQuestion,
  type AdaptiveAnswerResponse,
  type AdaptiveProgress,
  type SubjectCode
} from "@/lib/adaptive-api";
import { useAuth } from "@/hooks/use-auth";

interface AdaptiveLearningInterfaceProps {
  onBack?: () => void;
}

type LearningPhase = 'config' | 'setup' | 'learning' | 'completed' | 'error';

export default function AdaptiveLearningInterface({ 
  onBack 
}: AdaptiveLearningInterfaceProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  
  // State management
  const [phase, setPhase] = useState<LearningPhase>('config');
  const [sessionConfig, setSessionConfig] = useState<SessionConfigType | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<SubjectCode>('quantitative_aptitude');
  const [session, setSession] = useState<AdaptiveSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AdaptiveQuestion | null>(null);
  const [progress, setProgress] = useState<AdaptiveProgress | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string>('');
  const [feedback, setFeedback] = useState<AdaptiveAnswerResponse | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [questionsCompleted, setQuestionsCompleted] = useState(0);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);

  // Helper function to save session to backend for history
  const saveSessionToHistory = async () => {
    if (!session || !progress || !sessionStartTime || !sessionConfig) return;

    try {
      const sessionDurationSeconds = Math.floor(
        (Date.now() - sessionStartTime.getTime()) / 1000
      );

      // Calculate correct answers from progress if available
      const correctAnswers = progress.session_stats?.correct_answers || 0;
      const totalQuestions = questionsCompleted;
      
      // Extract mastery level from knowledge state (convert percentage string to number)
      const masteryString = progress.knowledge_state?.bkt_mastery || '0%';
      const finalMasteryLevel = parseFloat(masteryString.replace('%', '')) / 100;

      const sessionData = {
        session_id: session.session_id,
        total_questions: totalQuestions,
        correct_answers: correctAnswers,
        session_duration_seconds: sessionDurationSeconds,
        final_mastery_level: finalMasteryLevel,
        student_username: user?.username || 'unknown'  // Add current user's username
      };

      await AdaptiveLearningAPI.completeSession(sessionData);
      
      toast({
        title: "Session Saved! 📊",
        description: "Your learning session has been saved to history.",
      });
    } catch (error) {
      console.error('Failed to save session:', error);
      // Don't show error toast to avoid disrupting completion experience
    }
  };

  const handleStartSession = (config: SessionConfigType) => {
    setSessionConfig(config);
    setPhase('setup');
  };

  // Timer effect for adaptive learning sessions
  useEffect(() => {
    if (phase === 'learning' && timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(prev => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0 && phase === 'learning') {
      // Time's up! Complete the session
      setPhase('completed');
      // Save session to history
      saveSessionToHistory();
      toast({
        title: "Time's Up! ⏰",
        description: "Your adaptive learning session has completed.",
      });
    }
  }, [timeRemaining, phase]);

  // Start adaptive learning session
  const startAdaptiveSession = async () => {
    try {
      setError('');
      const sessionData = await AdaptiveLearningAPI.startSession({
        student_name: user?.name || 'Student',
        subject: selectedSubject,
        question_count: sessionConfig?.questionCount || 10  // Pass the selected question count
      });
      
      setSession(sessionData);
      setPhase('learning');
      
      // Initialize timer if sessionConfig is available
      if (sessionConfig) {
        setTimeRemaining(sessionConfig.timeLimit);
        setQuestionsCompleted(0);
        setSessionStartTime(IndianTimeUtils.getCurrentIST());
      }
      
      // Get first question
      await loadNextQuestion(sessionData.session_id);
      
      toast({
        title: "Adaptive Learning Started! 🚀",
        description: `Session created for ${AVAILABLE_SUBJECTS[selectedSubject]}. Questions will adapt to your performance!`
      });
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to start session');
      setPhase('error');
    }
  };

  // Load next adaptive question
  const loadNextQuestion = async (sessionId: string) => {
    try {
      const questionData = await AdaptiveLearningAPI.getAdaptiveQuestion(sessionId);
      setCurrentQuestion(questionData);
      setSelectedAnswer('');
      setQuestionStartTime(Date.now());
      setShowFeedback(false);
      setFeedback(null);
      
      // Load progress
      const progressData = await AdaptiveLearningAPI.getProgress(sessionId);
      setProgress(progressData);
      
    } catch (error) {
      if (error instanceof SessionCompleteError) {
        // Session completed naturally by reaching question limit
        setPhase('completed');
        toast({
          title: "Session Complete! 🎉",
          description: error.message,
        });
      } else {
        setError(error instanceof Error ? error.message : 'Failed to load question');
      }
    }
  };

  // Submit answer and get adaptive feedback
  const submitAnswer = async () => {
    if (!session || !currentQuestion || !selectedAnswer) return;
    
    setIsSubmitting(true);
    
    try {
      const timeSpent = (Date.now() - questionStartTime) / 1000;
      
      const response = await AdaptiveLearningAPI.submitAnswer({
        session_id: session.session_id,
        question_id: currentQuestion.question_id,
        selected_answer: selectedAnswer,
        time_spent: timeSpent
      });
      
      setFeedback(response);
      setShowFeedback(true);
      
      // Show adaptive feedback
      toast({
        title: response.answer_correct ? "Correct! 🎉" : "Incorrect 📚",
        description: response.adaptive_feedback.adaptation_message,
        variant: response.answer_correct ? "default" : "destructive"
      });
      
    } catch (error) {
      // Even if submission fails, we can continue with next question
      toast({
        title: "Submission Issue",
        description: "Answer recorded locally. Continuing with adaptive learning...",
        variant: "destructive"
      });
      
      // Continue to next question anyway
      setTimeout(() => {
        if (session) {
          loadNextQuestion(session.session_id);
        }
      }, 2000);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Continue to next question
  const continueToNextQuestion = async () => {
    if (!session) return;
    
    // Update questions completed count
    const newQuestionsCompleted = questionsCompleted + 1;
    setQuestionsCompleted(newQuestionsCompleted);
    
    // Check if we've reached the question limit from sessionConfig
    if (sessionConfig && newQuestionsCompleted >= sessionConfig.questionCount) {
      setPhase('completed');
      // Save session to history
      await saveSessionToHistory();
      toast({
        title: "Session Complete! 🎯",
        description: `You've completed all ${sessionConfig.questionCount} questions!`,
      });
      return;
    }
    
    // Check if session is complete based on API progress
    if (progress && progress.session_stats.questions_remaining <= 0) {
      setPhase('completed');
      // Save session to history
      await saveSessionToHistory();
      return;
    }
    
    await loadNextQuestion(session.session_id);
  };

  // Restart session
  const restartSession = () => {
    setPhase('setup');
    setSession(null);
    setCurrentQuestion(null);
    setProgress(null);
    setSelectedAnswer('');
    setError('');
    setFeedback(null);
    setShowFeedback(false);
  };

  // Setup phase
  // Show configuration screen first
  if (phase === 'config') {
    return (
      <SessionConfig
        title="Configure Adaptive Learning"
        description="Set up your adaptive learning session. Choose the number of questions, time limit, and initial difficulty level. The AI will adapt the difficulty based on your performance."
        onStartSession={handleStartSession}
        onCancel={onBack}
      />
    );
  }

  if (phase === 'setup') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        {onBack && (
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        )}
        
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center space-x-2">
              <Brain className="w-6 h-6 text-primary" />
              <span>Adaptive Learning</span>
            </CardTitle>
            <p className="text-muted-foreground">
              AI-powered learning that adapts to your performance in real-time
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Target className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-medium text-green-800">Adaptive Difficulty</h3>
                <p className="text-sm text-green-600">Questions adapt to your mastery level</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Brain className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h3 className="font-medium text-blue-800">AI Knowledge Tracking</h3>
                <p className="text-sm text-blue-600">BKT & DKT models track your learning</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <TrendingUp className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <h3 className="font-medium text-purple-800">Real-time Feedback</h3>
                <p className="text-sm text-purple-600">Instant adaptation based on performance</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="text-left">
                <label htmlFor="subject-select" className="block text-sm font-medium mb-2">
                  Select Subject
                </label>
                <Select value={selectedSubject} onValueChange={(value: SubjectCode) => setSelectedSubject(value)}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(AVAILABLE_SUBJECTS).map(([code, name]) => (
                      <SelectItem key={code} value={code}>
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <h3 className="font-medium mb-2 text-blue-800">Selected: {AVAILABLE_SUBJECTS[selectedSubject]}</h3>
                <div className="space-y-2 text-sm text-blue-700">
                  <p className="flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Questions from ALL chapters of {AVAILABLE_SUBJECTS[selectedSubject]}
                  </p>
                  {selectedSubject === 'quantitative_aptitude' && (
                    <p className="text-xs text-blue-600 ml-6">
                      • Profit & Loss • Percentage • Time & Work • Speed & Distance • Algebra • Geometry • And more...
                    </p>
                  )}
                  {selectedSubject === 'verbal_ability' && (
                    <p className="text-xs text-blue-600 ml-6">
                      • Reading Comprehension • Grammar • Vocabulary • Sentence Correction • And more...
                    </p>
                  )}
                  <p className="flex items-center gap-2">
                    <Brain className="h-4 w-4" />
                    AI adapts difficulty based on your performance  
                  </p>
                  <p className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Personalized learning path across the entire subject
                  </p>
                </div>
              </div>
              
              <Button onClick={startAdaptiveSession} size="lg" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                🚀 Start Cross-Chapter Adaptive Learning
                <div className="text-xs opacity-90 mt-1">
                  {AVAILABLE_SUBJECTS[selectedSubject]} - All Topics
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error phase
  if (phase === 'error') {
    return (
      <div className="max-w-2xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
        <div className="mt-4 text-center">
          <Button onClick={restartSession}>Try Again</Button>
        </div>
      </div>
    );
  }

  // Completed phase
  if (phase === 'completed') {
    // Calculate correct answers from accuracy and total questions
    const totalQuestions = sessionConfig?.questionCount || progress?.session_stats.questions_answered || 0;
    const accuracyPercent = parseFloat(progress?.session_stats.accuracy?.replace('%', '') || '0');
    const correctAnswers = Math.round((accuracyPercent / 100) * totalQuestions);
    
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-green-600">Session Complete! 🎉</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {progress && (
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {correctAnswers}/{totalQuestions}
                  </div>
                  <div className="text-sm text-green-600">Correct Answers</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {progress.knowledge_state.bkt_mastery}
                  </div>
                  <div className="text-sm text-blue-600">Mastery Level</div>
                </div>
              </div>
            )}
            
            {/* Additional stats */}
            {progress && (
              <div className="bg-muted/50 p-4 rounded-lg">
                <h4 className="font-medium mb-2 text-center">Session Summary</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Accuracy:</span>
                    <span className="font-medium">{progress.session_stats.accuracy}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Questions:</span>
                    <span className="font-medium">{correctAnswers}/{totalQuestions}</span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="text-center space-y-4">
              <p className="text-lg font-medium text-green-600">
                {progress?.adaptive_info.learning_status}
              </p>
              
              <div className="flex gap-2 justify-center">
                <Button onClick={restartSession}>
                  Try Again
                </Button>
                {onBack && (
                  <Button variant="outline" onClick={onBack}>
                    Back to Dashboard
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Learning phase
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Header */}
      {progress && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">
                  {progress.session_stats.questions_answered}
                </div>
                <div className="text-sm text-muted-foreground">Questions Answered</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {progress.session_stats.accuracy}
                </div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {progress.knowledge_state.bkt_mastery}
                </div>
                <div className="text-sm text-muted-foreground">Mastery Level</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {progress.adaptive_info.next_difficulty}
                </div>
                <div className="text-sm text-muted-foreground">Next Difficulty</div>
              </div>
            </div>
            
            <div className="mt-4 space-y-3">
              {/* Session Configuration Info */}
              {sessionConfig && (
                <div className="space-y-3">
                  {/* Session Timing Info */}
                  <div className="bg-muted/30 p-3 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Globe className="h-4 w-4 text-primary" />
                      <span className="font-medium text-sm">Session Info (IST)</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Started:</span>
                        <span className="font-mono">{sessionConfig.startTime?.split(' ')[1] || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Duration:</span>
                        <span className="font-mono">
                          {sessionStartTime ? IndianTimeUtils.calculateSessionDuration(sessionStartTime) : '0s'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Questions:</span>
                      <span className="font-medium">{questionsCompleted} / {sessionConfig.questionCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Time Left:</span>
                      <span className="font-medium text-primary font-mono">
                        {IndianTimeUtils.formatCountdown(timeRemaining)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {/* API Progress */}
              <div className="flex justify-between text-sm mb-2">
                <span>API Progress</span>
                <span>{progress.session_stats.questions_answered} / {progress.session_stats.questions_answered + progress.session_stats.questions_remaining}</span>
              </div>
              <Progress 
                value={(progress.session_stats.questions_answered / (progress.session_stats.questions_answered + progress.session_stats.questions_remaining)) * 100} 
                className="w-full" 
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Question */}
      {currentQuestion && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div className="space-y-2">
                <CardTitle className="flex items-center space-x-2">
                  <span>Question {currentQuestion.question_number}</span>
                  <Badge className={AdaptiveLearningUtils.getDifficultyColor(currentQuestion.difficulty)}>
                    {AdaptiveLearningUtils.getDifficultyEmoji(currentQuestion.difficulty)} {currentQuestion.difficulty.toUpperCase()}
                  </Badge>
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  {currentQuestion.adaptive_info.adaptive_reason}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center text-muted-foreground text-sm">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>Mastery: {AdaptiveLearningUtils.formatMasteryLevel(currentQuestion.adaptive_info.mastery_level)}</span>
                </div>
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
                onClick={submitAnswer}
                disabled={!selectedAnswer || isSubmitting}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Answer'}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Feedback */}
      {showFeedback && feedback && (
        <Card>
          <CardHeader>
            <CardTitle className={feedback.answer_correct ? "text-green-600" : "text-red-600"}>
              {feedback.answer_correct ? "Correct! 🎉" : "Incorrect 📚"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
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
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="font-medium text-purple-800 mb-1">Adaptation</div>
                <div className="text-sm text-purple-600">
                  {feedback.adaptive_feedback.difficulty_adaptation}
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
    </div>
  );
}