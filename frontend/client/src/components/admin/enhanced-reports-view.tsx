import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  TrendingUp, 
  BarChart3,
  RefreshCw,
  Users,
  BookOpen,
  Activity,
  CheckCircle,
  AlertTriangle
} from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

type ReportsTab = 'system' | 'students' | 'sessions' | 'performance';

// Type definitions for API responses
interface SystemStatsResponse {
  users: {
    total: number;
    students: number;
    active_week: number;
  };
  sessions: {
    total: number;
    today: number;
    week: number;
    month: number;
  };
  questions: {
    total: number;
    today: number;
  };
  subjects: Array<{
    name: string;
    sessions: number;
    questions_attempted: number;
    accuracy: number;
  }>;
  last_updated: string;
}

interface ClassOverviewResponse {
  totalStudents: number;
  activeThisWeek: number;
  totalSessions: number;
  completedSessions: number;
  averageAccuracy: number;
  recentActivity: number;
  total_students: number;
  average_progress: number;
  completion_rate: number;
  retention_rate: number;
  weekly_study_hours: number;
  struggling_students: number;
  improving_students: number;
  excellent_students: number;
}

interface StudentDataResponse {
  id: string;
  username: string;
  email: string;
  full_name: string;
  created_at: string;
  last_active: string;
  total_sessions: number;
  completed_sessions: number;
  accuracy: number;
  is_active: boolean;
  listening_score: number;
  grasping_score: number;
  retention_score: number;
  application_score: number;
}

