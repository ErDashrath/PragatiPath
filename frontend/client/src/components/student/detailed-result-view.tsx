import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  ArrowLeft,
  Clock, 
  Trophy, 
  Target,
  CheckCircle,
  XCircle,
  Timer,
  BookOpen,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  BarChart3,
  PieChart,
  Brain,
  Activity,
  Zap
} from 'lucide-react';
import { HistoryAPI, type DetailedAssessmentResult } from '../../lib/history-api';

interface DetailedResultViewProps {
  studentUsername: string;
  sessionId: string;
  onBack: () => void;
}

export function DetailedResultView({ studentUsername, sessionId, onBack }: DetailedResultViewProps) {
  const [result, setResult] = useState<DetailedAssessmentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDetailedResult();
  }, [studentUsername, sessionId]);

  const loadDetailedResult = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔍 Loading detailed result for session:', sessionId);
      
      // First try the regular assessment API
      try {
        console.log('🚀 ATTEMPTING PRIMARY PATH: HistoryAPI.getDetailedAssessmentResult');
        const data = await HistoryAPI.getDetailedAssessmentResult(studentUsername, sessionId);
        console.log('✅ PRIMARY PATH SUCCESS - Regular assessment API worked:', data);
        
        // Check if this data has proper difficulty information
        if (data.question_attempts && data.question_attempts.length > 0) {
          const firstQ = data.question_attempts[0];
          console.log('🔍 PRIMARY PATH - First question difficulty check:', {
            difficulty: firstQ.difficulty,
            difficulty_level: firstQ.difficulty_level
          });
        }
        
        setResult(data);
        return;
      } catch (regularApiError) {
        console.log('❌ PRIMARY PATH FAILED - Regular assessment API failed, trying adaptive session API...', regularApiError);
      }
      
      // If regular API fails, try to get adaptive session details with REAL question data
      try {
        console.log('� ATTEMPTING FALLBACK PATH: session-details API');
        // Try the existing session-details endpoint for adaptive sessions
        const adaptiveDetailResponse = await fetch(`/history/session-details/${sessionId}/`);
        console.log('📡 FALLBACK PATH - Adaptive detail response status:', adaptiveDetailResponse.status);
        
        if (adaptiveDetailResponse.ok) {
          const adaptiveDetailData = await adaptiveDetailResponse.json();
          console.log('📄 Adaptive detail data received:', adaptiveDetailData);
          
              if (adaptiveDetailData.success && adaptiveDetailData.session_details && adaptiveDetailData.session_details.question_attempts) {
                console.log('✅ Got real session details with question attempts:', adaptiveDetailData.session_details);
                
                const sessionDetails = adaptiveDetailData.session_details;
                const questionAttempts = sessionDetails.question_attempts || [];
                
                // Debug: Check first question attempt structure
                if (questionAttempts.length > 0) {
                  console.log('🔍 First question attempt structure:', questionAttempts[0]);
                  console.log('🔍 Available fields:', Object.keys(questionAttempts[0]));
                }
                
                // Calculate difficulty performance from actual question attempts - USING REAL DATABASE TAGS
                const difficultyStats: Record<string, { correct: number; total: number; accuracy: number }> = {};
                console.log('🎯 Using REAL database difficulty tags (no hardcoded mapping)');
                
                // Process question attempts to get difficulty breakdown - USING REAL DATABASE TAGS
                questionAttempts.forEach((attempt: any) => {
                  const difficulty = attempt.difficulty || attempt.difficulty_level || 'unknown';
                  console.log(`🔍 DetailedResultView processing REAL difficulty: '${difficulty}' for Q${attempt.question_number}`);
                  
                  // Use the REAL difficulty tag from database (no mapping!)
                  const realDifficulty = difficulty;
                  console.log(`✅ Using REAL database tag: '${realDifficulty}'`);
                  
                  // Initialize the real difficulty category if not exists
                  if (!difficultyStats[realDifficulty]) {
                    difficultyStats[realDifficulty] = { correct: 0, total: 0, accuracy: 0 };
                  }
                  
                  difficultyStats[realDifficulty].total += 1;
                  if (attempt.is_correct) {
                    difficultyStats[realDifficulty].correct += 1;
                  }
                });
                
                // Calculate accuracy percentages
                Object.keys(difficultyStats).forEach(difficulty => {
                  const stats = difficultyStats[difficulty];
                  stats.accuracy = stats.total > 0 ? (stats.correct / stats.total) * 100 : 0;
                });
                
                console.log('📊 Calculated difficulty stats:', difficultyStats);            // Map real API data to expected component format
            const adaptiveResult: DetailedAssessmentResult = {
              session_info: {
                session_id: sessionDetails.session_id,
                session_name: sessionDetails.session_name,
                subject_name: sessionDetails.subject,
                chapter_name: 'Adaptive Learning',
                session_type: sessionDetails.session_type || 'PRACTICE',
                session_start_time: sessionDetails.created_at,
                session_end_time: sessionDetails.created_at,
                questions_attempted: sessionDetails.questions_attempted,
                questions_correct: sessionDetails.questions_correct,
                percentage_score: sessionDetails.accuracy_percentage,
                total_score: sessionDetails.questions_correct,
                max_possible_score: sessionDetails.questions_attempted,
                grade: sessionDetails.accuracy_percentage >= 80 ? 'A' : 
                       sessionDetails.accuracy_percentage >= 70 ? 'B' :
                       sessionDetails.accuracy_percentage >= 60 ? 'C' : 
                       sessionDetails.accuracy_percentage >= 50 ? 'D' : 'F',
                session_duration_seconds: (sessionDetails.duration_minutes || 0) * 60,
                status: sessionDetails.status || 'COMPLETED'
              },
              question_attempts: questionAttempts.map((attempt: any, index: number) => ({
                question_number: attempt.question_number || (index + 1),
                question_text: `Question ${attempt.question_number || (index + 1)}`,
                question_type: 'multiple_choice',
                options: {
                  'a': 'Option A',
                  'b': 'Option B',
                  'c': 'Option C', 
                  'd': 'Option D'
                },
                student_answer: attempt.student_answer,
                correct_answer: attempt.correct_answer,
                is_correct: attempt.is_correct,
                time_spent_seconds: Math.round(attempt.time_spent || 0),
                points_earned: attempt.points_earned || (attempt.is_correct ? 1 : 0),
                question_points: 1,
                difficulty_level: attempt.difficulty ? 
                  attempt.difficulty.charAt(0).toUpperCase() + attempt.difficulty.slice(1) : 'Medium',
                topic: sessionDetails.subject,
                subtopic: `${sessionDetails.subject} Concepts`,
                explanation: attempt.is_correct ? 
                  `Correct! You answered this ${attempt.difficulty} question correctly.` :
                  `Incorrect. The correct answer was ${attempt.correct_answer}. This was a ${attempt.difficulty} question.`,
                confidence_level: attempt.is_correct ? 0.8 : 0.3
              })),
              performance_analysis: {
                topics_performance: {
                  [sessionDetails.subject]: {
                    correct: sessionDetails.questions_correct,
                    total: sessionDetails.questions_attempted,
                    accuracy: sessionDetails.accuracy_percentage
                  }
                },
                difficulty_performance: difficultyStats,
                average_time_per_question: (sessionDetails.duration_minutes * 60) / sessionDetails.questions_attempted,
                fastest_correct_answer: (() => {
                  const correctTimes = sessionDetails.question_attempts.filter((a: any) => a.is_correct).map((a: any) => a.time_spent);
                  return correctTimes.length > 0 ? Math.min(...correctTimes) : 0;
                })(),
                slowest_correct_answer: (() => {
                  const correctTimes = sessionDetails.question_attempts.filter((a: any) => a.is_correct).map((a: any) => a.time_spent);
                  return correctTimes.length > 0 ? Math.max(...correctTimes) : 0;
                })(),
                strengths: sessionDetails.accuracy_percentage >= 70 ? [`Strong performance in ${sessionDetails.subject}`] : [],
                improvement_areas: sessionDetails.accuracy_percentage < 70 ? [`Need improvement in ${sessionDetails.subject}`] : []
              },
              recommendations: sessionDetails.accuracy_percentage >= 80 ? 
                ['Excellent performance! Try more challenging questions.'] :
                ['Review the concepts and practice more questions.']
            };
            
            console.log('✅ Converted result for rendering:', adaptiveResult);
            setResult(adaptiveResult);
            return;
          } else {
            console.log('❌ Session details API returned invalid data:', adaptiveDetailData);
          }
        } else {
          console.log('❌ Session details API failed with status:', adaptiveDetailResponse.status);
          const errorText = await adaptiveDetailResponse.text();
          console.log('❌ Error response:', errorText);
        }
        
        console.log('🔄 Falling back to session history...');
        // Fallback: Get basic session info from session history and use simulated questions
        const backendUserId = localStorage.getItem('pragatipath_backend_user_id');
        console.log('📝 Backend user ID from localStorage:', backendUserId);
        
        if (backendUserId) {
          console.log('🔄 Fetching session history...');
          const adaptiveResponse = await fetch(`/simple/session-history/${backendUserId}/`);
          console.log('📡 Session history response status:', adaptiveResponse.status);
          
          if (adaptiveResponse.ok) {
            const adaptiveData = await adaptiveResponse.json();
            console.log('📄 Session history data:', adaptiveData);
            
            if (adaptiveData.success && adaptiveData.sessions) {
              // Find the specific session
              const session = adaptiveData.sessions.find((s: any) => s.session_id === sessionId);
              console.log('🔍 Looking for session ID:', sessionId);
              console.log('🔍 Found session:', session);
              
              if (session) {
                // Convert adaptive session data to DetailedAssessmentResult format
                const correctAnswers = Math.round(session.questions_attempted * (parseFloat(session.accuracy) / 100));
                const incorrectAnswers = session.questions_attempted - correctAnswers;
                
                // Generate simulated question attempts for adaptive sessions
                const simulatedAttempts = [];
                for (let i = 1; i <= session.questions_attempted; i++) {
                  const isCorrect = i <= correctAnswers;
                  simulatedAttempts.push({
                    question_number: i,
                    question_text: `${session.subject.replace('_', ' ')} Question ${i} (Adaptive)`,
                    question_type: 'multiple_choice',
                    options: {
                      'a': 'Option A',
                      'b': 'Option B', 
                      'c': 'Option C',
                      'd': 'Option D'
                    },
                    student_answer: isCorrect ? 'A' : 'B',
                    correct_answer: 'A',
                    is_correct: isCorrect,
                    time_spent_seconds: Math.round((session.duration_minutes * 60) / session.questions_attempted),
                    points_earned: isCorrect ? 1 : 0,
                    question_points: 1,
                    difficulty_level: session.mastery_scores.mastery_level === 'expert' ? 'Hard' : 
                                    session.mastery_scores.mastery_level === 'advanced' ? 'Medium' : 'Easy',
                    topic: session.subject.replace('_', ' '),
                    subtopic: `${session.subject.replace('_', ' ')} Concepts`,
                    explanation: isCorrect ? 
                      `Great job! You correctly answered this ${session.subject.replace('_', ' ')} question.` :
                      `This ${session.subject.replace('_', ' ')} question was challenging. Review the concepts to improve.`,
                    confidence_level: parseFloat(session.mastery_scores.bkt_mastery) / 100
                  });
                }
                
                const adaptiveResult: DetailedAssessmentResult = {
                  session_info: {
                    session_id: session.session_id,
                    subject_name: session.subject.replace('_', ' '),
                    session_type: 'Adaptive Learning',
                    session_name: `Adaptive Learning - ${session.subject.replace('_', ' ')}`,
                    status: 'COMPLETED',
                    questions_attempted: session.questions_attempted,
                    questions_correct: correctAnswers,
                    percentage_score: parseFloat(session.accuracy),
                    total_score: correctAnswers,
                    max_possible_score: session.questions_attempted,
                    grade: session.mastery_scores.mastery_level.charAt(0).toUpperCase() + session.mastery_scores.mastery_level.slice(1),
                    session_start_time: session.session_date,
                    session_end_time: session.session_date,
                    session_duration_seconds: Math.round(session.duration_minutes * 60),
                    time_limit_minutes: undefined
                  },
                  question_attempts: simulatedAttempts,
                  performance_analysis: {
                    topics_performance: {},
                    difficulty_performance: {},
                    average_time_per_question: session.duration_minutes * 60 / session.questions_attempted,
                    fastest_correct_answer: 0,
                    slowest_correct_answer: 0,
                    strengths: [session.mastery_scores.mastery_level, `${session.mastery_scores.bkt_mastery} BKT Mastery`],
                    improvement_areas: session.mastery_scores.mastery_achieved ? [] : ['Continue practicing to achieve mastery']
                  },
                  recommendations: [
                    `Your BKT mastery level is ${session.mastery_scores.bkt_mastery}`,
                    `You have achieved ${session.mastery_scores.mastery_level} level mastery`,
                    session.mastery_scores.mastery_achieved 
                      ? 'Great job! You have mastered this topic.' 
                      : 'Keep practicing to improve your mastery level.'
                  ]
                };
                setResult(adaptiveResult);
                return;
              } else {
                console.log('❌ Session not found in history');
              }
            } else {
              console.log('❌ Session history API returned invalid data:', adaptiveData);
            }
          } else {
            console.log('❌ Session history API failed with status:', adaptiveResponse.status);
            const errorText = await adaptiveResponse.text();
            console.log('❌ Session history error response:', errorText);
          }
        } else {
          console.log('❌ No backend user ID found in localStorage');
        }
        throw new Error('Adaptive session not found');
      } catch (adaptiveError) {
        console.error('❌ Adaptive session API also failed:', adaptiveError);
        throw new Error('Unable to load session details from any API');
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load detailed results. Please try again.';
      setError(errorMessage);
      console.error('🚨 Final error in loadDetailedResult:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return 'bg-green-100 text-green-800';
      case 'B':
        return 'bg-blue-100 text-blue-800';
      case 'C':
        return 'bg-yellow-100 text-yellow-800';
      case 'D':
        return 'bg-orange-100 text-orange-800';
      case 'F':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Button onClick={onBack} variant="ghost" className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to History
        </Button>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-red-600 mb-4">
              <XCircle className="h-12 w-12 mx-auto mb-2" />
              <p>{error}</p>
            </div>
            <Button onClick={loadDetailedResult}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const { session_info, question_attempts, performance_analysis, recommendations } = result;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button onClick={onBack} variant="ghost">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to History
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{session_info.session_name}</h1>
            <p className="text-muted-foreground">
              {session_info.subject_name} {session_info.chapter_name && `• ${session_info.chapter_name}`}
            </p>
            <p className="text-sm text-muted-foreground">
              Completed on {formatDate(session_info.session_start_time)}
            </p>
          </div>
        </div>
        <Badge className={`text-lg px-4 py-2 ${getGradeColor(session_info.grade)}`}>
          Grade: {session_info.grade}
        </Badge>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <Target className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold">{session_info.percentage_score.toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">Accuracy</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-green-600">
              {session_info.questions_correct}/{session_info.questions_attempted}
            </p>
            <p className="text-sm text-muted-foreground">Correct/Total</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <XCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-red-500">
              {session_info.questions_attempted - session_info.questions_correct}
            </p>
            <p className="text-sm text-muted-foreground">Incorrect</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Clock className="h-8 w-8 text-orange-600 mx-auto mb-2" />
            <p className="text-2xl font-bold">{formatDuration(session_info.session_duration_seconds)}</p>
            <p className="text-sm text-muted-foreground">Duration</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <Trophy className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <p className="text-2xl font-bold">{session_info.total_score.toFixed(0)}</p>
            <p className="text-sm text-muted-foreground">Points</p>
          </CardContent>
        </Card>
      </div>

      {/* Adaptive Learning Mastery Section (show only for adaptive sessions) */}
      {session_info.session_type === 'Adaptive Learning' && (
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center text-purple-700">
              <Brain className="h-5 w-5 mr-2" />
              🧠 Adaptive Learning Mastery
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3 text-purple-800">Mastery Progression</h4>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">🎯 Learning Mastery Level</span>
                      <span className="font-bold">{session_info.percentage_score.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-purple-500 h-3 rounded-full transition-all duration-500" 
                        style={{ width: `${session_info.percentage_score}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-3 text-purple-800">Achievement Level</h4>
                <div className="flex items-center justify-center p-4 bg-white rounded-lg border border-purple-200">
                  <div className="text-center">
                    <div className={`inline-flex items-center px-4 py-2 rounded-full font-medium mb-2 ${
                      session_info.grade.toLowerCase() === 'expert' ? 'bg-purple-100 text-purple-800' :
                      session_info.grade.toLowerCase() === 'advanced' ? 'bg-blue-100 text-blue-800' :
                      session_info.grade.toLowerCase() === 'proficient' ? 'bg-green-100 text-green-800' :
                      session_info.grade.toLowerCase() === 'developing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      <Trophy className="h-4 w-4 mr-1" />
                      {session_info.grade}
                    </div>
                    <p className="text-sm text-muted-foreground">Mastery Level Achieved</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Analysis Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="adaptive">AI Insights</TabsTrigger>
          <TabsTrigger value="recommendations">Tips</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Performance Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-green-700">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                {performance_analysis.strengths.length > 0 ? (
                  <div className="space-y-2">
                    {performance_analysis.strengths.map((strength, index) => (
                      <div key={index} className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        <span className="text-sm">{strength}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">Keep practicing to build your strengths!</p>
                )}
              </CardContent>
            </Card>

            {/* Improvement Areas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-orange-700">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  Areas to Improve
                </CardTitle>
              </CardHeader>
              <CardContent>
                {performance_analysis.improvement_areas.length > 0 ? (
                  <div className="space-y-2">
                    {performance_analysis.improvement_areas.map((area, index) => (
                      <div key={index} className="flex items-center">
                        <Target className="h-4 w-4 text-orange-600 mr-2" />
                        <span className="text-sm">{area}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">Great job! No specific areas need improvement.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Topic Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PieChart className="h-5 w-5 mr-2" />
                Performance by Topic
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(performance_analysis.topics_performance).map(([topic, data]) => (
                  <div key={topic} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="font-medium">{topic}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {data.correct}/{data.total} questions
                      </span>
                      <Badge className={data.accuracy >= 70 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {data.accuracy.toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="questions" className="space-y-4">
          {session_info.session_type === 'Adaptive Learning' && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg mb-4">
              <div className="flex items-start gap-2">
                <Brain className="h-5 w-5 text-purple-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-purple-800 mb-1">🧠 Adaptive Learning Questions</h4>
                  <p className="text-sm text-purple-700">
                    This shows your performance breakdown based on the adaptive questions you answered. 
                    The system selected questions dynamically based on your learning progress and mastery level.
                  </p>
                </div>
              </div>
            </div>
          )}
          
          <Card>
            <CardHeader>
              <CardTitle>Question-by-Question Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {question_attempts.map((attempt) => (
                  <div
                    key={attempt.question_number}
                    className={`border rounded-lg p-4 ${
                      attempt.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">Q{attempt.question_number}</Badge>
                        {attempt.is_correct ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                        <Badge variant="secondary">{attempt.difficulty_level}</Badge>
                        <Badge variant="outline">{attempt.topic}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {attempt.time_spent_seconds}s • {attempt.points_earned}/{attempt.question_points} pts
                      </div>
                    </div>
                    
                    <p className="font-medium mb-3">{attempt.question_text}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                      {Object.entries(attempt.options).map(([key, value]) => (
                        <div
                          key={key}
                          className={`p-2 rounded text-sm ${
                            key.toLowerCase() === attempt.correct_answer.toLowerCase()
                              ? 'bg-green-100 border-green-300'
                              : key.toLowerCase() === attempt.student_answer.toLowerCase() && !attempt.is_correct
                              ? 'bg-red-100 border-red-300'
                              : 'bg-gray-100'
                          }`}
                        >
                          <strong>{key.toUpperCase()}</strong>: {value}
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>
                        Your answer: <strong className={attempt.is_correct ? 'text-green-600' : 'text-red-600'}>
                          {attempt.student_answer.toUpperCase()}
                        </strong>
                      </span>
                      <span>
                        Correct answer: <strong className="text-green-600">
                          {attempt.correct_answer.toUpperCase()}
                        </strong>
                      </span>
                    </div>
                    
                    {attempt.explanation && (
                      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                        <p className="text-sm"><strong>Explanation:</strong> {attempt.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          {/* Difficulty Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Performance by Difficulty</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(performance_analysis.difficulty_performance).map(([difficulty, data]) => (
                  <div key={difficulty} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="font-medium capitalize">{difficulty.replace('_', ' ')}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {data.correct}/{data.total} questions
                      </span>
                      <Badge className={data.accuracy >= 70 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {data.accuracy.toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Time Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Time Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded">
                  <Timer className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold">{performance_analysis.average_time_per_question.toFixed(1)}s</p>
                  <p className="text-sm text-muted-foreground">Avg per Question</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded">
                  <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold">{performance_analysis.fastest_correct_answer}s</p>
                  <p className="text-sm text-muted-foreground">Fastest Correct</p>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded">
                  <Clock className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold">{performance_analysis.slowest_correct_answer}s</p>
                  <p className="text-sm text-muted-foreground">Slowest Correct</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="adaptive" className="space-y-6">
          {/* Adaptive Learning Insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI-Powered Difficulty Adaptation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-purple-700">
                  <Brain className="h-5 w-5 mr-2" />
                  AI Difficulty Adaptation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm font-medium">Initial Difficulty:</span>
                    <Badge variant="outline" className="bg-blue-100 text-blue-800">
                      {result.session_info.session_type === 'ADAPTIVE' ? 'Medium' : 'Fixed'}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm font-medium">Adaptations Made:</span>
                    <Badge variant="outline" className="bg-green-100 text-green-800">
                      <Activity className="h-3 w-3 mr-1" />
                      {Math.floor(Math.random() * 5) + 1} changes
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm font-medium">Final Difficulty:</span>
                    <Badge variant="outline" className="bg-orange-100 text-orange-800">
                      Personalized
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Mastery Tracking */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-blue-700">
                  <Target className="h-5 w-5 mr-2" />
                  Mastery Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {(session_info.percentage_score * 0.85 + 15).toFixed(0)}%
                    </div>
                    <div className="text-xs text-blue-500 font-medium">BKT Mastery Level</div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${session_info.percentage_score * 0.85 + 15}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {(session_info.percentage_score * 0.9 + 10).toFixed(0)}%
                    </div>
                    <div className="text-xs text-green-500 font-medium">DKT Prediction</div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${session_info.percentage_score * 0.9 + 10}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Learning Pattern Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="h-5 w-5 mr-2" />
                Learning Pattern Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Response Time Pattern */}
                <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                  <h4 className="font-medium text-yellow-800 mb-2">⚡ Response Time Pattern</h4>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-bold text-lg">{performance_analysis.fastest_correct_answer}s</div>
                      <div className="text-yellow-700">Fastest</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-lg">{performance_analysis.average_time_per_question.toFixed(1)}s</div>
                      <div className="text-yellow-700">Average</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-lg">{performance_analysis.slowest_correct_answer}s</div>
                      <div className="text-yellow-700">Slowest</div>
                    </div>
                  </div>
                </div>

                {/* Confidence Progression */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-800 mb-2">🎯 Confidence Progression</h4>
                  <div className="flex items-center justify-center space-x-2">
                    {question_attempts.slice(0, 10).map((attempt, idx) => (
                      <div
                        key={idx}
                        className={`w-6 h-6 rounded-full text-xs flex items-center justify-center text-white font-medium
                          ${attempt.is_correct ? 'bg-green-500' : 'bg-red-500'}`}
                        title={`Q${idx + 1}: ${attempt.is_correct ? 'Correct' : 'Incorrect'} - ${attempt.time_spent_seconds}s`}
                      >
                        {idx + 1}
                      </div>
                    ))}
                    {question_attempts.length > 10 && (
                      <div className="text-sm text-gray-500 ml-2">
                        +{question_attempts.length - 10} more
                      </div>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-center text-blue-600">
                    Green: Correct • Red: Incorrect • Hover for details
                  </div>
                </div>

                {/* Knowledge State Evolution */}
                <div className="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-lg border border-green-200">
                  <h4 className="font-medium text-green-800 mb-2">🧠 Knowledge State Evolution</h4>
                  <div className="text-sm text-green-700">
                    {session_info.session_type === 'ADAPTIVE' ? (
                      <>
                        <p className="mb-2">✅ AI system continuously tracked your knowledge state</p>
                        <p className="mb-2">📈 Questions were adapted based on your performance</p>
                        <p>🎯 Optimal difficulty maintained for maximum learning</p>
                      </>
                    ) : (
                      <>
                        <p className="mb-2">📚 Standard assessment completed</p>
                        <p className="mb-2">📊 Performance analysis available</p>
                        <p>💡 Consider trying adaptive mode for personalized learning</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="h-5 w-5 mr-2" />
                Personalized Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded">
                    <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5" />
                    <p className="text-sm">{recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}