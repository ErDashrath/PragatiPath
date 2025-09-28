import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Clock, 
  Trophy, 
  TrendingUp, 
  Calendar, 
  BookOpen, 
  Target,
  Eye,
  BarChart3,
  CheckCircle,
  XCircle,
  Timer,
  Brain,
  Zap,
  Activity,
  Globe,
  Star
} from 'lucide-react';
import { IndianTimeUtils } from '@/lib/indian-time-utils';
import { HistoryAPI, type AssessmentHistoryItem, type StudentHistoryStats } from '../../lib/history-api';
import { AdaptiveLearningAPI } from '@/lib/adaptive-api';
import { useAuth } from '@/hooks/use-auth';

interface AssessmentHistoryProps {
  studentUsername: string;
  onViewDetails: (sessionId: string) => void;
  backendUserId?: number; // Optional backend user ID for mastery history
}

interface EnhancedSessionHistory {
  success: boolean;
  student_username: string;
  summary: {
    total_sessions: number;
    completed_sessions: number;
    total_questions_attempted: number;
    overall_accuracy: number;
    assessment_sessions_count: number;
    adaptive_sessions_count: number;
    subject_breakdown: Record<string, {
      total_sessions: number;
      total_questions: number;
      total_correct: number;
      accuracy: number;
    }>;
  };
  assessment_sessions: Array<{
    session_id: string;
    session_name: string;
    session_type: string;
    subject: string;
    chapter: string | null;
    status: string;
    created_at: string;
    ended_at: string | null;
    duration_minutes: number;
    questions_attempted: number;
    questions_correct: number;
    accuracy_percentage: number;
    total_score: number;
    percentage_score: number;
    recent_attempts: Array<{
      question_id: string;
      is_correct: boolean;
      selected_answer: string;
      time_spent: number;
      difficulty: string;
      skill_id: string;
      timestamp: string;
    }>;
  }>;
  adaptive_sessions: Array<{
    session_id: string;
    session_name: string;
    session_type: string;
    subject: string;
    chapter: string | null;
    status: string;
    created_at: string;
    ended_at: string | null;
    duration_minutes: number;
    questions_attempted: number;
    questions_correct: number;
    accuracy_percentage: number;
    total_score: number;
    percentage_score: number;
    current_difficulty: string;
    difficulty_adjustments: number;
    recent_attempts: Array<{
      question_id: string;
      is_correct: boolean;
      selected_answer: string;
      time_spent: number;
      difficulty: string;
      skill_id: string;
      timestamp: string;
    }>;
  }>;
  generated_at: string;
}

