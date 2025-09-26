import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  AlertTriangle, 
  Headphones, 
  Target, 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  RefreshCw,
  Wifi,
  WifiOff
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart as RechartsLineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface DashboardData {
  total_students: number;
  total_sessions: number;
  total_submissions: number;
  average_session_accuracy: number;
  most_popular_subject: string;
  recent_activity: Array<{
    student: string;
    subject: string;
    correct: boolean;
    time: string;
    mastery: number;
  }>;
  performance_trends: {
    daily_accuracy: number[];
  };
}

interface SessionReport {
  session_id: string;
  student_name: string;
  subject: string;
  start_time: string;
  end_time?: string;
  total_questions: number;
  correct_answers: number;
  accuracy_percentage: number;
  average_time_per_question: number;
  mastery_progression: Record<string, any>;
  difficulty_distribution: Record<string, number>;
  session_duration_minutes: number;
}

interface StudentReport {
  student_id: number;
  student_name: string;
  total_sessions: number;
  total_questions_attempted: number;
  overall_accuracy: number;
  mastery_growth: number;
  subjects_studied: string[];
  last_activity: string;
  performance_trend: Record<string, any>;
}

interface QuestionAnalytic {
  question_id: string;
  question_text: string;
  subject: string;
  difficulty_level: string;
  total_attempts: number;
  correct_attempts: number;
  success_rate: number;
  average_time_spent: number;
  most_common_wrong_answer?: string;
}

type ReportsTab = 'overview' | 'analytics' | 'sessions' | 'students' | 'questions';

