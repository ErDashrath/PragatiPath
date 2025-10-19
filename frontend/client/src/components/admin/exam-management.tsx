import React, { useState, ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Checkbox } from "../ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Badge } from "../ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { CalendarDays, Clock, Users, BookOpen, Settings, BarChart3 } from "lucide-react";
import { DebugSubjectsAPI } from "../debug/debug-subjects-api";

// Utility functions for Indian timezone handling
const getIndianTime = () => {
  return new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));
};

const getIndianTimeISO = () => {
  const indianTime = new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));
  return indianTime.toISOString();
};

const formatDatetimeLocalValue = (date: Date) => {
  // Convert to Indian time for display
  const indianTime = new Date(date.toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));
  // Format as required by datetime-local input (YYYY-MM-DDTHH:MM)
  return indianTime.toISOString().slice(0, 16);
};

const parseLocalDatetime = (localDatetimeValue: string) => {
  // Parse the local datetime value and treat it as Indian time
  const date = new Date(localDatetimeValue);
  return date;
};

// Enhanced Types
interface EnhancedSubject {
  id: number;
  name: string;
  code: string;
  total_chapters: number;
  total_questions: number;
  difficulty_distribution: {
    easy: number;
    medium: number;
    hard: number;
  };
  chapters: EnhancedChapter[];
}

interface EnhancedChapter {
  chapter_number: ReactNode;
  id: number;
  name: string;
  question_count: number;
  difficulty_distribution: {
    very_easy: number;
    easy: number;
    medium: number;
    hard: number;
  };
}

interface ContentSelection {
  selection_type: "full_subject" | "specific_chapters";
  subject_id: number | null;
  chapter_ids: number[];
  difficulty_levels: string[];
  question_types: string[];
  adaptive_difficulty: boolean;
}

interface EnhancedCreateExamForm {
  exam_name: string;
  description: string;
  content_selection: ContentSelection;
  scheduled_start_time: Date;
  duration_minutes: number;
  question_count: number;
  time_warnings: number[];
  enrolled_students: number[];
  auto_assign_all_active: boolean;
  randomize_questions: boolean;
  allow_question_navigation: boolean;
  show_question_feedback: boolean;
  allow_question_review: boolean;
  auto_submit_on_expiry: boolean;
  proctoring_enabled: boolean;
  detailed_analytics: boolean;
  adaptive_config: Record<string, any>;
}

interface EnhancedScheduledExam {
  id: string;
  title: string;
  description?: string;
  subjects: Array<{id: number; name: string;}>;
  question_count: number;
  start_time: string;
  duration_minutes: number;
  enrolled_students: number;
  active_students: number;
  completed_students: number;
  status: string;
  created_at: string;
  created_by: string;
}

interface QuestionPoolInfo {
  available_questions: number;
  requested_questions: number;
  is_sufficient: boolean;
  difficulty_breakdown: {
    easy: number;
    medium: number;
    hard: number;
  };
  recommendations: string[];
}

