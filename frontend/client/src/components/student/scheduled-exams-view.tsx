import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Calendar,
  Clock, 
  FileText, 
  AlertCircle, 
  CheckCircle, 
  Play,
  Eye,
  Timer,
  BookOpen,
  Target,
  TrendingUp,
  Users
} from "lucide-react";
import { format, formatDistanceToNow, isAfter, isBefore } from "date-fns";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest } from "@/lib/queryClient";

// Enhanced types for student exam view with new schema
interface EnhancedStudentExam {
  id: string;
  exam_name: string;
  subject_name: string;
  subject_code: string;
  chapters: string[];
  scheduled_start_time: string | null;
  scheduled_end_time: string | null;
  duration_minutes: number;
  question_count: number;
  status: "draft" | "upcoming" | "active" | "available" | "completed" | "cancelled";
  content_selection: {
    subject_id: number;
    selection_type: string;
    chapter_ids?: number[];
    difficulty_levels?: string[];
  };
  question_pool: {
    total_available: number;
    selected_count: number;
    difficulty_breakdown: Record<string, number>;
    estimated_duration: number;
  };
  created_by: string;
  created_at: string;
  // Runtime calculated fields
  can_start?: boolean;
  time_until_start?: number;
  is_active?: boolean;
  exam_type?: string;
}

interface StudentExamAttempt {
  id: string;
  attempt_number: number;
  status: string;
  started_at: string | null;
  submitted_at: string | null;
  final_score_percentage: number;
  passed: boolean;
  grade: string;
  total_time_minutes: number;
  questions_attempted: number;
  questions_answered: number;
  correct_answers: number;
}

interface ScheduledExamsViewProps {
  onStartExam: (examSessionId: string, examName: string) => void;
}