export default function EnhancedReportsView() {
  const [activeTab, setActiveTab] = useState<ReportsTab>('system');
  const [lastRefresh, setLastRefresh] = useState(new Date());
  
  // Use working admin API endpoints with proper typing
  const { data: systemStats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useQuery<SystemStatsResponse>({
    queryKey: ["/api/admin/system-stats"],
    retry: 2,
  });

  const { data: studentsData, isLoading: studentsLoading, error: studentsError, refetch: refetchStudents } = useQuery<StudentDataResponse[]>({
    queryKey: ["/api/admin/students"],
    retry: 2,
  });

  const { data: classOverview, isLoading: overviewLoading, error: overviewError, refetch: refetchOverview } = useQuery<ClassOverviewResponse>({
    queryKey: ["/api/admin/class-overview"],
    retry: 2,
  });

  const loading = statsLoading || studentsLoading || overviewLoading;
  const hasErrors = statsError || studentsError || overviewError;

  const refreshAllData = () => {
    refetchStats();
    refetchStudents();
    refetchOverview();
    setLastRefresh(new Date());
  };

  // Process data for charts
  const getSubjectPerformanceData = () => {
    if (!systemStats?.subjects || !Array.isArray(systemStats.subjects)) return [];
    return systemStats.subjects.map((subject) => ({
      subject: subject.name,
      accuracy: Math.round(subject.accuracy),
      sessions: subject.sessions,
      questions: subject.questions_attempted
    }));
  };

  const getStudentPerformanceData = () => {
    if (!studentsData || !Array.isArray(studentsData)) return [];
    return studentsData.slice(0, 10).map((student, index) => {
      const avgScore = Math.round((
        (student.listening_score || 0) + 
        (student.grasping_score || 0) + 
        (student.retention_score || 0) + 
        (student.application_score || 0)
      ) / 4);
      
      return {
        name: student.full_name || student.username || `Student ${index + 1}`,
        score: avgScore,
        sessions: student.total_sessions || 0,
        accuracy: student.accuracy || avgScore
      };
    });
  };

  const getPerformanceDistributionData = () => {
    if (!studentsData || !Array.isArray(studentsData)) return [];
    
    const excellent = studentsData.filter((s) => s.accuracy >= 80).length;
    const good = studentsData.filter((s) => s.accuracy >= 60 && s.accuracy < 80).length;
    const needsWork = studentsData.filter((s) => s.accuracy < 60).length;
    
    return [
      { name: 'Excellent (≥80%)', value: excellent, color: '#00C49F' },
      { name: 'Good (60-79%)', value: good, color: '#FFBB28' },
      { name: 'Needs Support (<60%)', value: needsWork, color: '#FF8042' }
    ];
  };

  const tabs = [
    { key: 'system', label: 'System Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { key: 'students', label: 'Student Performance', icon: <Users className="w-4 h-4" /> },
    { key: 'sessions', label: 'Session Reports', icon: <Activity className="w-4 h-4" /> },
    { key: 'performance', label: 'Performance Trends', icon: <TrendingUp className="w-4 h-4" /> }
  ];

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-16 bg-muted rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Learning Analytics</h2>
          <p className="text-muted-foreground">Comprehensive insights into learning progress</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
            hasErrors ? 'bg-destructive/10 text-destructive' : 'bg-chart-4/10 text-chart-4'
          }`}>
            <div className={`w-2 h-2 rounded-full ${hasErrors ? 'bg-destructive' : 'bg-chart-4'}`}></div>
            <span>{hasErrors ? 'Issues detected' : 'Connected'}</span>
          </div>
          
          <div className="text-sm text-muted-foreground">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </div>
          
          <Button
            onClick={refreshAllData}
            disabled={loading}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
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
      {hasErrors && (
        <Card className="border-destructive/20 bg-destructive/5">
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-destructive mr-3" />
              <div className="flex-1">
                <h3 className="text-sm font-medium text-destructive">Connection Error</h3>
                <p className="text-sm text-destructive/80 mt-1">
                  Unable to fetch some data from the admin endpoints
                </p>
                <p className="text-sm text-destructive/60 mt-1">
                  Make sure the Django server is running on http://localhost:8000
                </p>
              </div>
              <Button
                onClick={refreshAllData}
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
      {activeTab === 'system' && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                    <p className="text-2xl font-bold text-foreground">{systemStats?.users?.total || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {systemStats?.users?.students || 0} students
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-primary/60" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Sessions</p>
                    <p className="text-2xl font-bold text-foreground">{systemStats?.sessions?.total || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {systemStats?.sessions?.today || 0} today
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-chart-4/60" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Questions Attempted</p>
                    <p className="text-2xl font-bold text-foreground">{systemStats?.questions?.total || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {systemStats?.questions?.today || 0} today
                    </p>
                  </div>
                  <BookOpen className="h-8 w-8 text-accent/60" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Active This Week</p>
                    <p className="text-2xl font-bold text-foreground">{systemStats?.users?.active_week || 0}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {systemStats?.sessions?.week || 0} sessions
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-secondary/60" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Subject Performance Chart */}
          {getSubjectPerformanceData().length > 0 && (
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-6">Subject Performance Overview</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={getSubjectPerformanceData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="subject" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="accuracy" fill="#0088FE" name="Accuracy %" />
                    <Bar dataKey="sessions" fill="#00C49F" name="Sessions" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'students' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Distribution */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-6">Performance Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getPerformanceDistributionData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {getPerformanceDistributionData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Top Performers */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-foreground mb-6">Top Performers</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={getStudentPerformanceData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={60} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#FFBB28" name="Average Score" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Student Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-chart-4 mb-2">
                  {getPerformanceDistributionData().find(d => d.name.includes('Excellent'))?.value || 0}
                </div>
                <div className="text-sm font-medium text-foreground">Excellent Students</div>
                <div className="text-xs text-muted-foreground">≥80% accuracy</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-accent mb-2">
                  {getPerformanceDistributionData().find(d => d.name.includes('Good'))?.value || 0}
                </div>
                <div className="text-sm font-medium text-foreground">Good Students</div>
                <div className="text-xs text-muted-foreground">60-79% accuracy</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-destructive mb-2">
                  {getPerformanceDistributionData().find(d => d.name.includes('Support'))?.value || 0}
                </div>
                <div className="text-sm font-medium text-foreground">Need Support</div>
                <div className="text-xs text-muted-foreground">&lt;60% accuracy</div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'sessions' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground mb-2">
                    {classOverview?.totalSessions || 0}
                  </div>
                  <div className="text-sm font-medium text-muted-foreground">Total Sessions</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-chart-4 mb-2">
                    {classOverview?.completedSessions || 0}
                  </div>
                  <div className="text-sm font-medium text-muted-foreground">Completed</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent mb-2">
                    {Math.round(classOverview?.averageAccuracy || 0)}%
                  </div>
                  <div className="text-sm font-medium text-muted-foreground">Avg Accuracy</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary mb-2">
                    {classOverview?.activeThisWeek || 0}
                  </div>
                  <div className="text-sm font-medium text-muted-foreground">Active This Week</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-6">Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Average Progress</span>
                      <span>{Math.round(classOverview?.average_progress || 0)}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-300"
                        style={{ width: `${classOverview?.average_progress || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Completion Rate</span>
                      <span>{Math.round(classOverview?.completion_rate || 0)}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="bg-chart-4 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${classOverview?.completion_rate || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Retention Rate</span>
                      <span>{Math.round(classOverview?.retention_rate || 0)}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div 
                        className="bg-accent h-2 rounded-full transition-all duration-300"
                        style={{ width: `${classOverview?.retention_rate || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="text-center p-4 bg-muted/20 rounded-lg">
                    <div className="text-lg font-bold text-foreground mb-1">
                      {classOverview?.weekly_study_hours || 0}h
                    </div>
                    <div className="text-sm text-muted-foreground">Weekly Study Time</div>
                  </div>
                  
                  <div className="text-center p-4 bg-primary/10 rounded-lg">
                    <div className="text-lg font-bold text-primary mb-1">
                      {studentsData?.length || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Students Tracked</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}