export default function ExamManagement() {
  const [selectedTab, setSelectedTab] = useState("exams");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedExam, setSelectedExam] = useState<EnhancedScheduledExam | null>(null);
  const [isEnrollDialogOpen, setIsEnrollDialogOpen] = useState(false);
  const [questionPool, setQuestionPool] = useState<QuestionPoolInfo | null>(null);
  const [forceUpdate, setForceUpdate] = useState(0); // Force re-render trigger
  const queryClient = useQueryClient();

  // Simplified exam form state
  const [createForm, setCreateForm] = useState({
    exam_name: "",
    description: "",
    exam_type: "adaptive_subject" as "adaptive_subject" | "practice_chapter",
    subject_id: null as number | null,
    chapter_ids: [] as number[],
    scheduled_start_time: new Date(getIndianTime().getTime() + 60 * 60 * 1000), // Default to 1 hour from current Indian time
    duration_minutes: 60,
    question_count: 20
  });

  // Enhanced API Queries
  const { data: exams = [], isLoading: examsLoading } = useQuery({
    queryKey: ["enhanced-exams"],
    queryFn: async (): Promise<EnhancedScheduledExam[]> => {
      const response = await fetch("http://localhost:8000/api/v1/enhanced-exam/admin/exams/scheduled/");
      if (!response.ok) throw new Error("Failed to fetch enhanced exams");
      const data = await response.json();
      return data.success ? data.data : (Array.isArray(data) ? data : []);
    }
  });

  // Fetch enhanced subjects with detailed info
  const { data: subjectsResponse, isLoading: isLoadingSubjects, error: subjectsError, refetch: refetchSubjects } = useQuery({
    queryKey: ["enhanced-subjects"],
    queryFn: async () => {
      console.log("🔍 TanStack Query: Fetching subjects from API...");
      const url = "http://localhost:8000/api/multi-student/subjects/";
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch subjects: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("🔍 TanStack Query: Raw response:", data);
      console.log("🔍 TanStack Query: Is Array?", Array.isArray(data));
      
      return data;
    },
    retry: 2,
    retryDelay: 1000,
    refetchOnWindowFocus: false,
    staleTime: 0, // Always fetch fresh data for debugging
  });

  // Extract subjects array from response  
  const subjects = Array.isArray(subjectsResponse) 
    ? subjectsResponse 
    : Array.isArray(subjectsResponse?.data) 
      ? subjectsResponse.data
      : [];
  
  // Debug: Log subjects data
  console.log("🔍 TanStack Query States:");
  console.log("  - isLoading:", isLoadingSubjects);
  console.log("  - error:", subjectsError);
  console.log("  - subjectsResponse type:", typeof subjectsResponse);
  console.log("  - subjectsResponse:", subjectsResponse);
  console.log("  - subjects extracted:", subjects);
  console.log("  - subjects type:", typeof subjects);
  console.log("  - subjects.length:", subjects?.length);
  console.log("  - Array.isArray(subjects):", Array.isArray(subjects));
  
  // Get current selected subject data for chapter loading
  const selectedSubject = Array.isArray(subjects) 
    ? subjects.find((s: any) => s.id === createForm.subject_id)
    : undefined;

  // Fetch chapters dynamically for selected subject
  const { data: chapters = [], isLoading: isLoadingChapters } = useQuery({
    queryKey: ["subject-chapters", createForm.subject_id],
    queryFn: async () => {
      if (!createForm.subject_id) return [];
      
      const response = await fetch(`http://localhost:8000/api/multi-student/subjects/${createForm.subject_id}/chapters/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch chapters: ${response.status}`);
      }
      
      const chaptersData = await response.json();
      console.log("🔍 Chapters API response:", chaptersData);
      return Array.isArray(chaptersData) ? chaptersData : [];
    },
    enabled: !!createForm.subject_id,
    retry: 2,
    retryDelay: 1000,
  });
  
  // Validate question pool when form data changes (disabled for now since endpoint doesn't exist yet)
  const { data: questionPoolData } = useQuery({
    queryKey: ["question-pool", createForm.subject_id, createForm.exam_type],
    queryFn: async () => {
      // For now, return a basic validation based on selected subject
      if (!createForm.subject_id || !selectedSubject) return null;
      
      // Only show validation if we have detailed question data
      if (!selectedSubject.total_questions) return null;
      
      const totalQuestions = selectedSubject.total_questions;
      const requestedQuestions = createForm.question_count;
      
      return {
        available_questions: totalQuestions,
        requested_questions: requestedQuestions,
        is_sufficient: totalQuestions >= requestedQuestions,
        difficulty_breakdown: selectedSubject.difficulty_distribution || {},
        recommendations: totalQuestions < requestedQuestions 
          ? [`Reduce question count to ${totalQuestions} or select additional chapters`]
          : []
      };
    },
    enabled: !!createForm.subject_id && !!selectedSubject && !!selectedSubject.total_questions
  });

  // Fetch students for enrollment (simplified for now)
  const { data: students = [] } = useQuery({
    queryKey: ["students"],
    queryFn: async () => {
      // For now, return empty array since we don't have a students endpoint
      // This can be implemented later when needed
      return [];
    }
  });

  // Create simplified exam mutation  
  const createExamMutation = useMutation({
    mutationFn: async (examData: typeof createForm) => {
      // Create exam payload matching backend API expectations
      const payload: any = {
        title: examData.exam_name, // Backend expects 'title' not 'exam_name'
        start_time: examData.scheduled_start_time.toISOString(), // Backend expects 'start_time'
        duration_minutes: examData.duration_minutes,
        question_count: examData.question_count,
        subjects: examData.subject_id ? [examData.subject_id] : [], // Backend expects array of subject IDs
        auto_activate: false, // Created as inactive, admin needs to activate manually
        pass_threshold: 70,
        max_attempts: 1,
        is_randomized: true
      };

      // Add description and exam type info for internal tracking
      if (examData.description) {
        payload.description = examData.description;
      }
      
      // Add chapter-specific data if practice_chapter type
      if (examData.exam_type === "practice_chapter" && examData.chapter_ids.length > 0) {
        payload.chapters = examData.chapter_ids;
      }

      const response = await fetch("http://localhost:8000/api/v1/enhanced-exam/admin/exams/schedule/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.message || "Failed to schedule exam");
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
      setIsCreateDialogOpen(false);
      resetCreateForm();
      
      // Show success message with broadcasting info - use backend response structure
      const examTitle = data.title || data.exam_name || createForm.exam_name;
      const startTime = data.start_time || data.scheduled_start_time;
      
      alert(`✅ Exam "${examTitle}" scheduled successfully!\n\n` +
            `📅 Start Time: ${startTime ? new Date(startTime).toLocaleString() : 'As scheduled'}\n` +
            `👥 Students will see this when activated\n` +
            `🔔 Use "Activate" button to broadcast to students`);
    },
    onError: (error: Error) => {
      alert(`❌ Failed to schedule exam: ${error.message}`);
    }
  });

  // Activate exam mutation for manual activation
  const activateExamMutation = useMutation({
    mutationFn: async (examId: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/enhanced-exam/admin/exams/${examId}/activate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.message || "Failed to activate exam");
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
      alert(`✅ ${data.message}\n🔔 Students have been notified automatically!`);
    },
    onError: (error: Error) => {
      alert(`❌ Failed to activate exam: ${error.message}`);
    }
  });

  // End exam mutation for manual ending
  const endExamMutation = useMutation({
    mutationFn: async (examId: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/enhanced-exam/admin/exams/${examId}/end/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.message || "Failed to end exam");
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
      alert(`✅ ${data.message}\n📊 Results are being processed automatically!`);
    },
    onError: (error: Error) => {
      alert(`❌ Failed to end exam: ${error.message}`);
    }
  });

  // Delete exam mutation
  const deleteExamMutation = useMutation({
    mutationFn: async (examId: string) => {
      // TODO: Implement delete endpoint in API
      console.log("Delete exam functionality not yet implemented:", examId);
      throw new Error("Delete functionality coming soon");
      
      const response = await fetch(`http://localhost:8000/api/v1/enhanced-exam/admin/exams/${examId}/delete/`, {
        method: "DELETE",
      });
      
      if (!response.ok) {
        throw new Error("Failed to delete exam");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
    },
  });

  const resetCreateForm = () => {
    setCreateForm({
      exam_name: "",
      description: "",
      exam_type: "adaptive_subject",
      subject_id: null,
      chapter_ids: [],
      scheduled_start_time: new Date(getIndianTime().getTime() + 60 * 60 * 1000), // 1 hour from current Indian time
      duration_minutes: 60,
      question_count: 20
    });
  };

  const handleCreateExam = () => {
    // Form validation
    if (!createForm.exam_name.trim()) {
      alert("❌ Please enter an exam name");
      return;
    }
    
    if (!createForm.subject_id) {
      alert("❌ Please select a subject");
      return;
    }
    
    if (createForm.question_count < 1) {
      alert("❌ Question count must be at least 1");
      return;
    }
    
    if (createForm.duration_minutes < 1) {
      alert("❌ Duration must be at least 1 minute");
      return;
    }
    
    if (createForm.scheduled_start_time <= getIndianTime()) {
      alert("❌ Scheduled start time must be in the future (India time)");
      return;
    }
    
    if (createForm.exam_type === "practice_chapter" && 
        createForm.chapter_ids.length === 0) {
      alert("❌ Please select at least one chapter for practice chapter exam");
      return;
    }
    
    if (createForm.exam_type === "practice_chapter" && 
        isLoadingChapters) {
      alert("❌ Please wait for chapters to load before creating the exam");
      return;
    }

    // All validations passed, submit the form
    createExamMutation.mutate(createForm);
  };

  const handleDeleteExam = (examId: string) => {
    if (confirm("Are you sure you want to delete this exam?")) {
      deleteExamMutation.mutate(examId);
    }
  };

  const handleSubjectChange = (subjectId: string) => {
    const id = parseInt(subjectId);
    setCreateForm(prev => ({
      ...prev,
      subject_id: id,
      chapter_ids: [] // Reset chapters when subject changes
    }));
  };

  const handleChapterToggle = (chapterId: number, checked: boolean) => {
    setCreateForm(prev => ({
      ...prev,
      chapter_ids: checked 
        ? [...prev.chapter_ids, chapterId]
        : prev.chapter_ids.filter(id => id !== chapterId)
    }));
  };



  return (
    <div className="container mx-auto p-6">
      {/* Debug Component - Remove in production */}
      <DebugSubjectsAPI />
      
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Enhanced Exam Management</h1>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>Create Enhanced Exam</Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Enhanced Exam</DialogTitle>
              <DialogDescription>
                Configure your exam with advanced options and dynamic content selection
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="exam_name">Exam Name</Label>
                  <Input
                    id="exam_name"
                    value={createForm.exam_name}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, exam_name: e.target.value }))}
                    placeholder="Enter exam name"
                  />
                </div>
                <div>
                  <Label htmlFor="question_count">Question Count</Label>
                  <Input
                    id="question_count"
                    type="number"
                    value={createForm.question_count}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, question_count: parseInt(e.target.value) }))}
                    min="1"
                    max="100"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={createForm.description}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter exam description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="scheduled_start_time">Start Date & Time (India Time)</Label>
                  <div className="flex gap-2">
                    <Input
                      id="scheduled_start_time"
                      type="datetime-local"
                      value={formatDatetimeLocalValue(createForm.scheduled_start_time)}
                      onChange={(e) => setCreateForm(prev => ({ ...prev, scheduled_start_time: parseLocalDatetime(e.target.value) }))}
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setCreateForm(prev => ({ 
                        ...prev, 
                        scheduled_start_time: new Date(getIndianTime().getTime() + 1 * 60 * 1000) // 1 minute from now
                      }))}
                      className="whitespace-nowrap"
                    >
                      Now +1min
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Current India time: {getIndianTime().toLocaleString('en-IN', {
                      timeZone: 'Asia/Kolkata',
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: true
                    })} IST
                  </p>
                </div>
                <div>
                  <Label htmlFor="duration_minutes">Duration (minutes)</Label>
                  <Input
                    id="duration_minutes"
                    type="number"
                    value={createForm.duration_minutes}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) }))}
                    min="5"
                    max="300"
                  />
                </div>
              </div>

              {/* Exam Type Selection */}
              <div>
                <Label>Exam Type</Label>
                <Select 
                  value={createForm.exam_type}
                  onValueChange={(value: "adaptive_subject" | "practice_chapter") => 
                    setCreateForm(prev => ({
                      ...prev,
                      exam_type: value,
                      chapter_ids: [] // Reset chapters when type changes
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="adaptive_subject">Adaptive Subject (Full Subject)</SelectItem>
                    <SelectItem value="practice_chapter">Practice Chapters (Specific Chapters)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground mt-1">
                  {createForm.exam_type === "adaptive_subject" 
                    ? "Questions from entire subject with adaptive difficulty" 
                    : "Practice questions from specific chapters"}
                </p>
              </div>

              {/* Subject Selection */}
              <div>
                <Label>Subject</Label>
                <Select 
                  value={createForm.subject_id?.toString() || ""} 
                  onValueChange={handleSubjectChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={
                      isLoadingSubjects 
                        ? "Loading subjects..." 
                        : subjectsError 
                          ? `Error: ${subjectsError.message}` 
                          : (!subjects || !Array.isArray(subjects) || subjects.length === 0)
                            ? "No subjects available" 
                            : "Select a subject"
                    } />
                  </SelectTrigger>
                  <SelectContent>
                    {isLoadingSubjects ? (
                      <SelectItem value="loading" disabled>Loading subjects...</SelectItem>
                    ) : subjectsError ? (
                      <SelectItem value="error" disabled>Error: {subjectsError.message}</SelectItem>
                    ) : (!subjects || !Array.isArray(subjects) || subjects.length === 0) ? (
                      <SelectItem value="empty" disabled>No subjects available</SelectItem>
                    ) : (
                      subjects.map((subject: any) => (
                        <SelectItem key={subject.id} value={subject.id.toString()}>
                          {subject.name} ({subject.code})
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* Chapter Selection - Only for Practice Chapter Type */}
              {createForm.exam_type === "practice_chapter" && createForm.subject_id && (
                <div>
                  <Label>
                    Select Chapters 
                    {isLoadingChapters ? " (Loading...)" : ` (${chapters.length} available)`}
                  </Label>
                  <div className="space-y-3 mt-3 max-h-60 overflow-y-auto border rounded p-4">
                    {isLoadingChapters ? (
                      <div className="text-center p-6">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        <p className="text-sm text-muted-foreground">Loading chapters...</p>
                      </div>
                    ) : chapters.length > 0 ? (
                      chapters.map((chapter: any) => (
                        <div key={chapter.id} className="border rounded-lg p-3 hover:bg-gray-50">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id={`chapter-${chapter.id}`}
                                checked={createForm.chapter_ids.includes(chapter.id)}
                                onCheckedChange={(checked) => handleChapterToggle(chapter.id, checked as boolean)}
                              />
                              <Label htmlFor={`chapter-${chapter.id}`} className="text-sm font-medium">
                                Chapter {chapter.chapter_number}: {chapter.name}
                              </Label>
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {chapter.question_count ? `${chapter.question_count} questions` : 'Questions available'}
                            </span>
                          </div>
                          <p className="ml-6 text-xs text-muted-foreground">{chapter.description}</p>
                        </div>
                      ))
                    ) : (
                      <div className="text-center p-6 bg-gray-50 rounded-lg">
                        <BookOpen className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                        <p className="text-sm text-muted-foreground">
                          No chapters found for this subject.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Preview */}
              {createForm.exam_name && createForm.subject_id && (
                <Card>
                  <CardHeader>
                    <CardTitle>Exam Preview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div><strong>Name:</strong> {createForm.exam_name}</div>
                      <div><strong>Type:</strong> {createForm.exam_type === "adaptive_subject" ? "Adaptive Subject" : "Practice Chapters"}</div>
                      <div><strong>Subject:</strong> {selectedSubject?.name}</div>
                      <div><strong>Duration:</strong> {createForm.duration_minutes} minutes</div>
                      <div><strong>Questions:</strong> {createForm.question_count}</div>
                      <div><strong>Start Time:</strong> {createForm.scheduled_start_time.toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'})} (India Time)</div>
                      {createForm.exam_type === "practice_chapter" && createForm.chapter_ids.length > 0 && (
                        <div><strong>Selected Chapters:</strong> {createForm.chapter_ids.length} chapters</div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateExam}
                disabled={createExamMutation.isPending || !createForm.exam_name || !createForm.subject_id}
              >
                {createExamMutation.isPending ? "Scheduling..." : "Schedule Exam"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="exams">Scheduled Exams</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="exams">
          {examsLoading ? (
            <div className="flex justify-center p-8">
              <div>Loading enhanced exams...</div>
            </div>
          ) : (
            <div className="grid gap-4">
              {exams.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-lg font-semibold mb-2">No Enhanced Exams Created</p>
                    <p className="text-muted-foreground mb-4">
                      Get started by creating your first enhanced exam with dynamic content selection.
                    </p>
                    <Button onClick={() => setIsCreateDialogOpen(true)}>
                      Create Your First Enhanced Exam
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                exams.map((exam) => (
                  <Card key={exam.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="flex items-center gap-2">
                            <BookOpen className="h-5 w-5" />
                            {exam.title}
                          </CardTitle>
                          <CardDescription>{exam.description || 'No description provided'}</CardDescription>
                        </div>
                        <Badge variant={exam.status === "active" ? "default" : "secondary"}>
                          {exam.status}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            {exam.subjects && exam.subjects.length > 0 
                              ? exam.subjects.map(s => s.name).join(', ')
                              : 'No subjects'
                            }
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CalendarDays className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            {exam.start_time 
                              ? new Date(exam.start_time).toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'}) + ' (IST)'
                              : 'Not Scheduled'
                            }
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{exam.duration_minutes} min</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{exam.enrolled_students} students</span>
                        </div>
                      </div>
                      <div className="flex justify-end gap-2 mt-4">
                        {/* Status-based action buttons */}
                        {exam.status === "scheduled" && (
                          <Button 
                            variant="default" 
                            size="sm"
                            onClick={() => activateExamMutation.mutate(exam.id)}
                            disabled={activateExamMutation.isPending}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            {activateExamMutation.isPending ? "Activating..." : "🚀 Activate Now"}
                          </Button>
                        )}
                        
                        {exam.status === "active" && (
                          <>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => {
                                // Navigate to live monitoring
                                alert("🔴 Live monitoring dashboard would open here");
                              }}
                            >
                              📊 Live Monitor
                            </Button>
                            <Button 
                              variant="destructive" 
                              size="sm"
                              onClick={() => {
                                if (confirm(`Are you sure you want to end the exam "${exam.title}"?\n\nThis will:\n• Auto-submit all ongoing attempts\n• Calculate final results\n• Notify all students`)) {
                                  endExamMutation.mutate(exam.id);
                                }
                              }}
                              disabled={endExamMutation.isPending}
                            >
                              {endExamMutation.isPending ? "Ending..." : "🏁 End Exam"}
                            </Button>
                          </>
                        )}
                        
                        {(exam.status === "completed" || exam.status === "cancelled") && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              // Navigate to results and analytics
                              alert("📈 Results and analytics would open here");
                            }}
                          >
                            📈 View Results
                          </Button>
                        )}
                        
                        <Button variant="outline" size="sm">
                          👁️ View Details
                        </Button>
                        
                        {exam.status !== "active" && (
                          <Button 
                            variant="destructive" 
                            size="sm"
                            onClick={() => {
                              if (confirm(`Are you sure you want to delete the exam "${exam.title}"?`)) {
                                handleDeleteExam(exam.id);
                              }
                            }}
                          >
                            🗑️ Delete
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Enhanced Exam Analytics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center p-8">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-semibold mb-2">Advanced Analytics Dashboard</p>
                <p className="text-muted-foreground">
                  Detailed analytics and insights for your enhanced exams will appear here.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}