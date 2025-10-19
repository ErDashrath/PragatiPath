import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { 
  Clock, 
  Users, 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  Play, 
  Pause, 
  StopCircle,
  BarChart3,
  RefreshCw,
  Timer,
  TrendingUp
} from "lucide-react";
// Using simple alert for notifications - replace with your preferred toast library
const toast = {
  success: (message: string) => alert(`✅ ${message}`),
  error: (message: string) => alert(`❌ ${message}`),
};
import { cn } from "../../lib/utils";

interface ExamStatus {
  id: number;
  title: string;
  status: 'scheduled' | 'active' | 'completed' | 'cancelled';
  start_time: string;
  end_time: string;
  duration_minutes: number;
  total_students: number;
  enrolled_students: number;
  active_students: number;
  completed_attempts: number;
  created_at: string;
  created_by: string;
}

interface LiveExamStats {
  exam_id: number;
  active_students: number;
  completed_students: number;
  avg_progress: number;
  avg_score: number;
  time_remaining: number;
  questions_answered: number;
  total_questions: number;
  last_activity: string;
}

interface StudentProgress {
  user_id: number;
  username: string;
  email: string;
  start_time: string;
  progress_percentage: number;
  current_question: number;
  total_questions: number;
  score: number;
  last_activity: string;
  time_spent: number;
  status: 'in_progress' | 'completed' | 'disconnected';
}

