import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, UserCheck, TrendingUp, AlertTriangle, FileText, Megaphone, CalendarPlus } from "lucide-react";

// Type definitions for API responses
interface GapDistributionData {
  struggling: number;
  improving: number;
  mastered: number;
}

interface ClassOverviewResponse {
  totalStudents: number;
  activeThisWeek: number;
  totalSessions: number;
  completedSessions: number;
  averageAccuracy: number;
  recentActivity: number;
  lastUpdated: string;
  total_students: number;
  average_progress: number;
  completion_rate: number;
  retention_rate: number;
  weekly_study_hours: number;
  struggling_students: number;
  improving_students: number;
  excellent_students: number;
  sessionsToday?: number;
  sessionsThisWeek?: number;
  questionsTotal?: number;
  gap_distribution?: {
    listening: GapDistributionData;
    grasping: GapDistributionData;
    retention: GapDistributionData;
    application: GapDistributionData;
  };
}

interface StudentData {
  id: string;
  username: string;
  email?: string;
  full_name?: string;
  total_sessions: number;
  accuracy: number;
  listening_score: number;
  grasping_score: number;
  retention_score: number;
  application_score: number;
}

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

interface FrontendAdminData {
  student_count: number;
  system_stats: {
    total_students: number;
    total_questions: number;
    total_interactions: number;
    active_sessions: number;
    system_uptime: string;
  };
  question_bank_stats: Record<string, number>;
  algorithm_performance: Record<string, number>;
  recent_activities: any[];
  usage_analytics: Record<string, any>;
  // Additional properties that might be present
  totalStudents?: number;
  averageAccuracy?: number;
  completedSessions?: number;
  totalSessions?: number;
  activeThisWeek?: number;
}

