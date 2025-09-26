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

  const modulePerformance = [
    {
      name: 'Quantitative Aptitude',
      score: 68,
      change: '+12%',
      bgColor: 'bg-primary/10',
      textColor: 'text-primary',
    },
    {
      name: 'Logical Reasoning',
      score: 52,
      change: '+8%',
      bgColor: 'bg-secondary/10',
      textColor: 'text-secondary',
    },
    {
      name: 'Verbal Ability',
      score: 74,
      change: '+15%',
      bgColor: 'bg-accent/10',
      textColor: 'text-accent',
    },
  ];

  const recommendations = {
    immediate: [
      {
        icon: AlertTriangle,
        title: 'Focus on Retention',
        description: 'Practice formula memorization daily for 10 minutes',
        color: 'text-destructive',
      },
      {
        icon: Headphones,
        title: 'Improve Listening',
        description: 'Use audio-based practice questions',
        color: 'text-accent',
      },
    ],
    longTerm: [
      {
        icon: Target,
        title: 'Achieve 80% Overall',
        description: 'Target for next 3 months',
        color: 'text-chart-4',
      },
      {
        icon: TrendingUp,
        title: 'Master All Fundamentals',
        description: 'Consistent 75%+ in all areas',
        color: 'text-secondary',
      },
    ],
  };

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
      {activeTab === 'analytics' && <AnalyticsOverviewTab data={dashboardData} trendData={getPerformanceTrendData()} />}
      {activeTab === 'sessions' && <SessionReportsTab data={sessionReports} chartData={getSessionAccuracyData()} />}
      {activeTab === 'students' && <StudentPerformanceTab data={studentReports} chartData={getStudentRankingData()} />}
      {activeTab === 'questions' && <QuestionAnalyticsTab data={questionAnalytics} difficultyData={getQuestionDifficultyData()} />}
    </div>
  );

  // Personal Overview Component (Original reports view)
  function PersonalOverviewTab() {
    return (
      <div className="space-y-6">

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Performance Chart */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Overall Performance Trend</h3>
            <div className="h-64 flex items-end justify-between space-x-2" data-testid="performance-chart">
              {performanceData.map((data, index) => (
                <div key={index} className="flex flex-col items-center space-y-2">
                  <div
                    className="bg-primary rounded-t transition-all duration-300 hover:bg-primary/80 cursor-pointer"
                    style={{ height: data.height, width: '32px' }}
                    title={`${data.week}: ${data.score}%`}
                    data-testid={`chart-bar-${index}`}
                  ></div>
                  <span className="text-xs text-muted-foreground">{data.week}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Learning Gap Analysis */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Learning Gap Analysis</h3>
            <div className="space-y-4">
              {learningGaps.map((gap) => (
                <div
                  key={gap.type}
                  className={`p-4 rounded-lg border ${gap.bgColor} ${gap.borderColor}`}
                  data-testid={`gap-analysis-${gap.type}`}
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

      {/* Module Performance Breakdown */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Module Performance Breakdown</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="module-performance">
            {modulePerformance.map((module) => (
              <div
                key={module.name}
                className={`text-center p-4 rounded-lg ${module.bgColor}`}
                data-testid={`module-performance-${module.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <div className={`text-2xl font-bold ${module.textColor} mb-2`}>
                  {module.score}%
                </div>
                <div className="text-sm font-medium text-foreground mb-1">
                  {module.name}
                </div>
                <div className="text-xs text-muted-foreground">
                  {module.change} this month
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Personalized Recommendations */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Personalized Recommendations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-foreground">Immediate Actions</h4>
              <div className="space-y-3">
                {recommendations.immediate.map((rec, index) => {
                  const Icon = rec.icon;
                  return (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 rounded-lg bg-muted/50"
                      data-testid={`immediate-action-${index}`}
                    >
                      <Icon className={`h-5 w-5 ${rec.color} mt-1`} />
                      <div>
                        <p className="text-sm font-medium text-foreground">{rec.title}</p>
                        <p className="text-xs text-muted-foreground">{rec.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium text-foreground">Long-term Goals</h4>
              <div className="space-y-3">
                {recommendations.longTerm.map((rec, index) => {
                  const Icon = rec.icon;
                  return (
                    <div
                      key={index}
                      className="flex items-start space-x-3 p-3 rounded-lg bg-muted/50"
                      data-testid={`long-term-goal-${index}`}
                    >
                      <Icon className={`h-5 w-5 ${rec.color} mt-1`} />
                      <div>
                        <p className="text-sm font-medium text-foreground">{rec.title}</p>
                        <p className="text-xs text-muted-foreground">{rec.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Study Insights */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Study Insights</h3>
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