export function AssessmentHistory({ studentUsername, onViewDetails, backendUserId }: AssessmentHistoryProps) {
  const { user } = useAuth();
  const [history, setHistory] = useState<AssessmentHistoryItem[]>([]);
  const [enhancedHistory, setEnhancedHistory] = useState<EnhancedSessionHistory | null>(null);
  const [masteryHistory, setMasteryHistory] = useState<any>(null);
  const [stats, setStats] = useState<StudentHistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('mastery'); // Default to mastery tab to show BKT sessions
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Debug useEffect to track masteryHistory changes
  useEffect(() => {
    console.log('🔄 masteryHistory state changed:', {
      hasData: !!masteryHistory,
      success: masteryHistory?.success,
      totalSessions: masteryHistory?.total_sessions,
      sessionsLength: masteryHistory?.sessions?.length
    });
  }, [masteryHistory]);

  useEffect(() => {
    loadData();
  }, [studentUsername, selectedSubject]);

  // Auto-refresh every 30 seconds to catch new sessions
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing history data...');
      loadData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [studentUsername]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Debug logging
      console.log('=== LOADING HISTORY DATA ===');
      console.log('Username:', studentUsername);
      console.log('Username type:', typeof studentUsername);
      console.log('Username length:', studentUsername?.length || 0);
      console.log('Is empty username?', !studentUsername || studentUsername.trim() === '');
      console.log('Current timestamp:', new Date().toISOString());
      console.log('API URL:', `/history/student/${studentUsername}/`);

      // If no username provided, don't proceed
      if (!studentUsername || studentUsername.trim() === '') {
        console.log('❌ No username provided, skipping API call');
        setError('No username available. Please log in again.');
        return;
      }

      // Create comprehensive username fallback system for all students
      const getUniversalUsernameFallbacks = (username: string) => {
        if (!username) return [];
        
        const fallbacks = [
          username,                           // Original username
          `student_${username}`,             // With student_ prefix
          username.replace('student_', ''),   // Without student_ prefix
          username.toLowerCase(),             // Lowercase version
          username.toUpperCase(),             // Uppercase version
        ];
        
        // Remove duplicates and empty strings
        const uniqueFallbacks = [];
        const seen = new Set();
        for (const fallback of fallbacks) {
          if (fallback && fallback.trim() && !seen.has(fallback)) {
            uniqueFallbacks.push(fallback);
            seen.add(fallback);
          }
        }
        return uniqueFallbacks;
      };
      
      const usernameFallbacks = getUniversalUsernameFallbacks(studentUsername);
      console.log(`Username fallbacks for ${studentUsername}:`, usernameFallbacks);

      // Try to load enhanced session history first with comprehensive fallback system
      let enhancedData = null;
      let workingUsername = null;
      
      for (const tryUsername of usernameFallbacks) {
        try {
          console.log(`Trying enhanced API with username: ${tryUsername}`);
          let enhancedResponse = await fetch(`/history/student/${tryUsername}/`);
          console.log(`Enhanced API Response Status for ${tryUsername}:`, enhancedResponse.status);
          
          if (enhancedResponse.ok) {
            try {
              enhancedData = await enhancedResponse.json();
              workingUsername = tryUsername;
              console.log(`✅ Enhanced API successful with username: ${tryUsername}`);
              setEnhancedHistory(enhancedData);
              break; // Stop trying once we find a working username
            } catch (jsonError) {
              console.log(`❌ Enhanced API returned HTML instead of JSON for ${tryUsername}:`, jsonError);
              // Continue to next username
            }
          }
        } catch (err) {
          console.log(`Enhanced API error for ${tryUsername}:`, err);
          // Continue to next username
        }
      }
      
      if (!workingUsername) {
        console.log('❌ Enhanced API failed for all username variations');
      }

      // Load mastery history using backend user ID (multiple sources with auto-detection)
      try {
        const storedUserId = localStorage.getItem('pragatipath_backend_user_id');
        let userId = backendUserId || 
                    (storedUserId ? parseInt(storedUserId, 10) : null) ||
                    (user?.id ? (typeof user.id === 'string' ? parseInt(user.id, 10) : user.id) : null);
        
        // If no user ID found, try to auto-detect from recent sessions
        if (!userId && studentUsername) {
          console.log('Auto-detecting user ID for:', studentUsername);
          
          // Try common user IDs that might have recent sessions
          const candidateIds = [69, 68, 36, 106, 107, 108, 109, 110]; // Common user IDs
          
          for (const candidateId of candidateIds) {
            try {
              const testData = await AdaptiveLearningAPI.getSessionHistory(candidateId);
              if (testData.success && testData.total_sessions > 0) {
                console.log(`✅ Found sessions for user ID ${candidateId}:`, testData.total_sessions, 'sessions');
                userId = candidateId;
                
                // Store for future use
                localStorage.setItem('pragatipath_backend_user_id', candidateId.toString());
                break;
              }
            } catch (err) {
              // Continue to next candidate
              continue;
            }
          }
        }
        
        if (userId) {
          console.log('Loading mastery history for user ID:', userId, 'source:', 
                     backendUserId ? 'prop' : storedUserId ? 'localStorage' : 'auto-detected');
          
          const masteryData = await AdaptiveLearningAPI.getSessionHistory(userId);
          console.log('🎯 Mastery history loaded:', masteryData);
          console.log('🎯 Setting masteryHistory state with:', {
            success: masteryData.success,
            total_sessions: masteryData.total_sessions,
            sessions_count: masteryData.sessions?.length
          });
          setMasteryHistory(masteryData);
          
          // Force component update
          console.log('🔄 Forcing component refresh after mastery data loaded');
          setLastUpdated(new Date());
        } else {
          console.log('No user ID available for mastery history after auto-detection');
          console.log('Sources - Backend prop:', backendUserId, 'LocalStorage:', storedUserId, 'Auth user:', user?.id);
        }
      } catch (masteryErr) {
        console.warn('Mastery history not available:', masteryErr);
        console.log('Attempted user ID from various sources failed');
        // Don't set error as this is optional enhancement
      }

      // Load legacy history and stats for compatibility with username fallback system
      let legacyHistoryData: any[] = [];
      let legacyStatsData: any = null;
      
      // Try the working username first, then fallback to other usernames
      const legacyUsernamesToTry = workingUsername ? [workingUsername, ...usernameFallbacks] : usernameFallbacks;
      
      for (const tryUsername of legacyUsernamesToTry) {
        try {
          console.log(`Trying legacy API with username: ${tryUsername}`);
          const [historyData, statsData] = await Promise.all([
            selectedSubject === 'all' 
              ? HistoryAPI.getStudentHistory(tryUsername)
              : HistoryAPI.getSubjectHistory(tryUsername, selectedSubject),
            HistoryAPI.getStudentStats(tryUsername)
          ]);
          
          // If we got any data, use it
          if (historyData && historyData.length > 0) {
            legacyHistoryData = historyData;
            legacyStatsData = statsData;
            console.log(`✅ Legacy API successful with username: ${tryUsername}, found ${historyData.length} records`);
            break;
          }
        } catch (legacyErr) {
          console.log(`Legacy API error for ${tryUsername}:`, legacyErr);
          // Continue to next username
        }
      }

      setHistory(legacyHistoryData);
      setStats(legacyStatsData);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to load assessment history. Please try again.');
      console.error('Error loading history:', err);
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'IN_PROGRESS':
        return <Timer className="h-4 w-4 text-blue-600" />;
      case 'PAUSED':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <XCircle className="h-4 w-4 text-red-600" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-red-600 mb-4">
              <XCircle className="h-12 w-12 mx-auto mb-2" />
              <p>{error}</p>
            </div>
            <Button onClick={loadData}>Try Again</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Learning History</h1>
          <p className="text-muted-foreground">Track your assessment and adaptive learning progress</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadData} variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Refresh History
          </Button>
          <div className="text-sm text-muted-foreground flex items-center">
            <Clock className="h-3 w-3 mr-1" />
            {lastUpdated ? `Updated: ${lastUpdated.toLocaleTimeString()}` : 'Auto-refreshes every 30s'}
          </div>
        </div>
      </div>



      {/* Statistics Overview */}
      {enhancedHistory ? (
        <>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Sessions</p>
                  <p className="text-2xl font-bold">{enhancedHistory.summary.total_sessions}</p>
                </div>
                <BookOpen className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Overall Accuracy</p>
                  <p className="text-2xl font-bold">{enhancedHistory.summary.overall_accuracy.toFixed(1)}%</p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Assessment Sessions</p>
                  <p className="text-2xl font-bold">{enhancedHistory.summary.assessment_sessions_count}</p>
                </div>
                <Trophy className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Adaptive Sessions</p>
                  <p className="text-2xl font-bold">{enhancedHistory.summary.adaptive_sessions_count}</p>
                </div>
                <Brain className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Questions</p>
                  <p className="text-2xl font-bold">{enhancedHistory.summary.total_questions_attempted}</p>
                </div>
                <Clock className="h-8 w-8 text-indigo-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-4">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Globe className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm font-medium">Data Updated</p>
                  <p className="text-xs text-muted-foreground">Indian Standard Time (IST)</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-mono">{enhancedHistory ? IndianTimeUtils.formatIST(new Date(enhancedHistory.generated_at)) : 'Loading...'}</p>
                <p className="text-xs text-muted-foreground">
                  Auto-refreshes every 30 seconds
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        </>
      ) : stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Assessments</p>
                  <p className="text-2xl font-bold">{stats?.total_assessments || 0}</p>
                </div>
                <BookOpen className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Overall Accuracy</p>
                  <p className="text-2xl font-bold">{stats?.overall_accuracy.toFixed(1) || 0}%</p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Best Score</p>
                  <p className="text-2xl font-bold">{stats?.best_accuracy.toFixed(1) || 0}%</p>
                </div>
                <Trophy className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg. Time</p>
                  <p className="text-2xl font-bold">{formatDuration(stats?.average_session_time || 0)}</p>
                </div>
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Adaptive Learning History Section - Always Show */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="h-5 w-5 mr-2 text-purple-600" />
            Adaptive Learning History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {masteryHistory && masteryHistory.success && masteryHistory.sessions.length > 0 ? (
            <>
              {/* Session Count Info */}
              <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2">
                  <Trophy className="h-4 w-4 text-purple-600" />
                  <span className="font-medium text-purple-800">
                    {masteryHistory.total_sessions} Adaptive Learning Sessions Completed
                  </span>
                  <Badge variant="outline" className="ml-auto">
                    Updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Now'}
                  </Badge>
                </div>
              </div>
              
              <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
                {masteryHistory.sessions.map((session: any, index: number) => {
                  const masteryScores = session.mastery_scores;
                  const getMasteryColor = (level: string) => {
                    switch (level) {
                      case 'expert': return 'bg-purple-100 text-purple-800 border-purple-200';
                      case 'advanced': return 'bg-blue-100 text-blue-800 border-blue-200';
                      case 'proficient': return 'bg-green-100 text-green-800 border-green-200';
                      case 'developing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
                      case 'novice': return 'bg-gray-100 text-gray-800 border-gray-200';
                      default: return 'bg-gray-100 text-gray-800 border-gray-200';
                    }
                  };

                  return (
                    <div key={session.session_id} className="p-4 border rounded-lg bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Brain className="h-4 w-4 text-purple-600" />
                            <h3 className="font-semibold capitalize">{session.subject.replace('_', ' ')}</h3>
                            <Badge className={`${getMasteryColor(masteryScores.mastery_level)} font-medium`}>
                              {masteryScores.mastery_level} ({masteryScores.bkt_mastery})
                            </Badge>
                            <Badge variant="outline">
                              {session.accuracy}
                            </Badge>
                          </div>
                          
                          <div className="text-sm text-muted-foreground mb-3">
                            📅 {session.session_date} • ❓ {session.questions_attempted} questions • ⏱️ {session.duration_minutes.toFixed(1)} min
                          </div>

                          {/* Mastery Progress Bar */}
                          <div className="mb-2">
                            <div className="flex justify-between text-xs mb-1">
                              <span className="font-medium text-purple-700">🧠 Mastery Level</span>
                              <span className="font-bold">{masteryScores.bkt_mastery}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-purple-500 h-2 rounded-full transition-all duration-300" 
                                style={{ width: masteryScores.bkt_mastery }}
                              ></div>
                            </div>
                          </div>
                        </div>
                        <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                          <Eye className="h-4 w-4 mr-1" />
                          Details
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : history.length > 0 ? (
            // Fallback: Show regular history sessions as adaptive learning sessions
            <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
              <div className="p-3 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg mb-3">
                <p className="text-sm text-yellow-800 font-medium">
                  ⚡ Your Adaptive Learning Sessions
                </p>
                <p className="text-xs text-yellow-700 mt-1">
                  All sessions shown below • Auto-refreshing every 30 seconds
                </p>
              </div>
              {history.map((session) => (
                <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg bg-purple-50">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Brain className="h-4 w-4 text-purple-600" />
                      <h3 className="font-semibold">{session.session_name || `${session.session_type} Session`}</h3>
                      <Badge className="bg-purple-100 text-purple-800">
                        Adaptive Mode
                      </Badge>
                      <Badge variant="outline">
                        {session.questions_correct}/{session.questions_attempted}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {session.subject_name} • {session.questions_attempted} questions • {new Date(session.session_start_time).toLocaleDateString()}
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                    <Eye className="h-4 w-4 mr-1" />
                    Details
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 text-purple-400 mx-auto mb-4" />
              <p className="text-muted-foreground">No adaptive learning sessions found</p>
              <p className="text-sm text-muted-foreground mb-4">
                Try the Adaptive Learning feature to see your AI-powered progress here
              </p>
              <Button variant="outline">
                <Zap className="h-4 w-4 mr-2" />
                Start Adaptive Learning
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Content with Tabs */}
      {enhancedHistory ? (
        <>
          {/* Debug Info */}
          <div className="mb-4 p-2 bg-blue-50 rounded text-sm">
            <strong>🔧 Debug:</strong> masteryHistory = {masteryHistory ? `${masteryHistory.total_sessions} sessions found` : 'loading...'}
            {masteryHistory && <span> | Latest: {masteryHistory.sessions?.[0]?.session_date}</span>}
          </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="assessments" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Assessments ({enhancedHistory.summary.assessment_sessions_count})
            </TabsTrigger>
            <TabsTrigger value="adaptive" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Adaptive Learning ({enhancedHistory.summary.adaptive_sessions_count})
            </TabsTrigger>
            <TabsTrigger 
              value="mastery" 
              className="flex items-center gap-2 bg-purple-100 border-purple-300"
            >
              <Trophy className="h-4 w-4 text-purple-600" />
              <span className="font-semibold text-purple-800">
                🧠 Mastery Progress {masteryHistory ? `(${masteryHistory.total_sessions})` : ''}
              </span>
            </TabsTrigger>
          </TabsList>



          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Subject Performance Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(enhancedHistory.summary.subject_breakdown).map(([subject, stats]) => (
                    <div key={subject} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{subject}</h4>
                        <div className="grid grid-cols-3 gap-4 text-sm text-muted-foreground mt-1">
                          <span>Sessions: {stats.total_sessions}</span>
                          <span>Questions: {stats.total_questions}</span>
                          <span>Accuracy: {stats.accuracy.toFixed(1)}%</span>
                        </div>
                      </div>
                      <Badge className={stats.accuracy >= 80 ? 'bg-green-100 text-green-800' : 
                                        stats.accuracy >= 60 ? 'bg-yellow-100 text-yellow-800' : 
                                        'bg-red-100 text-red-800'}>
                        {stats.accuracy.toFixed(1)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Assessment History Tab */}
          <TabsContent value="assessments" className="space-y-4">
            {enhancedHistory.assessment_sessions.length > 0 ? (
              <div className="max-h-96 overflow-y-auto space-y-3 pr-2">
                {enhancedHistory.assessment_sessions.map((session) => (
                  <Card key={session.session_id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {getStatusIcon(session.status)}
                            <h3 className="font-semibold">{session.session_name}</h3>
                            <Badge variant="outline">{session.session_type}</Badge>
                            <Badge className={session.accuracy_percentage >= 80 ? 'bg-green-100 text-green-800' : 
                                               session.accuracy_percentage >= 60 ? 'bg-yellow-100 text-yellow-800' : 
                                               'bg-red-100 text-red-800'}>
                              {session.accuracy_percentage.toFixed(1)}%
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground mb-2">
                            <div className="flex items-center gap-2">
                              <Globe className="h-4 w-4" />
                              <span className="font-medium">Started:</span> 
                              <span className="font-mono">{IndianTimeUtils.formatIST(new Date(session.created_at))}</span>
                            </div>
                            {session.ended_at && (
                              <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4" />
                                <span className="font-medium">Completed:</span>
                                <span className="font-mono">{IndianTimeUtils.formatIST(new Date(session.ended_at))}</span>
                              </div>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm text-muted-foreground">
                            <div>
                              <span className="font-medium">Subject:</span> {session.subject}
                            </div>
                            <div>
                              <span className="font-medium">Chapter:</span> {session.chapter || 'All'}
                            </div>
                            <div>
                              <span className="font-medium">Score:</span> {session.questions_correct}/{session.questions_attempted}
                            </div>
                            <div>
                              <span className="font-medium">Duration:</span> {session.duration_minutes}m
                            </div>
                            <div>
                              <span className="font-medium">Date:</span> {new Date(session.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        
                        <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                          <Eye className="h-4 w-4 mr-1" />
                          Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-muted-foreground">No assessment sessions found</p>
                  <p className="text-sm text-muted-foreground">Complete assessments to see your history here</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Adaptive Learning Tab */}
          <TabsContent value="adaptive" className="space-y-4">
            {enhancedHistory.adaptive_sessions.length > 0 ? (
              <div className="max-h-96 overflow-y-auto space-y-3 pr-2">
                {enhancedHistory.adaptive_sessions.map((session) => (
                  <Card key={session.session_id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-3">
                            <Brain className="h-4 w-4 text-purple-600" />
                            <h3 className="font-semibold">{session.session_name}</h3>
                            <Badge variant="outline" className="bg-purple-50 text-purple-700">
                              {session.session_type}
                            </Badge>
                            <Badge className="bg-blue-100 text-blue-800">
                              Difficulty: {session.current_difficulty}
                            </Badge>
                            {session.difficulty_adjustments > 0 && (
                              <Badge className="bg-orange-100 text-orange-800">
                                <Activity className="h-3 w-3 mr-1" />
                                {session.difficulty_adjustments} Adaptations
                              </Badge>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground mb-2">
                            <div className="flex items-center gap-2">
                              <Globe className="h-4 w-4" />
                              <span className="font-medium">Started:</span> 
                              <span className="font-mono">{IndianTimeUtils.formatIST(new Date(session.created_at))}</span>
                            </div>
                            {session.ended_at && (
                              <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4" />
                                <span className="font-medium">Completed:</span>
                                <span className="font-mono">{IndianTimeUtils.formatIST(new Date(session.ended_at))}</span>
                              </div>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm text-muted-foreground mb-2">
                            <div>
                              <span className="font-medium">Subject:</span> {session.subject}
                            </div>
                            <div>
                              <span className="font-medium">Questions:</span> {session.questions_attempted}
                            </div>
                            <div>
                              <span className="font-medium">Accuracy:</span> {session.accuracy_percentage.toFixed(1)}%
                            </div>
                            <div>
                              <span className="font-medium">Duration:</span> {session.duration_minutes}m
                            </div>
                            <div>
                              <span className="font-medium">Adaptations:</span> {session.difficulty_adjustments}
                            </div>
                          </div>

                          {/* Performance Pattern */}
                          {session.recent_attempts && session.recent_attempts.length > 0 && (
                            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                              <h4 className="font-medium text-sm mb-2 flex items-center">
                                <Zap className="h-4 w-4 mr-1 text-yellow-500" />
                                Recent Performance
                              </h4>
                              <div className="flex gap-1">
                                {session.recent_attempts.slice(0, 10).map((attempt, idx) => (
                                  <div
                                    key={idx}
                                    className={`w-6 h-6 rounded text-xs flex items-center justify-center text-white font-medium
                                      ${attempt.is_correct ? 'bg-green-500' : 'bg-red-500'}`}
                                    title={`Q${idx + 1}: ${attempt.is_correct ? 'Correct' : 'Incorrect'}`}
                                  >
                                    {idx + 1}
                                  </div>
                                ))}
                                {session.recent_attempts.length > 10 && (
                                  <div className="text-sm text-gray-500 flex items-center ml-2">
                                    +{session.recent_attempts.length - 10} more
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                          <Eye className="h-4 w-4 mr-1" />
                          Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Brain className="h-12 w-12 text-purple-400 mx-auto mb-4" />
                  <p className="text-muted-foreground">No adaptive learning sessions found</p>
                  <p className="text-sm text-muted-foreground">Start adaptive learning to see your AI-powered progress here</p>
                  <Button className="mt-4" variant="outline">
                    <Zap className="h-4 w-4 mr-2" />
                    Try Adaptive Learning
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Mastery Progress Tab */}
          <TabsContent value="mastery" className="space-y-4">
            {/* Debug Info */}
            <div className="mb-4 p-2 bg-blue-50 rounded text-sm">
              <strong>🔧 Debug:</strong> masteryHistory = {masteryHistory ? `${masteryHistory.total_sessions} sessions found` : 'loading...'}
              {masteryHistory && <span> | Success: {masteryHistory.success ? 'YES' : 'NO'} | Sessions: {masteryHistory.sessions?.length || 0}</span>}
              <br />
              <strong>🕐 Last Updated:</strong> {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
            </div>
            {masteryHistory && masteryHistory.success ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Trophy className="h-5 w-5 mr-2" />
                        Mastery Progression Overview
                      </div>
                      <Button 
                        onClick={loadData} 
                        variant="outline" 
                        size="sm"
                        className="ml-4"
                      >
                        <TrendingUp className="h-4 w-4 mr-1" />
                        Refresh History
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-4 gap-4 mb-6">
                      <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                        <div className="text-sm font-medium text-blue-700 mb-1">Total Sessions</div>
                        <p className="text-3xl font-bold text-blue-600">{masteryHistory.total_sessions}</p>
                        <div className="text-xs text-blue-500">with mastery tracking</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
                        <div className="text-sm font-medium text-green-700 mb-1">Current Level</div>
                        <p className="text-xl font-bold text-green-600 capitalize">
                          {masteryHistory.mastery_progression?.latest_mastery?.mastery_level || 'N/A'}
                        </p>
                        <div className="text-xs text-green-500">latest achievement</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                        <div className="text-sm font-medium text-purple-700 mb-1">BKT Mastery</div>
                        <p className="text-xl font-bold text-purple-600">
                          {masteryHistory.mastery_progression?.latest_mastery?.bkt_mastery || 'N/A'}
                        </p>
                        <div className="text-xs text-purple-500">current confidence</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200">
                        <div className="text-sm font-medium text-orange-700 mb-1">Progress Trend</div>
                        <p className="text-xl font-bold text-orange-600 capitalize">
                          {masteryHistory.mastery_progression?.mastery_trend || 'Stable'}
                        </p>
                        <div className="text-xs text-orange-500">learning trajectory</div>
                      </div>
                    </div>

                    {/* Latest Session Highlight */}
                    {masteryHistory.sessions && masteryHistory.sessions.length > 0 && (
                      <div className="mb-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                        <h4 className="font-semibold text-indigo-800 mb-2 flex items-center">
                          <Star className="h-4 w-4 mr-1" />
                          Latest Session Highlights
                        </h4>
                        <div className="grid md:grid-cols-3 gap-3 text-sm">
                          <div className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1 text-indigo-500" />
                            <span className="text-gray-600">Date:</span>
                            <span className="ml-1 font-medium">{masteryHistory.sessions[0].session_date}</span>
                          </div>
                          <div className="flex items-center">
                            <Target className="h-3 w-3 mr-1 text-indigo-500" />
                            <span className="text-gray-600">Accuracy:</span>
                            <span className="ml-1 font-medium">{masteryHistory.sessions[0].accuracy}</span>
                          </div>
                          <div className="flex items-center">
                            <Brain className="h-3 w-3 mr-1 text-indigo-500" />
                            <span className="text-gray-600">Mastery:</span>
                            <span className="ml-1 font-medium">{masteryHistory.sessions[0].mastery_scores.bkt_mastery}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Session History with Mastery</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {masteryHistory.sessions.map((session: any, index: number) => {
                        const masteryScores = session.mastery_scores;
                        const getMasteryColor = (level: string) => {
                          switch (level) {
                            case 'expert': return 'bg-purple-100 text-purple-800 border-purple-200';
                            case 'advanced': return 'bg-blue-100 text-blue-800 border-blue-200';
                            case 'proficient': return 'bg-green-100 text-green-800 border-green-200';
                            case 'developing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
                            case 'novice': return 'bg-gray-100 text-gray-800 border-gray-200';
                            default: return 'bg-gray-100 text-gray-800 border-gray-200';
                          }
                        };

                        return (
                          <div key={session.session_id} className="border rounded-lg p-4 bg-white">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <Brain className="h-4 w-4 text-blue-600" />
                                  <h3 className="font-semibold capitalize">{session.subject.replace('_', ' ')}</h3>
                                  <Badge className={`border ${getMasteryColor(masteryScores.mastery_level)}`}>
                                    {masteryScores.mastery_level} Level
                                  </Badge>
                                  {masteryScores.mastery_achieved && (
                                    <Badge variant="default" className="bg-green-100 text-green-800">
                                      🏆 Mastery Achieved
                                    </Badge>
                                  )}
                                </div>
                                <div className="text-sm text-muted-foreground flex items-center gap-4">
                                  <span className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {session.session_date}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    {session.duration_minutes} min
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Target className="h-3 w-3" />
                                    {session.accuracy}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Enhanced Mastery Scores Display */}
                            <div className="grid md:grid-cols-3 gap-3 mt-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
                              <div className="text-center p-2 bg-white rounded-lg shadow-sm">
                                <div className="text-xs font-semibold text-blue-700 uppercase tracking-wide mb-1">BKT Mastery</div>
                                <div className="text-2xl font-bold text-blue-600 mb-1">
                                  {masteryScores.bkt_mastery}
                                </div>
                                <div className="text-xs text-blue-500 font-medium">
                                  Bayesian Knowledge Tracking
                                </div>
                                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                                    style={{ width: masteryScores.bkt_mastery }}
                                  ></div>
                                </div>
                              </div>
                              <div className="text-center p-2 bg-white rounded-lg shadow-sm">
                                <div className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-1">DKT Prediction</div>
                                <div className="text-2xl font-bold text-green-600 mb-1">
                                  {masteryScores.dkt_prediction}
                                </div>
                                <div className="text-xs text-green-500 font-medium">
                                  Deep Knowledge Tracing
                                </div>
                                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                                    style={{ width: masteryScores.dkt_prediction }}
                                  ></div>
                                </div>
                              </div>
                              <div className="text-center p-2 bg-white rounded-lg shadow-sm">
                                <div className="text-xs font-semibold text-purple-700 uppercase tracking-wide mb-1">Combined</div>
                                <div className="text-2xl font-bold text-purple-600 mb-1">
                                  {masteryScores.combined_confidence}
                                </div>
                                <div className="text-xs text-purple-500 font-medium">
                                  Overall Confidence
                                </div>
                                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                                  <div 
                                    className="bg-purple-500 h-2 rounded-full transition-all duration-300" 
                                    style={{ width: masteryScores.combined_confidence }}
                                  ></div>
                                </div>
                              </div>
                            </div>
                            
                            {/* Raw Mastery Values for Debug/Reference */}
                            <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono text-gray-600">
                              <span className="font-semibold">Raw Values:</span> 
                              BKT: {(masteryScores.bkt_mastery_raw * 100).toFixed(1)}% | 
                              DKT: {(masteryScores.dkt_prediction_raw * 100).toFixed(1)}% | 
                              Combined: {(masteryScores.combined_confidence_raw * 100).toFixed(1)}%
                            </div>

                            {/* Performance Summary */}
                            <div className="flex items-center justify-between mt-3">
                              <div className="flex items-center gap-4 text-sm">
                                <span className="flex items-center gap-1">
                                  <CheckCircle className="h-3 w-3 text-green-500" />
                                  {session.performance.correct_answers} correct
                                </span>
                                <span className="flex items-center gap-1">
                                  <XCircle className="h-3 w-3 text-red-500" />
                                  {session.performance.total_questions - session.performance.correct_answers} incorrect
                                </span>
                                <span className="text-muted-foreground">
                                  Total: {session.performance.total_questions} questions
                                </span>
                              </div>
                              
                              {/* View Details Button for Mastery Sessions */}
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => onViewDetails(session.session_id)}
                                className="ml-4"
                              >
                                <Eye className="h-4 w-4 mr-1" />
                                View Analysis
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Mastery Data Available</h3>
                  <p className="text-muted-foreground mb-4">
                    Complete adaptive learning sessions to see your mastery progression.
                  </p>
                  <Button onClick={() => window.location.reload()} variant="outline">
                    <Activity className="h-4 w-4 mr-2" />
                    Refresh Data
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
        </>
      ) : (
        // Legacy History Display (fallback)
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              Assessment History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {history.length > 0 ? (
              <div className="max-h-96 overflow-y-auto space-y-3 pr-2">
                {history.map((session) => (
                  <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getStatusIcon(session.status)}
                        <h3 className="font-semibold">{session.session_name}</h3>
                        <Badge variant="outline">{session.session_type}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {session.subject_name} • {session.questions_correct}/{session.questions_attempted} • {new Date(session.session_start_time).toLocaleDateString()}
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                      <Eye className="h-4 w-4 mr-1" />
                      Details
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-muted-foreground">No assessment history found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}