export default function AdminOverview() {
  // ADMIN DASHBOARD - NOT STUDENT CONTENT
  console.log("🔧 AdminOverview: Rendering ADMIN content, NOT student content!");
  
  // Try primary admin endpoints first, fallback to frontend endpoint
  const { data: classOverview, isLoading: overviewLoading, error: overviewError } = useQuery<ClassOverviewResponse>({
    queryKey: ["/api/admin/class-overview"],
    retry: 1,
  });

  const { data: studentsData, isLoading: studentsLoading, error: studentsError } = useQuery<StudentData[]>({
    queryKey: ["/api/admin/students"],
    retry: 1,
  });

  // Fallback to frontend admin dashboard if main admin endpoints fail
  const { data: frontendAdminData, isLoading: frontendLoading } = useQuery<FrontendAdminData>({
    queryKey: ["/api/frontend/dashboard/admin"],
    enabled: !!overviewError || !!studentsError,
    retry: 1,
  });

  // Additional system stats endpoint
  const { data: systemStats } = useQuery<SystemStatsResponse>({
    queryKey: ["/api/admin/system-stats"],
    retry: 1,
  });

  // Debug logging
  console.log("AdminOverview Debug:", {
    classOverview,
    studentsData,
    frontendAdminData,
    systemStats,
    overviewLoading,
    studentsLoading,
    overviewError,
    studentsError
  });

  if (overviewLoading || studentsLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-6 bg-muted rounded w-1/4 mb-4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-muted rounded w-full"></div>
                <div className="h-4 bg-muted rounded w-3/4"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (overviewError || studentsError) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-destructive mb-2">Error Loading Data</h3>
              <p className="text-muted-foreground mb-4">
                {overviewError?.message || studentsError?.message || "Failed to load admin data"}
              </p>
              <Button onClick={() => window.location.reload()}>Reload Page</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Use real database data from multiple API sources
  const gapDistribution = classOverview?.gap_distribution || {
    listening: { struggling: 0, improving: 0, mastered: 0 },
    grasping: { struggling: 0, improving: 0, mastered: 0 },
    retention: { struggling: 0, improving: 0, mastered: 0 },
    application: { struggling: 0, improving: 0, mastered: 0 },
  };

  // Merge data from different endpoints for comprehensive stats
  const classStats = {
    totalStudents: classOverview?.total_students || 
                   classOverview?.totalStudents || 
                   frontendAdminData?.student_count || 
                   systemStats?.users?.students || 0,
    averageProgress: classOverview?.average_progress || 
                     classOverview?.averageAccuracy || 0,
    completionRate: classOverview?.completion_rate || 
                    classOverview?.completedSessions || 0,
    retentionRate: classOverview?.retention_rate || 
                   classOverview?.averageAccuracy || 0,
    studyTimeWeekly: classOverview?.weekly_study_hours || 0,
    strugglingStudents: classOverview?.struggling_students || 0,
    improvingStudents: classOverview?.improving_students || 0,
    excellentStudents: classOverview?.excellent_students || 0,
    
    // Additional stats from system endpoint
    totalSessions: systemStats?.sessions?.total || classOverview?.totalSessions || 0,
    sessionsToday: systemStats?.sessions?.today || 0,
    sessionsThisWeek: systemStats?.sessions?.week || classOverview?.activeThisWeek || 0,
    questionsTotal: systemStats?.questions?.total || frontendAdminData?.system_stats?.total_questions || 0,
  };

  const getStudentsByPriority = () => {
    if (!studentsData) {
      return {
        needsAttention: [],
        improving: [],
        excellent: []
      };
    }

    return studentsData.reduce((acc: any, student: any) => {
      const scores = [
        student.listening_score || 0,
        student.grasping_score || 0,
        student.retention_score || 0,
        student.application_score || 0,
      ];
      
      const avgScore = scores.reduce((sum: number, score: number) => sum + score, 0) / 4;
      const hasLowScore = scores.some((score: number) => score < 60);
      
      if (hasLowScore && avgScore < 60) {
        acc.needsAttention.push(student);
      } else if (avgScore >= 80) {
        acc.excellent.push(student);
      } else {
        acc.improving.push(student);
      }
      
      return acc;
    }, {
      needsAttention: [],
      improving: [],
      excellent: []
    });
  };

  const studentsByPriority = getStudentsByPriority();

  return (
    <div className="space-y-8">
      {/* ADMIN DASHBOARD HEADER - CLEAR IDENTIFICATION */}
      <div className="mb-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
            <Users className="h-4 w-4 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-foreground">🛠️ Admin Dashboard - Class Management</h2>
        </div>
        <p className="text-muted-foreground">Monitor class-wide performance, manage students, and analyze learning patterns</p>
        <div className="mt-2 text-xs text-blue-600">
          ✅ This is the ADMIN dashboard - showing class metrics, NOT personal student progress
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Students</p>
                <p className="text-2xl font-bold text-foreground">{classStats.totalStudents}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {systemStats?.users?.active_week || 0} active this week
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
                <p className="text-sm font-medium text-muted-foreground">Learning Sessions</p>
                <p className="text-2xl font-bold text-foreground">{classStats.totalSessions}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {classStats.sessionsToday} today, {classStats.sessionsThisWeek} this week
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-chart-4/60" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Completion Rate</p>
                <p className="text-2xl font-bold text-foreground">{Math.round(classStats.completionRate)}%</p>
                <p className="text-xs text-muted-foreground mt-1">Average accuracy: {Math.round(classStats.averageProgress)}%</p>
              </div>
              <UserCheck className="h-8 w-8 text-accent/60" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Questions Attempted</p>
                <p className="text-2xl font-bold text-foreground">{classStats.questionsTotal}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {systemStats?.questions?.today || 0} today
                </p>
              </div>
              <FileText className="h-8 w-8 text-secondary/60" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Subject Performance Breakdown */}
      {systemStats?.subjects && systemStats.subjects.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-6">Subject Performance</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {systemStats.subjects.map((subject: any, index: number) => (
                <div key={index} className="p-4 rounded-lg border border-border bg-muted/20">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-medium text-foreground capitalize">{subject.name}</h4>
                    <Badge variant={subject.accuracy >= 70 ? "default" : subject.accuracy >= 50 ? "secondary" : "destructive"}>
                      {Math.round(subject.accuracy)}%
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div className="flex justify-between">
                      <span>Sessions:</span>
                      <span>{subject.sessions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Questions:</span>
                      <span>{subject.questions_attempted}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Gap Analysis */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-6">Learning Gap Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(gapDistribution).map(([skill, data]) => (
              <div key={skill} className="space-y-3">
                <h4 className="font-medium text-foreground capitalize">{skill}</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Struggling</span>
                    <Badge variant="destructive" className="text-xs">
                      {(data as GapDistributionData).struggling}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Improving</span>
                    <Badge variant="secondary" className="text-xs">
                      {(data as GapDistributionData).improving}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Mastered</span>
                    <Badge variant="default" className="text-xs bg-chart-4 text-chart-4-foreground">
                      {(data as GapDistributionData).mastered}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Student Priority Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Students Needing Attention */}
        <Card className="border-destructive/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-destructive">Needs Attention</h3>
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <p className="text-2xl font-bold text-destructive mb-2">
              {studentsByPriority.needsAttention.length}
            </p>
            <p className="text-sm text-muted-foreground mb-4">students require support</p>
            <div className="space-y-2">
              {studentsByPriority.needsAttention.slice(0, 3).map((student: any, index: number) => (
                <div key={index} className="flex justify-between items-center text-sm">
                  <span>{student.full_name || `Student ${index + 1}`}</span>
                  <Badge variant="destructive" className="text-xs">
                    {Math.round((student.listening_score + student.grasping_score + student.retention_score + student.application_score) / 4) || 0}%
                  </Badge>
                </div>
              ))}
            </div>
            <Button variant="destructive" size="sm" className="w-full mt-4">
              <Megaphone className="h-4 w-4 mr-2" />
              Send Support Resources
            </Button>
          </CardContent>
        </Card>

        {/* Improving Students */}
        <Card className="border-accent/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-accent">Improving</h3>
              <TrendingUp className="h-5 w-5 text-accent" />
            </div>
            <p className="text-2xl font-bold text-accent mb-2">
              {studentsByPriority.improving.length}
            </p>
            <p className="text-sm text-muted-foreground mb-4">students making progress</p>
            <div className="space-y-2">
              {studentsByPriority.improving.slice(0, 3).map((student: any, index: number) => (
                <div key={index} className="flex justify-between items-center text-sm">
                  <span>{student.full_name || `Student ${index + 1}`}</span>
                  <Badge variant="secondary" className="text-xs bg-accent/10 text-accent">
                    {Math.round((student.listening_score + student.grasping_score + student.retention_score + student.application_score) / 4) || 0}%
                  </Badge>
                </div>
              ))}
            </div>
            <Button variant="outline" size="sm" className="w-full mt-4 border-accent text-accent">
              <CalendarPlus className="h-4 w-4 mr-2" />
              Schedule Check-in
            </Button>
          </CardContent>
        </Card>

        {/* Excellent Students */}
        <Card className="border-chart-4/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-chart-4">Excellent</h3>
              <UserCheck className="h-5 w-5 text-chart-4" />
            </div>
            <p className="text-2xl font-bold text-chart-4 mb-2">
              {studentsByPriority.excellent.length}
            </p>
            <p className="text-sm text-muted-foreground mb-4">students excelling</p>
            <div className="space-y-2">
              {studentsByPriority.excellent.slice(0, 3).map((student: any, index: number) => (
                <div key={index} className="flex justify-between items-center text-sm">
                  <span>{student.full_name || `Student ${index + 1}`}</span>
                  <Badge className="text-xs bg-chart-4 text-chart-4-foreground">
                    {Math.round((student.listening_score + student.grasping_score + student.retention_score + student.application_score) / 4) || 0}%
                  </Badge>
                </div>
              ))}
            </div>
            <Button variant="outline" size="sm" className="w-full mt-4 border-chart-4 text-chart-4">
              <TrendingUp className="h-4 w-4 mr-2" />
              Advanced Challenges
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}