export function ExamMonitoringDashboard() {
  const [selectedExam, setSelectedExam] = useState<number | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const queryClient = useQueryClient();

  // Fetch all active and scheduled exams
  const { data: exams, isLoading: examsLoading, refetch: refetchExams } = useQuery({
    queryKey: ["admin-exams-monitoring"],
    queryFn: async (): Promise<ExamStatus[]> => {
      const response = await fetch("/api/admin/exams/monitoring/", {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to fetch exams");
      return await response.json();
    },
    refetchInterval: autoRefresh ? 30000 : false, // Refresh every 30 seconds
  });

  // Fetch live stats for selected exam
  const { data: liveStats, isLoading: statsLoading } = useQuery({
    queryKey: ["exam-live-stats", selectedExam],
    queryFn: async (): Promise<LiveExamStats | null> => {
      if (!selectedExam) return null;
      const response = await fetch(`/api/admin/exams/${selectedExam}/live-stats/`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to fetch live stats");
      return await response.json();
    },
    enabled: !!selectedExam,
    refetchInterval: autoRefresh ? 10000 : false, // Refresh every 10 seconds
  });

  // Fetch student progress for selected exam
  const { data: studentProgress, isLoading: progressLoading } = useQuery({
    queryKey: ["exam-student-progress", selectedExam],
    queryFn: async (): Promise<StudentProgress[]> => {
      if (!selectedExam) return [];
      const response = await fetch(`/api/admin/exams/${selectedExam}/student-progress/`, {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to fetch student progress");
      return await response.json();
    },
    enabled: !!selectedExam,
    refetchInterval: autoRefresh ? 15000 : false, // Refresh every 15 seconds
  });

  // Exam control mutations
  const activateExamMutation = useMutation({
    mutationFn: async (examId: number) => {
      const response = await fetch(`/api/admin/exams/${examId}/activate/`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to activate exam");
      return response.json();
    },
    onSuccess: () => {
      toast.success("Exam activated successfully");
      queryClient.invalidateQueries({ queryKey: ["admin-exams-monitoring"] });
      queryClient.invalidateQueries({ queryKey: ["exam-live-stats"] });
    },
    onError: () => {
      toast.error("Failed to activate exam");
    },
  });

  const endExamMutation = useMutation({
    mutationFn: async (examId: number) => {
      const response = await fetch(`/api/admin/exams/${examId}/end/`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to end exam");
      return response.json();
    },
    onSuccess: () => {
      toast.success("Exam ended successfully");
      queryClient.invalidateQueries({ queryKey: ["admin-exams-monitoring"] });
      queryClient.invalidateQueries({ queryKey: ["exam-live-stats"] });
    },
    onError: () => {
      toast.error("Failed to end exam");
    },
  });

  // Auto-refresh control
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refetchExams();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refetchExams]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled': return <Clock className="h-4 w-4" />;
      case 'active': return <Activity className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'cancelled': return <AlertCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const formatTimeRemaining = (minutes: number) => {
    if (minutes <= 0) return "Ended";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (examsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Exam Monitoring Dashboard</h1>
          <div className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            <span className="text-sm text-muted-foreground">Loading...</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-full"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Exam Monitoring Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Label htmlFor="auto-refresh">Auto Refresh</Label>
            <Button
              variant={autoRefresh ? "default" : "outline"}
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCw className={cn("h-4 w-4", autoRefresh && "animate-spin")} />
            </Button>
          </div>
          <Button onClick={() => refetchExams()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Now
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Exams</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{exams?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Exams</CardTitle>
            <Activity className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {exams?.filter(exam => exam.status === 'active').length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Exams</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {exams?.filter(exam => exam.status === 'scheduled').length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Students</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {exams?.reduce((sum, exam) => sum + exam.enrolled_students, 0) || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Exams List */}
      <Card>
        <CardHeader>
          <CardTitle>Exam Status Overview</CardTitle>
          <CardDescription>
            Real-time monitoring of all scheduled and active exams
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {exams?.map((exam) => (
              <div
                key={exam.id}
                className={cn(
                  "p-4 border rounded-lg cursor-pointer transition-colors",
                  selectedExam === exam.id ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:bg-gray-50"
                )}
                onClick={() => setSelectedExam(exam.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(exam.status)}
                    <div>
                      <h3 className="font-semibold">{exam.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {new Date(exam.start_time).toLocaleString()} - {formatTimeRemaining(exam.duration_minutes)} duration
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Badge className={getStatusColor(exam.status)}>
                      {exam.status.charAt(0).toUpperCase() + exam.status.slice(1)}
                    </Badge>
                    <div className="text-right">
                      <p className="text-sm font-medium">{exam.active_students}/{exam.enrolled_students} active</p>
                      <p className="text-xs text-muted-foreground">{exam.completed_attempts} completed</p>
                    </div>
                    {exam.status === 'scheduled' && (
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          activateExamMutation.mutate(exam.id);
                        }}
                        disabled={activateExamMutation.isPending}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Activate
                      </Button>
                    )}
                    {exam.status === 'active' && (
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          endExamMutation.mutate(exam.id);
                        }}
                        disabled={endExamMutation.isPending}
                      >
                        <StopCircle className="h-4 w-4 mr-1" />
                        End
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Live Statistics for Selected Exam */}
      {selectedExam && liveStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Students</CardTitle>
              <Users className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{liveStats.active_students}</div>
              <p className="text-xs text-muted-foreground">
                {liveStats.completed_students} completed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{liveStats.avg_progress.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                {liveStats.questions_answered}/{liveStats.total_questions} questions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <BarChart3 className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{liveStats.avg_score.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                Current average
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Remaining</CardTitle>
              <Timer className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {formatTimeRemaining(liveStats.time_remaining)}
              </div>
              <p className="text-xs text-muted-foreground">
                Last activity: {new Date(liveStats.last_activity).toLocaleTimeString()}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Student Progress Table */}
      {selectedExam && studentProgress && studentProgress.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Student Progress</CardTitle>
            <CardDescription>
              Real-time progress tracking for all students taking the exam
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Student</th>
                    <th className="text-left py-2 px-3">Progress</th>
                    <th className="text-left py-2 px-3">Score</th>
                    <th className="text-left py-2 px-3">Time Spent</th>
                    <th className="text-left py-2 px-3">Last Activity</th>
                    <th className="text-left py-2 px-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {studentProgress.map((student) => (
                    <tr key={student.user_id} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-3">
                        <div>
                          <p className="font-medium">{student.username}</p>
                          <p className="text-xs text-muted-foreground">{student.email}</p>
                        </div>
                      </td>
                      <td className="py-2 px-3">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all"
                              style={{ width: `${student.progress_percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{student.progress_percentage.toFixed(1)}%</span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {student.current_question}/{student.total_questions} questions
                        </p>
                      </td>
                      <td className="py-2 px-3">
                        <span className="font-medium">{student.score.toFixed(1)}%</span>
                      </td>
                      <td className="py-2 px-3">
                        <span className="text-sm">{formatDuration(student.time_spent)}</span>
                      </td>
                      <td className="py-2 px-3">
                        <span className="text-sm">
                          {new Date(student.last_activity).toLocaleTimeString()}
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        <Badge className={cn(
                          student.status === 'in_progress' && 'bg-green-100 text-green-800',
                          student.status === 'completed' && 'bg-blue-100 text-blue-800',
                          student.status === 'disconnected' && 'bg-red-100 text-red-800'
                        )}>
                          {student.status.replace('_', ' ')}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!exams || exams.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Exams Found</h3>
            <p className="text-muted-foreground">
              Create your first exam to start monitoring student progress.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}