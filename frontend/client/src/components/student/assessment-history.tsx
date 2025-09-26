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
  Globe
} from 'lucide-react';
import { IndianTimeUtils } from '@/lib/indian-time-utils';
import { HistoryAPI, type AssessmentHistoryItem, type StudentHistoryStats } from '../../lib/history-api';

interface AssessmentHistoryProps {
  studentUsername: string;
  onViewDetails: (sessionId: string) => void;
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

export function AssessmentHistory({ studentUsername, onViewDetails }: AssessmentHistoryProps) {
  const [history, setHistory] = useState<AssessmentHistoryItem[]>([]);
  const [enhancedHistory, setEnhancedHistory] = useState<EnhancedSessionHistory | null>(null);
  const [stats, setStats] = useState<StudentHistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

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

      // Try to load enhanced session history first
      try {
        let enhancedResponse = await fetch(`/history/student/${studentUsername}/`);
        console.log('Enhanced API Response Status:', enhancedResponse.status);
        
        // If first attempt fails and username doesn't start with 'student_', try prefixed version
        if (!enhancedResponse.ok && !studentUsername.startsWith('student_')) {
          console.log('Trying with student_ prefix...');
          enhancedResponse = await fetch(`/history/student/student_${studentUsername}/`);
          console.log('Prefixed API Response Status:', enhancedResponse.status);
        }
        
        // Also try direct backend API if proxy fails
        if (!enhancedResponse.ok) {
          console.log('Trying direct backend API call...');
          try {
            enhancedResponse = await fetch(`http://localhost:8000/history/student/${studentUsername}/`);
            console.log('Direct backend API Response Status:', enhancedResponse.status);
          } catch (directError) {
            console.log('Direct backend API also failed:', directError);
          }
        }
        
        if (enhancedResponse.ok) {
          const enhancedData = await enhancedResponse.json();
          setEnhancedHistory(enhancedData);
        } else {
          console.log('❌ Enhanced API failed with status:', enhancedResponse.status);
          const errorText = await enhancedResponse.text();
          console.log('Error response:', errorText.substring(0, 200));
        }
      } catch (err) {
        console.warn('Enhanced history not available, falling back to legacy API');
        console.error('Enhanced history error:', err);
      }

      // Load legacy history and stats for compatibility
      const [historyData, statsData] = await Promise.all([
        selectedSubject === 'all' 
          ? HistoryAPI.getStudentHistory(studentUsername)
          : HistoryAPI.getSubjectHistory(studentUsername, selectedSubject),
        HistoryAPI.getStudentStats(studentUsername)
      ]);

      setHistory(historyData);
      setStats(statsData);
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
          {enhancedHistory && enhancedHistory.adaptive_sessions.length > 0 ? (
            <div className="max-h-64 overflow-y-auto space-y-3 pr-2">
              {enhancedHistory.adaptive_sessions.map((session) => (
                <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg bg-purple-50">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Brain className="h-4 w-4 text-purple-600" />
                      <h3 className="font-semibold">{session.session_name}</h3>
                      <Badge className="bg-purple-100 text-purple-800">
                        {session.current_difficulty || 'Adaptive'}
                      </Badge>
                      <Badge variant="outline">
                        {session.accuracy_percentage.toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {session.subject} • {session.questions_attempted} questions • {new Date(session.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                    <Eye className="h-4 w-4 mr-1" />
                    Details
                  </Button>
                </div>
              ))}
            </div>
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
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
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
        </Tabs>
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