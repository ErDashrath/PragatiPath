import { useState, useEffect, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  Timer, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  FileText,
  LogOut,
  Save,
  Flag,
  ArrowLeft,
  ArrowRight,
  Brain,
  Target,
  TrendingUp
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/use-auth";


interface AdaptiveQuestion {
  id: string;
  question_text: string;
  options: {
    a: string;
    b: string;
    c: string;
    d: string;
  };
  correct_answer: string;
  difficulty_level: string;
  subject: string;
  chapter_name?: string;
  knowledge_component?: string;
  explanation?: string;
}

interface MasteryStatus {
  current_score: number;
  mastery_achieved: boolean;
  mastery_level: string;
  confidence: number;
  questions_remaining: number;
  bkt_parameters?: {
    P_L: number;
    P_T: number;
    P_G: number;
    P_S: number;
  };
}

interface AdaptiveSession {
  session_id: string;
  student_id: string;
  subject_code: string;
  max_questions: number;
  questions_attempted: number;
  questions_correct: number;
  current_difficulty: string;
  mastery_status: MasteryStatus;
  session_start_time: string;
  estimated_completion_time?: number;
}

interface ExamSession {
  id: string;
  exam_name: string;
  subject_name?: string;
  duration_minutes: number;
  question_count?: number;
  total_questions: number;
  started_at: string;
  ends_at?: string;
  time_remaining_seconds: number;
  current_question_index?: number;
  current_question_number: number;
  questions_answered: number;
  questions_attempted: number;
  auto_submit?: boolean;
  status: "active" | "completed" | "expired";
  // Adaptive learning integration
  adaptive_session?: AdaptiveSession;
  current_question?: AdaptiveQuestion;
  is_adaptive: boolean;
  content_selection?: {
    subject_id?: number;
    selection_type?: string;
    chapter_ids?: number[];
    difficulty_levels?: string[];
    subject_code?: string;
  };
}

interface TimedExamInterfaceProps {
  sessionId: string;
  examName: string;
  onExamComplete: (sessionId: string, results: any) => void;
  onExamExit: () => void;
}

export default function TimedExamInterface({ 
  sessionId, 
  examName, 
  onExamComplete, 
  onExamExit 
}: TimedExamInterfaceProps) {
  const [examSession, setExamSession] = useState<ExamSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AdaptiveQuestion | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [showExitConfirmation, setShowExitConfirmation] = useState(false);
  const [showTimeWarning, setShowTimeWarning] = useState(false);
  const [showAutoSubmitWarning, setShowAutoSubmitWarning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [examExpired, setExamExpired] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  
  const timerInterval = useRef<NodeJS.Timeout | null>(null);
  const warningShown = useRef(false);
  const autoSubmitWarningShown = useRef(false);
  const { user } = useAuth();

  // Fetch exam session details
  const fetchExamSession = useCallback(async () => {
    try {
      console.log("🔄 Fetching exam attempt details for:", sessionId);
      const response = await apiRequest("GET", `http://localhost:8000/api/enhanced-exam/student/attempts/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch exam attempt: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("📚 Exam attempt data received:", data);
      
      if (!data.success || !data.data) {
        throw new Error("Invalid exam attempt data");
      }
      
  const attemptData = data.data;
      
      // Calculate time remaining
      const startTime = attemptData.started_at ? new Date(attemptData.started_at) : new Date();
      const durationMs = attemptData.exam.duration_minutes * 60 * 1000;
      const elapsedMs = Date.now() - startTime.getTime();
      const remainingMs = Math.max(0, durationMs - elapsedMs);
      const remainingSeconds = Math.floor(remainingMs / 1000);
      
      const session: ExamSession = {
        id: attemptData.id,
        exam_name: attemptData.exam.name,
        status: attemptData.status === 'completed' ? 'expired' : 'active',
        time_remaining_seconds: remainingSeconds,
        total_questions: attemptData.exam.total_questions,
        questions_attempted: attemptData.questions_attempted,
        questions_answered: attemptData.questions_answered,
        current_question_number: Math.min(attemptData.questions_attempted + 1, attemptData.exam.total_questions),
        started_at: attemptData.started_at,
        duration_minutes: attemptData.exam.duration_minutes,
        is_adaptive: true, // Enable adaptive learning mode
        subject_name: attemptData.exam.subject || 'General',
        // Persist admin-configured selection so adaptive starter can use it
        content_selection: attemptData.exam.content_selection || attemptData.content_selection || {}
      };
      
      console.log("📝 Processed exam session:", session);
      setExamSession(session);
      setTimeRemaining(remainingSeconds);
      
      if (session.status === "expired" || remainingSeconds <= 0) {
        setExamExpired(true);
        handleAutoSubmit();
      }
    } catch (error) {
      console.error("❌ Error fetching exam session:", error);
      setExamExpired(true);
    }
  }, [sessionId]);

  // Start orchestrated adaptive session using working API
  const startOrchestatedAdaptiveSession = useCallback(async () => {
    try {
      console.log("🧠 Starting adaptive session for exam:", examSession?.exam_name);
      
      // Build payload using scheduled exam's content_selection when available
  const studentId = Number(user?.id) || 1;

      // Prefer explicit subject_code from content_selection if provided
      let subjectCode: string | undefined = undefined;
      if (examSession?.content_selection?.subject_code) {
        subjectCode = examSession.content_selection.subject_code;
      } else if (examSession?.subject_name) {
        // Fallback: normalize subject_name to a simple code (best-effort)
        subjectCode = examSession.subject_name.toLowerCase().replace(/\s+/g, "_");
      }

      const chapterId = Array.isArray(examSession?.content_selection?.chapter_ids) && examSession!.content_selection!.chapter_ids.length > 0
        ? examSession!.content_selection!.chapter_ids[0]
        : undefined;

      const payload: any = {
        student_id: studentId,
        subject_code: subjectCode || "math",
        max_questions: examSession?.total_questions || 10
      };

      if (chapterId) payload.chapter_id = chapterId;
      if (examSession?.content_selection?.difficulty_levels) payload.difficulty_levels = examSession.content_selection.difficulty_levels;

      // Use working adaptive session API instead of problematic orchestrated one
      const sessionResponse = await apiRequest("POST", `http://localhost:8000/adaptive-session/start/`, payload);
      
      if (!sessionResponse.ok) {
        throw new Error("Failed to start adaptive session");
      }
      
      const sessionData = await sessionResponse.json();
      console.log("🎯 Adaptive session started:", sessionData);
      
      if (sessionData.success && sessionData.session_id) {
        // Update exam session with adaptive session data
        setExamSession(prev => prev ? {
          ...prev,
          adaptive_session: {
            session_id: sessionData.session_id,
            student_id: String(studentId),
            subject_code: sessionData.subject_code || "MATH",
            max_questions: sessionData.max_questions || 10,
            questions_attempted: 0,
            questions_correct: 0,
            current_difficulty: "medium",
            mastery_status: {
              current_score: sessionData.session.initial_mastery || 0,
              mastery_achieved: false,
              mastery_level: sessionData.session.mastery_level || "beginner",
              confidence: sessionData.session.confidence || 0.5,
              questions_remaining: sessionData.session.max_questions
            },
            session_start_time: sessionData.session.start_time
          }
        } : null);
        
        return sessionData.session.session_id;
      } else {
        throw new Error("Invalid session response");
      }
      
    } catch (error) {
      console.error("❌ Error starting orchestrated session:", error);
      throw error;
    }
  }, [examSession, user]);

  // Fetch next adaptive question using orchestrated API
  const fetchNextAdaptiveQuestion = useCallback(async () => {
    if (!examSession?.is_adaptive) return;
    
    setIsLoadingQuestion(true);
    try {
      console.log("🧠 Fetching next adaptive question");
      
      // Start adaptive session if not already started
      let sessionId = examSession.adaptive_session?.session_id;
      if (!sessionId) {
        sessionId = await startOrchestatedAdaptiveSession();
      }
      
      // Get next question from adaptive API
      const questionResponse = await apiRequest("GET", `http://localhost:8000/adaptive-session/next-question/${sessionId}/`);
      
      if (!questionResponse.ok) {
        throw new Error("Failed to fetch adaptive question");
      }
      
      const questionData = await questionResponse.json();
      console.log("❓ Adaptive question received:", questionData);
      
      if (questionData.success && questionData.question) {
        const orchestratedQuestion: AdaptiveQuestion = {
          id: questionData.question.id,
          question_text: questionData.question.question_text,
          options: {
            a: questionData.question.options?.[0] || "",
            b: questionData.question.options?.[1] || "",
            c: questionData.question.options?.[2] || "",
            d: questionData.question.options?.[3] || ""
          },
          correct_answer: questionData.question.correct_answer,
          difficulty_level: questionData.question.difficulty_level || questionData.question.difficulty || "medium",
          subject: questionData.question.subject || examSession.subject_name || "General",
          chapter_name: questionData.question.chapter_name || questionData.question.topic,
          knowledge_component: questionData.question.skill_id || questionData.question.knowledge_component,
          explanation: questionData.question.explanation
        };
        
        setCurrentQuestion(orchestratedQuestion);
        setSelectedAnswer("");
        setQuestionStartTime(Date.now());
        
        // Update exam session with current question and orchestration metadata
        setExamSession(prev => prev ? {
          ...prev,
          current_question: orchestratedQuestion,
          adaptive_session: prev.adaptive_session ? {
            ...prev.adaptive_session,
            mastery_status: {
              ...prev.adaptive_session.mastery_status,
              current_score: questionData.orchestration_metadata?.combined_score || prev.adaptive_session.mastery_status.current_score,
              mastery_level: questionData.orchestration_metadata?.mastery_level || prev.adaptive_session.mastery_status.mastery_level,
              confidence: questionData.orchestration_metadata?.confidence || prev.adaptive_session.mastery_status.confidence
            }
          } : prev.adaptive_session
        } : null);
        
        console.log("✅ Orchestrated question loaded successfully");
      } else {
        throw new Error("No question available from adaptive system");
      }
      
    } catch (error) {
      console.error("❌ Error fetching adaptive question:", error);
      // Fallback: Show completion if no more questions
      if (examSession.questions_attempted >= examSession.total_questions) {
        setExamExpired(true);
        handleAutoSubmit();
      }
    } finally {
      setIsLoadingQuestion(false);
    }
  }, [examSession, startOrchestatedAdaptiveSession]);

  // Submit answer to orchestrated system and get next question
  const submitAdaptiveAnswer = useCallback(async (answer: string) => {
    if (!currentQuestion || !examSession?.adaptive_session) return;
    
    setIsSubmitting(true);
    try {
      const responseTime = (Date.now() - questionStartTime) / 1000;
      const isCorrect = answer.toLowerCase() === currentQuestion.correct_answer.toLowerCase();
      
      console.log("📝 Submitting to adaptive system:", {
        question_id: currentQuestion.id,
        answer: answer,
        is_correct: isCorrect,
        response_time: responseTime
      });
      
      // Submit answer to adaptive API
      const submitResponse = await apiRequest("POST", `http://localhost:8000/adaptive-session/submit-answer/`, {
        session_id: examSession.adaptive_session.session_id,
        question_id: currentQuestion.id,
        selected_answer: answer,
        response_time: responseTime,
        is_correct: isCorrect
      });
      
      if (!submitResponse.ok) {
        throw new Error("Failed to submit to adaptive system");
      }
      
      const submitData = await submitResponse.json();
      console.log("🔄 Answer submitted to adaptive system:", submitData);
      
      // Update exam session progress with orchestrated feedback
      setExamSession(prev => prev ? {
        ...prev,
        questions_attempted: prev.questions_attempted + 1,
        questions_answered: isCorrect ? prev.questions_answered + 1 : prev.questions_answered,
        current_question_number: Math.min(prev.questions_attempted + 2, prev.total_questions),
        adaptive_session: prev.adaptive_session ? {
          ...prev.adaptive_session,
          questions_attempted: prev.adaptive_session.questions_attempted + 1,
          questions_correct: isCorrect ? prev.adaptive_session.questions_correct + 1 : prev.adaptive_session.questions_correct,
          mastery_status: {
            current_score: submitData.updated_knowledge?.combined_mastery || prev.adaptive_session.mastery_status.current_score,
            mastery_achieved: submitData.updated_knowledge?.mastery_achieved || prev.adaptive_session.mastery_status.mastery_achieved,
            mastery_level: submitData.updated_knowledge?.mastery_level || prev.adaptive_session.mastery_status.mastery_level,
            confidence: submitData.updated_knowledge?.confidence || prev.adaptive_session.mastery_status.confidence,
            questions_remaining: prev.adaptive_session.mastery_status.questions_remaining - 1,
            bkt_parameters: submitData.updated_knowledge?.bkt_parameters
          }
        } : prev.adaptive_session
      } : null);
      
      // Check if exam is complete
      if (examSession.questions_attempted + 1 >= examSession.total_questions) {
        console.log("🎓 Exam completed - finalizing with orchestration!");
        setExamExpired(true);
        handleAutoSubmit();
      } else {
        // Fetch next orchestrated question
        setTimeout(() => {
          fetchNextAdaptiveQuestion();
        }, 1000); // Small delay to show result
      }
      
    } catch (error) {
      console.error("❌ Error submitting to orchestrated system:", error);
      alert("Failed to submit answer. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }, [currentQuestion, examSession, questionStartTime, timeRemaining, fetchNextAdaptiveQuestion]);

  // Initialize exam session
  useEffect(() => {
    fetchExamSession();
  }, [fetchExamSession]);

  // Load first question when exam session is ready
  useEffect(() => {
    if (examSession && examSession.status === "active" && examSession.is_adaptive && !currentQuestion && !isLoadingQuestion) {
      fetchNextAdaptiveQuestion();
    }
  }, [examSession, currentQuestion, isLoadingQuestion, fetchNextAdaptiveQuestion]);

  // Timer countdown effect
  useEffect(() => {
    if (!examSession || examExpired || examSession.status !== "active") return;

    timerInterval.current = setInterval(() => {
      setTimeRemaining(prev => {
        const newTime = prev - 1;
        
        // Show 5-minute warning
        if (newTime === 300 && !warningShown.current) { // 5 minutes
          setShowTimeWarning(true);
          warningShown.current = true;
        }
        
        // Show 1-minute auto-submit warning
        if (newTime === 60 && !autoSubmitWarningShown.current) { // 1 minute
          setShowAutoSubmitWarning(true);
          autoSubmitWarningShown.current = true;
        }
        
        // Auto-submit when time expires
        if (newTime <= 0) {
          setExamExpired(true);
          handleAutoSubmit();
          return 0;
        }
        
        return newTime;
      });
    }, 1000);

    return () => {
      if (timerInterval.current) {
        clearInterval(timerInterval.current);
      }
    };
  }, [examSession, examExpired]);

  // Handle auto-submit when time expires
  const handleAutoSubmit = useCallback(async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/exams/session/${sessionId}/auto-submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      const result = await response.json();
      onExamComplete(sessionId, result);
    } catch (error) {
      console.error("Error during auto-submit:", error);
    } finally {
      setIsSubmitting(false);
    }
  }, [sessionId, onExamComplete, isSubmitting]);

  // Handle manual exam submission
  const handleManualSubmit = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/exams/session/${sessionId}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      const result = await response.json();
      onExamComplete(sessionId, result);
    } catch (error) {
      console.error("Error submitting exam:", error);
      alert("Failed to submit exam. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle early exit with confirmation
  const handleEarlyExit = () => {
    setShowExitConfirmation(true);
  };

  const confirmExit = () => {
    onExamExit();
  };

  // Format time display
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // Get timer color based on remaining time
  const getTimerColor = (seconds: number) => {
    if (seconds <= 60) return "text-red-600"; // Last minute - red
    if (seconds <= 300) return "text-orange-600"; // Last 5 minutes - orange
    return "text-green-600"; // More than 5 minutes - green
  };

  // Get difficulty level color
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'very_easy':
      case 'easy':
        return "bg-green-600";
      case 'medium':
      case 'moderate':
        return "bg-blue-600";
      case 'hard':
      case 'difficult':
        return "bg-orange-600";
      case 'very_hard':
        return "bg-red-600";
      default:
        return "bg-gray-600";
    }
  };

  // Calculate progress percentage
  const getProgressPercentage = () => {
    if (!examSession) return 0;
    const totalTime = examSession.duration_minutes * 60;
    const elapsed = totalTime - timeRemaining;
    return (elapsed / totalTime) * 100;
  };

  if (!examSession) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Timer className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-spin" />
          <p className="text-lg text-muted-foreground">Loading exam...</p>
        </div>
      </div>
    );
  }

  if (examExpired) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-red-600" />
            <CardTitle className="text-red-600">Exam Time Expired</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-muted-foreground">
              Your exam time has ended and your answers have been automatically submitted.
            </p>
            <div className="space-y-2">
              <div className="text-sm">
                <strong>Exam:</strong> {examSession.exam_name}
              </div>
              <div className="text-sm">
                <strong>Duration:</strong> {examSession.duration_minutes} minutes
              </div>
            </div>
            {isSubmitting ? (
              <Button disabled className="w-full">
                <Timer className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </Button>
            ) : (
              <Button onClick={() => onExamExit()} className="w-full">
                <CheckCircle2 className="h-4 w-4 mr-2" />
                View Results
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Exam Header with Timer */}
      <div className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-xl font-bold text-foreground">{examSession.exam_name}</h1>
              <p className="text-sm text-muted-foreground">
                {examSession.subject_name || 'General'} • {examSession.total_questions} questions
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Question Progress */}
            <div className="text-sm text-muted-foreground">
              Question {examSession.current_question_number} of {examSession.total_questions}
            </div>

            {/* Time Remaining */}
            <div className="flex items-center space-x-2">
              <Clock className={`h-5 w-5 ${getTimerColor(timeRemaining)}`} />
              <div className={`text-lg font-mono font-bold ${getTimerColor(timeRemaining)}`}>
                {formatTime(timeRemaining)}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleEarlyExit}
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Exit Exam
              </Button>
              
              <Button
                onClick={handleManualSubmit}
                disabled={isSubmitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSubmitting ? (
                  <>
                    <Timer className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Submit Exam
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-4 pb-2">
          <Progress 
            value={getProgressPercentage()} 
            className="h-2"
          />
        </div>
      </div>

      {/* Main Exam Content */}
      <div className="p-4">
        {isLoadingQuestion ? (
          <Card>
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <Brain className="h-12 w-12 mx-auto text-blue-600 animate-pulse" />
                <div>
                  <h3 className="text-lg font-semibold">Loading Next Question...</h3>
                  <p className="text-muted-foreground">
                    Adaptive BKT system is selecting your optimal next question
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : currentQuestion ? (
          <div className="space-y-6">
            {/* Question Header */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary">
                      Question {examSession.current_question_number} of {examSession.total_questions}
                    </Badge>
                    <Badge className={`${getDifficultyColor(currentQuestion.difficulty_level)} text-white`}>
                      {currentQuestion.difficulty_level}
                    </Badge>
                    {currentQuestion.chapter_name && (
                      <Badge variant="outline">
                        {currentQuestion.chapter_name}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Brain className="h-4 w-4 text-blue-600" />
                    <span className="text-sm text-muted-foreground">Adaptive BKT</span>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Question Content */}
            <Card>
              <CardContent className="p-6">
                <div className="space-y-6">
                  {/* Question Text */}
                  <div>
                    <h2 className="text-xl font-semibold text-foreground mb-4">
                      {currentQuestion.question_text}
                    </h2>
                  </div>

                  {/* Answer Options */}
                  <div className="space-y-3">
                    {Object.entries(currentQuestion.options).map(([key, value]) => (
                      <div key={key} className="flex items-center space-x-3">
                        <input
                          type="radio"
                          id={`option-${key}`}
                          name="answer"
                          value={key}
                          checked={selectedAnswer === key}
                          onChange={(e) => setSelectedAnswer(e.target.value)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <label 
                          htmlFor={`option-${key}`}
                          className="flex-1 text-foreground cursor-pointer hover:bg-gray-50 p-3 rounded-lg transition-colors"
                        >
                          <span className="font-medium mr-2">({key.toUpperCase()})</span>
                          {value}
                        </label>
                      </div>
                    ))}
                  </div>

                  {/* Submit Answer Button */}
                  <div className="flex justify-between items-center pt-4">
                    <div className="text-sm text-muted-foreground">
                      {examSession.adaptive_session && (
                        <div className="flex items-center space-x-6">
                          <span>Accuracy: {Math.round((examSession.adaptive_session.questions_correct / Math.max(examSession.adaptive_session.questions_attempted, 1)) * 100)}%</span>
                          <span>Mastery: {examSession.adaptive_session.mastery_status.mastery_level}</span>
                          <span>Confidence: {Math.round(examSession.adaptive_session.mastery_status.confidence * 100)}%</span>
                          {examSession.adaptive_session.mastery_status.bkt_parameters && (
                            <span className="text-xs bg-blue-100 px-2 py-1 rounded">
                              BKT: {Math.round(examSession.adaptive_session.mastery_status.bkt_parameters.P_L * 100)}%
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <Button
                      onClick={() => selectedAnswer && submitAdaptiveAnswer(selectedAnswer)}
                      disabled={!selectedAnswer || isSubmitting}
                      className="bg-blue-600 hover:bg-blue-700 px-8"
                    >
                      {isSubmitting ? (
                        <>
                          <Timer className="h-4 w-4 mr-2 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <ArrowRight className="h-4 w-4 mr-2" />
                          Submit Answer
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Mastery Progress */}
            {examSession.adaptive_session && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-sm">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Orchestrated Learning Progress (BKT+DKT)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {examSession.adaptive_session.questions_attempted}
                      </div>
                      <div className="text-xs text-muted-foreground">Attempted</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {examSession.adaptive_session.questions_correct}
                      </div>
                      <div className="text-xs text-muted-foreground">Correct</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {Math.round(examSession.adaptive_session.mastery_status.current_score * 100)}%
                      </div>
                      <div className="text-xs text-muted-foreground">Mastery</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${examSession.adaptive_session.mastery_status.mastery_achieved ? 'text-green-600' : 'text-gray-600'}`}>
                        {examSession.adaptive_session.mastery_status.mastery_level}
                      </div>
                      <div className="text-xs text-muted-foreground">Level</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <Card>
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground" />
                <div>
                  <h3 className="text-lg font-semibold">Initializing Orchestrated Assessment</h3>
                  <p className="text-muted-foreground">
                    Setting up your personalized exam with adaptive BKT learning...
                  </p>
                </div>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p><strong>Session ID:</strong> {sessionId}</p>
                  <p><strong>Time Remaining:</strong> {formatTime(timeRemaining)}</p>
                  <p><strong>Status:</strong> {examSession.status}</p>
                  <p><strong>Adaptive Mode:</strong> {examSession.is_adaptive ? 'Orchestrated Enabled' : 'Disabled'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Exit Confirmation Dialog */}
      <Dialog open={showExitConfirmation} onOpenChange={setShowExitConfirmation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Confirm Exit Exam
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to exit the exam? Your current progress will be saved, but you may not be able to return to continue the exam.
            </DialogDescription>
          </DialogHeader>
          
          <div className="bg-yellow-50 p-4 rounded-md">
            <div className="flex items-start gap-3">
              <Flag className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-yellow-800">Important:</p>
                <ul className="mt-1 text-yellow-700 space-y-1">
                  <li>• Your answers so far will be automatically submitted</li>
                  <li>• You will not be able to return to this exam</li>
                  <li>• Time remaining: {formatTime(timeRemaining)}</li>
                  <li>• Questions answered: {examSession.questions_answered} of {examSession.total_questions}</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowExitConfirmation(false)}
            >
              Cancel - Continue Exam
            </Button>
            <Button
              variant="destructive"
              onClick={confirmExit}
              className="bg-red-600 hover:bg-red-700"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Exit and Submit
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Time Warning Dialog */}
      <Dialog open={showTimeWarning} onOpenChange={setShowTimeWarning}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-orange-600">
              <Clock className="h-5 w-5" />
              Time Warning
            </DialogTitle>
            <DialogDescription>
              You have 5 minutes remaining in this exam. Please review your answers and prepare to submit.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => setShowTimeWarning(false)}>
              Continue Exam
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Auto-Submit Warning Dialog */}
      <Dialog open={showAutoSubmitWarning} onOpenChange={setShowAutoSubmitWarning}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Final Warning
            </DialogTitle>
            <DialogDescription>
              Your exam will automatically submit in 1 minute. Please finalize your answers now.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button 
              onClick={() => setShowAutoSubmitWarning(false)}
              className="bg-orange-600 hover:bg-orange-700"
            >
              I Understand
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}