export default function ReportsView() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<ReportsTab>('overview');
  
  // Analytics Data States
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [sessionReports, setSessionReports] = useState<SessionReport[]>([]);
  const [studentReports, setStudentReports] = useState<StudentReport[]>([]);
  const [questionAnalytics, setQuestionAnalytics] = useState<QuestionAnalytic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const API_BASE = 'http://localhost:8000/api/reports';

  // Fetch analytics data
  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboard, sessions, students, questions] = await Promise.all([
        fetch(`${API_BASE}/dashboard`).then(async r => {
          if (!r.ok) throw new Error(`Dashboard API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/sessions?days=30`).then(async r => {
          if (!r.ok) throw new Error(`Sessions API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/students?days=30`).then(async r => {
          if (!r.ok) throw new Error(`Students API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/questions`).then(async r => {
          if (!r.ok) throw new Error(`Questions API error: ${r.status}`);
          return r.json();
        })
      ]);

      setDashboardData(dashboard);
      setSessionReports(sessions);
      setStudentReports(students);
      setQuestionAnalytics(questions);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'analytics' || activeTab === 'sessions' || activeTab === 'students' || activeTab === 'questions') {
      fetchAnalyticsData();
    }
  }, [activeTab]);

  // Static data for personal overview
  const performanceData = [
    { week: 'Week 1', score: 60, height: '120px' },
    { week: 'Week 2', score: 70, height: '140px' },
    { week: 'Week 3', score: 80, height: '160px' },
    { week: 'Week 4', score: 90, height: '180px' },
    { week: 'This Week', score: 100, height: '200px' },
  ];

  const learningGaps = [
    {
      type: 'critical',
      title: 'Critical Gaps',
      count: 2,
      items: ['Formula retention (Quantitative)', 'Audio comprehension (All modules)'],
      bgColor: 'bg-destructive/10',
      borderColor: 'border-destructive/20',
      textColor: 'text-destructive',
    },
    {
      type: 'moderate', 
      title: 'Moderate Gaps',
      count: 1,
      items: ['Pattern recognition (Logical Reasoning)'],
      bgColor: 'bg-accent/10',
      borderColor: 'border-accent/20',
      textColor: 'text-accent',
    },
    {
      type: 'strengths',
      title: 'Strengths',
      count: 3,
      items: ['Problem application (All modules)', 'Vocabulary (Verbal Ability)', 'Basic concepts (Quantitative)'],
      bgColor: 'bg-chart-4/10',
      borderColor: 'border-chart-4/20',
      textColor: 'text-chart-4',
    },
  ];

  // Process analytics data
  const getPerformanceTrendData = () => {
    if (!dashboardData?.performance_trends?.daily_accuracy) return [];
    return dashboardData.performance_trends.daily_accuracy.map((accuracy, index) => ({
      day: `Day ${index + 1}`,
      accuracy: accuracy
    }));
  };

  const getSessionAccuracyData = () => {
    return sessionReports.slice(0, 10).map(session => ({
      session: session.student_name.substring(0, 10) + '...',
      accuracy: session.accuracy_percentage,
      questions: session.total_questions
    }));
  };

  const getStudentRankingData = () => {
    return studentReports
      .sort((a, b) => b.overall_accuracy - a.overall_accuracy)
      .slice(0, 10)
      .map(student => ({
        name: student.student_name.substring(0, 15) + '...',
        accuracy: student.overall_accuracy,
        sessions: student.total_sessions
      }));
  };

  const getQuestionDifficultyData = () => {
    const difficultyGroups = questionAnalytics.reduce((acc, question) => {
      const difficulty = question.difficulty_level || 'unknown';
      acc[difficulty] = (acc[difficulty] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(difficultyGroups).map(([difficulty, count]) => ({
      name: difficulty.charAt(0).toUpperCase() + difficulty.slice(1),
      value: count
    }));
  };

  const tabs = [
    { key: 'overview', label: 'My Overview', icon: <Target className="w-4 h-4" /> },
    { key: 'analytics', label: 'System Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { key: 'sessions', label: 'Session Reports', icon: <LineChart className="w-4 h-4" /> },
    { key: 'students', label: 'Student Performance', icon: <TrendingUp className="w-4 h-4" /> },
    { key: 'questions', label: 'Question Analytics', icon: <PieChart className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Learning Analytics</h2>
          <p className="text-muted-foreground">Comprehensive insights into learning progress</p>
        </div>
        
        {(activeTab === 'analytics' || activeTab === 'sessions' || activeTab === 'students' || activeTab === 'questions') && (
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              error ? 'bg-destructive/10 text-destructive' : 'bg-primary/10 text-primary'
            }`}>
              {error ? <WifiOff className="w-3 h-3" /> : <Wifi className="w-3 h-3" />}
              <span>{error ? 'Disconnected' : 'Connected'}</span>
            </div>
            
            {lastUpdated && (
              <div className="text-sm text-muted-foreground">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            )}
            
            <Button
              onClick={fetchAnalyticsData}
              disabled={loading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-border">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as ReportsTab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.key
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Error Banner */}
      {error && (activeTab === 'analytics' || activeTab === 'sessions' || activeTab === 'students' || activeTab === 'questions') && (
        <Card className="border-destructive/20 bg-destructive/5">
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-destructive mr-3" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-destructive">Connection Error</h3>
                <p className="text-sm text-destructive/80 mt-1">
                  Unable to fetch latest data: {error}
                </p>
                <p className="text-sm text-destructive/60 mt-1">
                  Make sure the Django server is running on http://localhost:8000
                </p>
              </div>
              <Button
                onClick={() => {setError(null); fetchAnalyticsData();}}
                variant="outline"
                size="sm"
                className="border-destructive/20 text-destructive hover:bg-destructive/10"
              >
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab Content */}
      {activeTab === 'overview' && <PersonalOverviewTab />}
      {activeTab === 'analytics' && <AnalyticsOverviewTab />}
      {activeTab === 'sessions' && <SessionReportsTab />}
      {activeTab === 'students' && <StudentPerformanceTab />}
      {activeTab === 'questions' && <QuestionAnalyticsTab />}
    </div>
  );

  // Personal Overview Component (Original reports view)
  function PersonalOverviewTab() {
    return (
      <div className="space-y-6">
        {/* Performance Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Chart */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">My Performance Trend</h3>
              <div className="h-64 flex items-end justify-between space-x-2">
                {performanceData.map((data, index) => (
                  <div key={index} className="flex flex-col items-center space-x-2">
                    <div
                      className="bg-primary rounded-t transition-all duration-300 hover:bg-primary/80 cursor-pointer"
                      style={{ height: data.height, width: '32px' }}
                      title={`${data.week}: ${data.score}%`}
                    />
                    <span className="text-xs text-muted-foreground">{data.week}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Learning Gap Analysis */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">My Learning Gaps</h3>
              <div className="space-y-4">
                {learningGaps.map((gap) => (
                  <div
                    key={gap.type}
                    className={`p-4 rounded-lg border ${gap.bgColor} ${gap.borderColor}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className={`font-medium ${gap.textColor}`}>{gap.title}</span>
                      <span className={`text-sm ${gap.textColor}`}>{gap.count} area{gap.count > 1 ? 's' : ''}</span>
                    </div>
                    <ul className={`text-sm ${gap.textColor} space-y-1`}>
                      {gap.items.map((item, index) => (
                        <li key={index}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Study Insights */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">My Study Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-primary/10">
                <div className="text-2xl font-bold text-primary mb-2">45</div>
                <div className="text-sm text-foreground">Practice Sessions</div>
                <div className="text-xs text-muted-foreground">This month</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-secondary/10">
                <div className="text-2xl font-bold text-secondary mb-2">12h</div>
                <div className="text-sm text-foreground">Study Time</div>
                <div className="text-xs text-muted-foreground">This week</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-accent/10">
                <div className="text-2xl font-bold text-accent mb-2">87%</div>
                <div className="text-sm text-foreground">Avg. Accuracy</div>
                <div className="text-xs text-muted-foreground">Last 30 days</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-chart-4/10">
                <div className="text-2xl font-bold text-chart-4 mb-2">15</div>
                <div className="text-sm text-foreground">Concepts Mastered</div>
                <div className="text-xs text-muted-foreground">This month</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Analytics Overview Component
  function AnalyticsOverviewTab() {
    if (!dashboardData) return <div className="text-center py-12">Loading system analytics...</div>;

    return (
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="text-2xl mr-4">👥</div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Students</p>
                  <p className="text-2xl font-bold text-foreground">{dashboardData.total_students}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="text-2xl mr-4">📝</div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Sessions</p>
                  <p className="text-2xl font-bold text-foreground">{dashboardData.total_sessions}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="text-2xl mr-4">✍️</div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Submissions</p>
                  <p className="text-2xl font-bold text-foreground">{dashboardData.total_submissions}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="text-2xl mr-4">🎯</div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Average Accuracy</p>
                  <p className="text-2xl font-bold text-foreground">{dashboardData.average_session_accuracy}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Trend */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-medium text-foreground mb-4">📈 System Performance Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={getPerformanceTrendData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
                  <Line type="monotone" dataKey="accuracy" stroke="hsl(var(--primary))" strokeWidth={2} />
                </RechartsLineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-medium text-foreground mb-4">🕒 Recent Activity</h3>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {(dashboardData.recent_activity || []).slice(0, 5).map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded">
                    <div>
                      <p className="font-medium">{activity.student}</p>
                      <p className="text-sm text-muted-foreground">{activity.subject}</p>
                    </div>
                    <div className="text-right">
                      <Badge variant={activity.correct ? "default" : "destructive"}>
                        {activity.correct ? '✓ Correct' : '✗ Incorrect'}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        Mastery: {(activity.mastery * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Popular Subject */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">🏆 Most Popular Subject</h3>
            <div className="text-center">
              <div className="text-4xl mb-2">📚</div>
              <p className="text-xl font-semibold">{dashboardData.most_popular_subject}</p>
              <p className="text-muted-foreground">Students are focusing on this subject the most</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Session Reports Component
  function SessionReportsTab() {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">📊 Session Performance Overview</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={getSessionAccuracyData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="session" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="accuracy" fill="hsl(var(--primary))" name="Accuracy %" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">📝 Recent Sessions</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {sessionReports.slice(0, 10).map((session, index) => (
                <div key={index} className="p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{session.student_name}</p>
                      <p className="text-sm text-muted-foreground">{session.subject}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(session.start_time).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">{session.accuracy_percentage}%</p>
                      <p className="text-sm text-muted-foreground">
                        {session.correct_answers}/{session.total_questions}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {session.session_duration_minutes.toFixed(1)} min
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Student Performance Component
  function StudentPerformanceTab() {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">👥 Top Performing Students</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={getStudentRankingData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="accuracy" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-foreground mb-4">🎓 Student Performance Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {studentReports.slice(0, 8).map((student, index) => (
                <div key={index} className="p-4 rounded-lg border border-border">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 ${
                        index === 0 ? 'bg-yellow-500' : 
                        index === 1 ? 'bg-gray-400' : 
                        index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-medium">{student.student_name}</h4>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-primary">{student.overall_accuracy}%</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Sessions:</span> {student.total_sessions}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Questions:</span> {student.total_questions_attempted}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Growth:</span> {(student.mastery_growth * 100).toFixed(1)}%
                    </div>
                    <div>
                      <span className="text-muted-foreground">Last Active:</span> {new Date(student.last_activity).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Question Analytics Component
  function QuestionAnalyticsTab() {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-medium text-foreground mb-4">📊 Question Difficulty Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={getQuestionDifficultyData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {getQuestionDifficultyData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-medium text-foreground mb-4">❓ Question Performance</h3>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {questionAnalytics.slice(0, 10).map((question, index) => (
                  <div key={index} className="p-3 rounded-lg border border-border">
                    <div className="flex justify-between items-start">
                      <div className="flex-1 mr-4">
                        <p className="text-sm font-medium mb-1">
                          {question.question_text.length > 60 
                            ? question.question_text.substring(0, 60) + '...' 
                            : question.question_text}
                        </p>
                        <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                          <span>📚 {question.subject}</span>
                          <span>⭐ {question.difficulty_level}</span>
                          <span>👥 {question.total_attempts} attempts</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`text-lg font-bold ${
                          question.success_rate >= 80 ? 'text-green-600' :
                          question.success_rate >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {question.success_rate}%
                        </p>
                        <p className="text-sm text-muted-foreground">success rate</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }
}