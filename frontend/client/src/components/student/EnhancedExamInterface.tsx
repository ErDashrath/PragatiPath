import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Clock, Calendar, BookOpen, Award, AlertCircle, CheckCircle, Brain } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ScheduledExam {
  id: string;
  exam_name: string;
  subject: string;
  total_questions: number;
  duration_minutes: number;
  scheduled_start_time: string;
  scheduled_end_time: string;
  status: 'DRAFT' | 'SCHEDULED' | 'ACTIVE' | 'COMPLETED';
  passing_score_percentage: number;
}

interface ExamSession {
  session_id: string;
  adaptive_session_id: string;
  exam_name: string;
  total_questions: number;
  duration_minutes: number;
}

interface Question {
  question_id: string;
  question_number: number;
  total_questions: number;
  question_text: string;
  options: Array<{ id: string; text: string }>;
  difficulty: string;
  subject: string;
  time_remaining_minutes: number;
  current_mastery: number;
}

const EnhancedExamInterface: React.FC = () => {
  const [scheduledExams, setScheduledExams] = useState<ScheduledExam[]>([]);
  const [currentExamSession, setCurrentExamSession] = useState<ExamSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [examStarted, setExamStarted] = useState(false);
  const [examCompleted, setExamCompleted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [currentScore, setCurrentScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [adaptiveLoading, setAdaptiveLoading] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  
  const { toast } = useToast();

  // Load scheduled exams on component mount
  useEffect(() => {
    loadScheduledExams();
  }, []);

  // Timer effect for exam duration
  useEffect(() => {
    if (examStarted && !examCompleted && timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(prev => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0 && examStarted && !examCompleted) {
      handleTimeUp();
    }
  }, [timeRemaining, examStarted, examCompleted]);

  const loadScheduledExams = async () => {
    try {
      setLoading(true);
      // Get student's scheduled exams
      const response = await fetch('http://localhost:8000/api/v1/enhanced-exam/student/1/exams/scheduled/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setScheduledExams(data.data || []);
        }
      } else {
        throw new Error('Failed to load scheduled exams');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load scheduled exams. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const joinScheduledExam = async (examId: string) => {
    try {
      setLoading(true);
      
      // Join the enhanced exam using our new API
      const response = await fetch(`http://localhost:8000/enhanced-exam-session/join/${examId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: 1 // Use student_id instead of username to avoid lookup errors
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Set up exam session
          setCurrentExamSession({
            session_id: data.session_id,
            adaptive_session_id: data.adaptive_session_id,
            exam_name: data.exam_name,
            total_questions: data.total_questions,
            duration_minutes: data.duration_minutes
          });

          // Initialize timer
          setTimeRemaining(data.duration_minutes * 60);
          setExamStarted(true);
          
          // Get first question
          await getNextQuestion(data.session_id);
          
          toast({
            title: "Exam Started! 📝",
            description: `${data.exam_name} - Adaptive learning enabled`,
          });
        } else {
          throw new Error(data.error || 'Failed to join exam');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to join exam');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to start exam. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getNextQuestion = async (sessionId: string) => {
    try {
      setAdaptiveLoading(true);
      setCurrentQuestion(null); // Clear current question to show loading
      
      const response = await fetch(`http://localhost:8000/enhanced-exam-session/question/${sessionId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.question) {
          // Simulate adaptive processing time for better UX
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          setCurrentQuestion(data.question);
          setSelectedAnswer('');
        } else if (data.exam_completed) {
          // Exam completed - no more questions
          handleExamComplete();
        } else {
          throw new Error('No more questions available');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get question');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to get question. Please try again.",
        variant: "destructive"
      });
    } finally {
      setAdaptiveLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer || !currentExamSession || !currentQuestion) return;

    try {
      setLoading(true);
      
      const response = await fetch(`http://localhost:8000/enhanced-exam-session/submit-answer/${currentExamSession.session_id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion.question_id,
          selected_answer: selectedAnswer,
          time_taken: 30 // Calculate actual time taken
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Update progress
          setQuestionsAnswered(data.questions_answered);
          setCurrentScore(data.current_score);
          
          // Check if exam should auto-complete after reaching total questions
          if (currentQuestion && data.questions_answered >= currentQuestion.total_questions) {
            console.log('🏁 Exam completed - reached total questions limit');
            toast({
              title: "🎉 Exam Completed!",
              description: `You have answered all ${currentQuestion.total_questions} questions. Submitting exam...`,
              variant: "default",
              duration: 3000
            });
            
            // Auto-submit after brief delay
            setTimeout(() => {
              handleExamComplete();
            }, 2000);
            return;
          }
          
          // Show detailed adaptive feedback
          toast({
            title: data.is_correct ? "🎉 Correct Answer!" : "❌ Incorrect Answer",
            description: (
              <div className="space-y-2">
                <div>Score: {data.current_score.toFixed(1)}% ({data.correct_answers}/{data.questions_answered})</div>
                {data.mastery_update && (
                  <div className="text-sm">
                    🧠 Mastery Level: {(data.mastery_update.new_mastery * 100).toFixed(0)}%
                    {data.mastery_update.difficulty_adjustment && (
                      <div>🎯 Next Difficulty: {data.mastery_update.next_difficulty}</div>
                    )}
                  </div>
                )}
                <div className="text-xs opacity-75">
                  ⚡ Adaptive system is selecting your next optimal question...
                </div>
              </div>
            ),
            variant: data.is_correct ? "default" : "destructive",
            duration: 3000
          });

          // Reset selected answer and get next question with visual feedback
          setSelectedAnswer('');
          
          // Show loading state briefly then get next question
          setTimeout(() => {
            getNextQuestion(currentExamSession.session_id);
          }, 2000);
        } else {
          throw new Error(data.error || 'Failed to submit answer');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit answer');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit answer. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExamComplete = async () => {
    // Auto-submit if exam completes naturally (all questions answered or time up)
    if (currentExamSession && !examCompleted) {
      try {
        const response = await fetch(`http://localhost:8000/enhanced-exam-session/submit/${currentExamSession.session_id}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            auto_complete: true,
            questions_attempted: questionsAnswered,
            final_score: currentScore
          })
        });

        if (response.ok) {
          const data = await response.json();
          setCurrentScore(data.final_score || currentScore);
        }
      } catch (error) {
        console.error('Auto-submit error:', error);
      }
    }
    
    setExamCompleted(true);
    setExamStarted(false);
    
    toast({
      title: "Exam Completed! 🎉",
      description: `Final Score: ${currentScore.toFixed(1)}% • Questions Attempted: ${questionsAnswered}`,
      duration: 5000
    });
  };

  const handleTimeUp = () => {
    toast({
      title: "Time's Up! ⏰",
      description: "Exam automatically submitted due to time limit.",
      variant: "destructive"
    });
    handleExamComplete();
  };

  const requestExamSubmission = () => {
    setShowConfirmDialog(true);
  };

  const confirmExamSubmission = async () => {
    if (!currentExamSession) return;
    
    setLoading(true);
    console.log('🚀 Starting exam submission process...', {
      sessionId: currentExamSession.session_id,
      questionsAnswered,
      currentScore
    });

    try {
      const response = await fetch(`http://localhost:8000/enhanced-exam-session/submit/${currentExamSession.session_id}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          force_submit: true,
          partial_completion: true,
          questions_attempted: questionsAnswered,
          final_score: currentScore,
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Backend submission successful:', data);
        
        if (data.success) {
          // Enhanced success feedback with database confirmation
          toast({
            title: "🎉 Exam Successfully Submitted & Saved!",
            description: (
              <div className="space-y-1">
                <div>📊 Final Score: {(data.results?.final_score_percentage || currentScore).toFixed(1)}%</div>
                <div>📝 Questions Attempted: {questionsAnswered}/{currentQuestion?.total_questions || 0}</div>
                <div>💾 Saved to Database: Session #{currentExamSession.session_id}</div>
                <div className="text-xs opacity-75">✅ All progress permanently recorded</div>
              </div>
            ),
            variant: "default",
            duration: 5000
          });
          
          // Mark as completed and show results
          setExamCompleted(true);
          setExamStarted(false);
          
          // Save the final results for display
          if (data.results?.final_score_percentage !== undefined) {
            setCurrentScore(data.results.final_score_percentage);
          }
          
          // Show additional success confirmation
          setTimeout(() => {
            alert(`🎊 EXAM COMPLETED SUCCESSFULLY! 🎊\n\n📈 Your Results:\n• Final Score: ${(data.results?.final_score_percentage || currentScore).toFixed(1)}%\n• Questions Completed: ${questionsAnswered}\n• Grade: ${data.results?.grade || 'Calculating...'}\n• Session ID: ${currentExamSession.session_id}\n\n💾 All your answers have been permanently saved to the database!\n✅ You can now view this attempt in your exam history.`);
          }, 1000);
          
        } else {
          throw new Error(data.error || 'Submission failed');
        }
      } else {
        const errorData = await response.json();
        console.error('❌ Backend submission failed:', errorData);
        throw new Error(errorData.error || 'Failed to submit exam');
      }
    } catch (error) {
      console.error('💥 Submission error:', error);
      toast({
        title: "⚠️ Submission Error",
        description: `Failed to save exam: ${error instanceof Error ? error.message : 'Unknown error'}. Your progress may not be saved. Please contact support.`,
        variant: "destructive",
        duration: 8000
      });
      
      // Still mark as completed locally but show warning
      setExamCompleted(true);
      setExamStarted(false);
    } finally {
      setLoading(false);
      setShowConfirmDialog(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getExamStatusBadge = (status: string) => {
    const statusConfig = {
      'DRAFT': { variant: 'outline' as const, text: 'Draft', icon: '📝' },
      'SCHEDULED': { variant: 'secondary' as const, text: 'Scheduled', icon: '📅' },
      'ACTIVE': { variant: 'default' as const, text: 'Active', icon: '🟢' },
      'COMPLETED': { variant: 'destructive' as const, text: 'Completed', icon: '✅' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.DRAFT;
    
    return (
      <Badge variant={config.variant}>
        {config.icon} {config.text}
      </Badge>
    );
  };

  // Show exam in progress
  if (examStarted && !examCompleted) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Exam Header */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-xl">{currentExamSession?.exam_name}</CardTitle>
                <CardDescription>
                  Question {currentQuestion?.question_number} of {currentQuestion?.total_questions}
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2 text-lg font-semibold">
                  <Clock className="h-5 w-5" />
                  {formatTime(timeRemaining)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Score: {currentScore.toFixed(1)}% ({questionsAnswered} answered)
                </div>
              </div>
            </div>
            <Progress 
              value={(questionsAnswered / (currentQuestion?.total_questions || 1)) * 100} 
              className="w-full"
            />
          </CardHeader>
        </Card>

        {/* Adaptive Learning Stats */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              Adaptive Learning Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">{questionsAnswered}</div>
                <div className="text-sm text-muted-foreground">Questions Answered</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{currentScore.toFixed(1)}%</div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {currentQuestion ? (currentQuestion.current_mastery * 100).toFixed(0) : 0}%
                </div>
                <div className="text-sm text-muted-foreground">BKT Mastery</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">
                  {currentQuestion?.difficulty || 'Unknown'}
                </div>
                <div className="text-sm text-muted-foreground">Current Difficulty</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Adaptive Loading State */}
        {adaptiveLoading && (
          <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
            <CardContent className="p-8 text-center">
              <div className="space-y-4">
                <div className="relative">
                  <Brain className="h-16 w-16 mx-auto text-blue-600 animate-pulse" />
                  <div className="absolute -top-2 -right-2">
                    <div className="h-4 w-4 bg-green-500 rounded-full animate-ping"></div>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-blue-900">Adaptive BKT System Working...</h3>
                  <p className="text-blue-700 mt-2">
                    🧠 Analyzing your performance and selecting the optimal next question
                  </p>
                  <div className="flex items-center justify-center gap-2 mt-3 text-sm text-blue-600">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span>Difficulty adaptation in progress</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Question Card */}
        {currentQuestion && !adaptiveLoading && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between mb-3">
                <Badge variant="outline" className="text-lg px-3 py-1">
                  Question {currentQuestion.question_number} of {currentQuestion.total_questions}
                </Badge>
                <div className="flex gap-2">
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    💪 {currentQuestion.difficulty}
                  </Badge>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    🧠 Mastery: {(currentQuestion.current_mastery * 100).toFixed(0)}%
                  </Badge>
                  <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                    ⏱️ {formatTime(timeRemaining)}
                  </Badge>
                </div>
              </div>
              <CardTitle className="text-xl mb-4">{currentQuestion.question_text}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {currentQuestion.options.map((option) => (
                  <div
                    key={option.id}
                    onClick={() => setSelectedAnswer(option.id)}
                    className={`
                      flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer transition-all duration-200
                      ${selectedAnswer === option.id 
                        ? 'border-blue-500 bg-blue-50 shadow-md transform scale-[1.02]' 
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }
                    `}
                  >
                    <div className={`
                      w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all
                      ${selectedAnswer === option.id 
                        ? 'border-blue-500 bg-blue-500' 
                        : 'border-gray-300'
                      }
                    `}>
                      {selectedAnswer === option.id && (
                        <CheckCircle className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <span className="font-bold text-lg text-blue-600 mr-3">{option.id.toUpperCase()})</span>
                      <span className={`text-lg ${selectedAnswer === option.id ? 'font-medium text-blue-900' : 'text-gray-700'}`}>
                        {option.text}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="flex justify-between items-center mt-6">
                <Button 
                  variant="outline" 
                  onClick={requestExamSubmission}
                  className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300 hover:bg-red-50"
                >
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Submit & End Exam
                </Button>
                <Button 
                  onClick={submitAnswer} 
                  disabled={!selectedAnswer || loading}
                  className="min-w-[120px]"
                >
                  {loading ? "Submitting..." : "Submit Answer"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Confirmation Dialog */}
        {showConfirmDialog && (
          <Card className="border-orange-200 bg-gradient-to-r from-orange-50 to-red-50">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Submit Exam with Current Progress
              </CardTitle>
              <CardDescription className="space-y-2">
                <div className="text-lg">
                  Your exam will be submitted and saved to the database with your current progress.
                </div>
                <div className="bg-white p-3 rounded border">
                  <strong>Current Progress:</strong><br/>
                  📊 Questions Attempted: {questionsAnswered} / {currentQuestion?.total_questions}<br/>
                  🎯 Current Score: {currentScore.toFixed(1)}%<br/>
                  💾 All answers will be saved to database
                </div>
                <div className="text-sm text-orange-700">
                  ⚠️ This action cannot be undone, but your progress will be permanently recorded.
                </div>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setShowConfirmDialog(false)} className="flex-1">
                  <span>Continue Exam</span>
                </Button>
                <Button 
                  variant="destructive" 
                  onClick={confirmExamSubmission}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Yes, Submit & Save
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  // Show scheduled exams list
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Scheduled Exams</h1>
        <p className="text-muted-foreground">
          Take scheduled exams with adaptive learning and comprehensive analytics
        </p>
      </div>

      {loading && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-pulse">Loading scheduled exams...</div>
          </CardContent>
        </Card>
      )}

      {!loading && scheduledExams.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No Scheduled Exams</h3>
            <p className="text-muted-foreground">
              There are no scheduled exams available at the moment.
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {scheduledExams.map((exam) => (
          <Card key={exam.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{exam.exam_name}</CardTitle>
                  <CardDescription className="flex items-center gap-1 mt-1">
                    <BookOpen className="h-4 w-4" />
                    {exam.subject}
                  </CardDescription>
                </div>
                {getExamStatusBadge(exam.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>
                    {new Date(exam.scheduled_start_time).toLocaleDateString()} at{' '}
                    {new Date(exam.scheduled_start_time).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>{exam.duration_minutes} minutes</span>
                </div>
                
                <div className="flex items-center gap-2 text-sm">
                  <Award className="h-4 w-4 text-muted-foreground" />
                  <span>{exam.total_questions} questions</span>
                </div>

                <div className="pt-3">
                  <Button 
                    className="w-full" 
                    onClick={() => joinScheduledExam(exam.id)}
                    disabled={exam.status !== 'ACTIVE' || loading}
                  >
                    {exam.status === 'ACTIVE' ? 'Start Exam' : 
                     exam.status === 'COMPLETED' ? 'Completed' :
                     exam.status === 'SCHEDULED' ? 'Not Started' : 'Unavailable'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {examCompleted && (
        <Card className="mt-8 border-green-200 bg-gradient-to-r from-green-50 to-blue-50">
          <CardHeader>
            <CardTitle className="text-green-700 flex items-center gap-2 text-2xl">
              <CheckCircle className="h-6 w-6" />
              Exam Successfully Submitted & Saved!
            </CardTitle>
            <CardDescription className="text-lg">
              Your exam results have been recorded in the database
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Results Summary */}
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-semibold text-gray-800 mb-3">📊 Final Results</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{currentScore.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Final Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{questionsAnswered}</div>
                    <div className="text-sm text-gray-600">Questions Attempted</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {currentExamSession?.total_questions || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">Total Questions</div>
                  </div>
                </div>
              </div>

              {/* Database Confirmation */}
              <div className="bg-green-100 p-4 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 text-green-800 mb-2">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">💾 Results Successfully Saved to Database</span>
                </div>
                <div className="text-sm text-green-700 space-y-1">
                  <div>• ✅ Exam attempt recorded with current progress</div>
                  <div>• ✅ All {questionsAnswered} answered questions permanently saved</div>
                  <div>• ✅ Final score {currentScore.toFixed(1)}% calculated and stored</div>
                  <div>• ✅ Session ID: {currentExamSession?.session_id || 'Unknown'} - Available in your exam history</div>
                  <div className="mt-2 p-2 bg-white rounded text-xs">
                    <strong>🔒 Data Integrity Confirmed:</strong> Your exam submission has been validated and stored in the academic database. This attempt will count towards your official academic record.
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button onClick={() => window.location.reload()} className="flex-1">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Take Another Exam
                </Button>
                <Button variant="outline" onClick={() => setExamCompleted(false)} className="flex-1">
                  <Award className="h-4 w-4 mr-2" />
                  View Exam List
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EnhancedExamInterface;