export default function ScheduledExamsView({ onStartExam }: ScheduledExamsViewProps) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [currentTime, setCurrentTime] = useState(new Date());

  console.log("🎯 ScheduledExamsView component mounted! User:", user?.username);

  // Fetch available enhanced exams for current user
  const { data: exams = [], isLoading, refetch, error } = useQuery({
    queryKey: ["enhancedStudentExams"],
    queryFn: async (): Promise<EnhancedStudentExam[]> => {
      try {
        console.log("🔄 Starting exam fetch...");
        const response = await apiRequest("GET", "http://localhost:8000/api/enhanced-exam/student/exams/available");
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("📚 Scheduled Exams Query - Raw data:", data);
        console.log("📚 Scheduled Exams Query - Array check:", Array.isArray(data));
        
        let result: EnhancedStudentExam[] = [];
        if (Array.isArray(data)) {
          result = data;
        } else if (data.data && Array.isArray(data.data)) {
          result = data.data;
        } else if (data.success && data.data && Array.isArray(data.data)) {
          result = data.data;
        } else {
          console.warn("📚 Unexpected data format:", data);
          result = [];
        }
        
        console.log("📚 Scheduled Exams Query - Final result:", result);
        console.log("🔄 Query completed successfully, returning", result.length, "exams");
        return result;
      } catch (error) {
        console.error("❌ Query failed:", error);
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    retry: 3, // Retry failed requests 3 times
  });

  // Update current time every minute for countdown timers
  useEffect(() => {
    console.log("🎯 ScheduledExamsView useEffect triggered");
    const interval = setInterval(() => {
      setCurrentTime(new Date());
      // Auto-refresh exam data every 5 minutes to catch status changes
      if (Date.now() % (5 * 60 * 1000) < 60000) {
        refetch();
      }
    }, 60000);
    return () => clearInterval(interval);
  }, [refetch]);

  // Fetch student's exam attempts
  const { data: attempts = [] } = useQuery({
    queryKey: ["studentExamAttempts", user?.id],
    queryFn: async (): Promise<StudentExamAttempt[]> => {
      if (!user?.id) return [];
      const response = await apiRequest("GET", `http://localhost:8000/api/enhanced-exam/student/${user.id}/attempts`);
      const data = await response.json();
      return Array.isArray(data) ? data : data.data || [];
    },
    enabled: !!user?.id,
  });

  // Debug effect to track query state changes
  useEffect(() => {
    console.log("🔍 Query state changed:", {
      isLoading,
      hasData: exams.length > 0,
      error,
      user: user ? { id: user.id, username: user.username } : null,
      timestamp: new Date().toISOString()
    });
  }, [isLoading, exams.length, error, user]);

  // Start exam mutation
  const startExamMutation = useMutation({
    mutationFn: async (examId: string) => {
      const response = await apiRequest("POST", `http://localhost:8000/api/enhanced-exam/student/exams/${examId}/start`);
      return await response.json();
    },
    onSuccess: (data, examId) => {
      const exam = exams.find(e => e.id === examId);
      if (data.success && data.attempt_id && exam) {
        onStartExam(data.attempt_id, exam.exam_name);
        queryClient.invalidateQueries({ queryKey: ["studentExamAttempts"] });
      }
    },
    onError: (error: Error) => {
      alert(error.message);
    },
  });

  // Calculate exam status with current time
  const calculateExamStatus = (exam: EnhancedStudentExam) => {
    const now = currentTime;
    const hasAttempt = attempts.some(attempt => 
      attempt.id.includes(exam.id) && attempt.status === 'COMPLETED'
    );

    if (hasAttempt) return "completed";
    
    if (exam.scheduled_start_time) {
      const startTime = new Date(exam.scheduled_start_time);
      const endTime = exam.scheduled_end_time ? new Date(exam.scheduled_end_time) : null;
      
      if (isBefore(now, startTime)) return "upcoming";
      if (endTime && isAfter(now, endTime)) return "expired";
      return "available";
    }
    
    return exam.status === "active" ? "available" : exam.status;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "upcoming": return <Clock className="h-4 w-4 text-blue-500" />;
      case "available": return <Play className="h-4 w-4 text-green-500" />;
      case "in_progress": return <Timer className="h-4 w-4 text-orange-500" />;
      case "completed": return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "expired": return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <Calendar className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "upcoming": return "bg-blue-100 text-blue-800";
      case "available": return "bg-green-100 text-green-800";
      case "in_progress": return "bg-orange-100 text-orange-800";
      case "completed": return "bg-green-100 text-green-800";
      case "expired": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusMessage = (exam: EnhancedStudentExam) => {
    const status = calculateExamStatus(exam);
    
    switch (status) {
      case "upcoming":
        if (exam.scheduled_start_time) {
          return `Starts ${formatDistanceToNow(new Date(exam.scheduled_start_time), { addSuffix: true })}`;
        }
        return "Upcoming";
      case "available":
        return "Ready to start";
      case "completed":
        return "Completed";
      case "expired":
        return "Expired";
      default:
        return "Available";
    }
  };

  const handleStartExam = (exam: EnhancedStudentExam) => {
    const status = calculateExamStatus(exam);
    if (status !== "available") return;
    
    startExamMutation.mutate(exam.id);
  };

  // Group exams by status
  const examsWithStatus = exams.map(exam => ({
    ...exam,
    calculatedStatus: calculateExamStatus(exam)
  }));
  
  console.log("📊 Exams with status:", examsWithStatus);

  const availableExams = examsWithStatus.filter(exam => exam.calculatedStatus === "available");
  const upcomingExams = examsWithStatus.filter(exam => exam.calculatedStatus === "upcoming");
  const completedExams = examsWithStatus.filter(exam => exam.calculatedStatus === "completed");
  const expiredExams = examsWithStatus.filter(exam => exam.calculatedStatus === "expired");
  
  console.log("📊 Available exams:", availableExams.length);
  console.log("📊 Upcoming exams:", upcomingExams.length);

  console.log("🎯 ScheduledExamsView render - isLoading:", isLoading, "exams.length:", exams.length, "error:", error);

  if (error) {
    console.error("❌ Query error:", error);
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-lg text-red-600">Error loading exams</div>
          <div className="text-sm text-muted-foreground mt-2">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </div>
          <Button onClick={() => refetch()} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    console.log("🎯 Rendering loading state");
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-lg text-muted-foreground">Loading enhanced exams...</div>
          <div className="text-sm text-muted-foreground mt-2">Please wait while we fetch your exams</div>
        </div>
      </div>
    );
  }

  console.log("🎯 Rendering main content - Available:", availableExams.length, "Upcoming:", upcomingExams.length);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Enhanced Scheduled Exams</h2>
          <p className="text-sm text-muted-foreground">
            View and take your enhanced scheduled exams with adaptive features
          </p>
        </div>
        <Button 
          variant="outline" 
          onClick={() => refetch()}
          className="flex items-center gap-2"
          disabled={isLoading}
        >
          <Clock className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Available Exams (Priority) */}
      {availableExams.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-green-700 flex items-center gap-2">
            <Play className="h-5 w-5" />
            Available to Start
          </h3>
          {availableExams.map((exam) => (
            <Card key={exam.id} className="border-green-200 bg-green-50">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(exam.calculatedStatus)}
                      <h4 className="font-semibold text-lg">{exam.exam_name}</h4>
                      <Badge className={getStatusColor(exam.calculatedStatus)}>
                        {getStatusMessage(exam)}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        {exam.subject_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {exam.duration_minutes} minutes
                      </span>
                      <span className="flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        {exam.question_count} questions
                      </span>
                      {exam.chapters.length > 0 && (
                        <span className="flex items-center gap-1">
                          <Target className="h-3 w-3" />
                          {exam.chapters.length} chapters
                        </span>
                      )}
                    </div>

                    {exam.scheduled_start_time && exam.scheduled_end_time && (
                      <div className="text-sm">
                        <strong>Schedule:</strong> {format(new Date(exam.scheduled_start_time), "MMM dd, yyyy 'at' h:mm a")} - {format(new Date(exam.scheduled_end_time), "h:mm a")}
                      </div>
                    )}

                    {exam.chapters.length > 0 && (
                      <div className="text-sm">
                        <strong>Chapters:</strong> {exam.chapters.join(", ")}
                      </div>
                    )}

                    {exam.content_selection.difficulty_levels && (
                      <div className="text-sm">
                        <strong>Difficulty:</strong> {exam.content_selection.difficulty_levels.join(", ")}
                      </div>
                    )}
                  </div>

                  <Button
                    onClick={() => handleStartExam(exam)}
                    disabled={startExamMutation.isPending}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    {startExamMutation.isPending ? "Starting..." : "Start Exam"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upcoming Exams */}
      {upcomingExams.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-blue-700 flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Upcoming Exams
          </h3>
          {upcomingExams.map((exam) => (
            <Card key={exam.id} className="border-blue-200">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(exam.calculatedStatus)}
                      <h4 className="font-semibold text-lg">{exam.exam_name}</h4>
                      <Badge className={getStatusColor(exam.calculatedStatus)}>
                        {getStatusMessage(exam)}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                      <span>{exam.subject_name}</span>
                      <span>{exam.duration_minutes} minutes</span>
                      <span>{exam.question_count} questions</span>
                      {exam.chapters.length > 0 && (
                        <span>{exam.chapters.length} chapters</span>
                      )}
                    </div>

                    {exam.scheduled_start_time && (
                      <div className="text-sm">
                        <strong>Starts:</strong> {format(new Date(exam.scheduled_start_time), "MMM dd, yyyy 'at' h:mm a")}
                      </div>
                    )}

                    {exam.chapters.length > 0 && (
                      <div className="text-sm text-muted-foreground">
                        Chapters: {exam.chapters.join(", ")}
                      </div>
                    )}
                  </div>

                  <Button variant="outline" disabled>
                    <Clock className="h-4 w-4 mr-2" />
                    Not Yet Available
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Completed Exams */}
      {completedExams.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-green-700 flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Completed Exams
          </h3>
          {completedExams.map((exam) => {
            const examAttempt = attempts.find(attempt => 
              attempt.id.includes(exam.id) && attempt.status === 'COMPLETED'
            );
            
            return (
              <Card key={exam.id} className="border-green-200">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(exam.calculatedStatus)}
                        <h4 className="font-semibold text-lg">{exam.exam_name}</h4>
                        <Badge className={getStatusColor(exam.calculatedStatus)}>
                          Completed
                        </Badge>
                        {examAttempt && examAttempt.passed && (
                          <Badge className="bg-green-100 text-green-800">
                            Passed ({examAttempt.grade})
                          </Badge>
                        )}
                      </div>
                      
                      <div className="text-sm text-muted-foreground">
                        {exam.subject_name} • {exam.question_count} questions
                        {examAttempt && (
                          <span> • Score: {examAttempt.final_score_percentage.toFixed(1)}%</span>
                        )}
                      </div>

                      {examAttempt && (
                        <div className="text-sm text-muted-foreground">
                          Completed on {format(new Date(examAttempt.submitted_at || examAttempt.started_at || exam.created_at), "MMM dd, yyyy")}
                          • Time taken: {examAttempt.total_time_minutes.toFixed(1)} minutes
                        </div>
                      )}
                    </div>

                    <Button variant="outline">
                      <Eye className="h-4 w-4 mr-2" />
                      View Results
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Statistics Card */}
      {exams.length > 0 && (
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Your Exam Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{exams.length}</div>
                <div className="text-sm text-muted-foreground">Total Exams</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{completedExams.length}</div>
                <div className="text-sm text-muted-foreground">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{availableExams.length}</div>
                <div className="text-sm text-muted-foreground">Available</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{upcomingExams.length}</div>
                <div className="text-sm text-muted-foreground">Upcoming</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {exams.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">No Enhanced Exams Available</h3>
            <p className="text-muted-foreground mb-4">
              You don't have any scheduled exams at the moment. Check back later or contact your instructor.
            </p>
            <Button onClick={() => refetch()} variant="outline">
              <Clock className="h-4 w-4 mr-2" />
              Check for New Exams
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Expired Exams Alert */}
      {expiredExams.length > 0 && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertCircle className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-800">
            You have {expiredExams.length} expired exam{expiredExams.length > 1 ? 's' : ''}. 
            Please contact your instructor if you need to take these exams.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}