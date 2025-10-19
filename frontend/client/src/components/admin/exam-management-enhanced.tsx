import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  CalendarIcon, 
  Clock, 
  Users, 
  BookOpen, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Plus,
  Eye,
  Settings
} from "lucide-react";

// Enhanced Types
interface EnhancedSubject {
  id: number;
  name: string;
  code: string;
  chapter_count: number;
  question_count: number;
  chapters: EnhancedChapter[];
}

interface EnhancedChapter {
  id: number;
  name: string;
  question_count: number;
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
  enrolled_students: string[];
  auto_assign_all_active: boolean;
  randomize_questions: boolean;
  allow_question_navigation: boolean;
  show_question_feedback: boolean;
  allow_question_review: boolean;
  auto_submit_on_expiry: boolean;
  proctoring_enabled: boolean;
  detailed_analytics: boolean;
  adaptive_config: any;
}

interface EnhancedScheduledExam {
  id: string;
  exam_name: string;
  subject_name: string;
  subject_code: string;
  status: string;
  scheduled_start_time: string;
  duration_minutes: number;
  question_count: number;
  enrolled_count: number;
  completed_count: number;
  content_selection: ContentSelection;
  detailed_analytics: boolean;
  created_at: string;
}

interface QuestionPoolInfo {
  available_questions: number;
  by_difficulty: Record<string, number>;
  by_chapter: Record<string, number>;
  recommendations: string[];
}

export default function EnhancedExamManagement() {
  const [selectedTab, setSelectedTab] = useState("exams");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedExam, setSelectedExam] = useState<EnhancedScheduledExam | null>(null);
  const [isEnrollDialogOpen, setIsEnrollDialogOpen] = useState(false);
  const [questionPool, setQuestionPool] = useState<QuestionPoolInfo | null>(null);
  const queryClient = useQueryClient();

  // Enhanced Create exam form state
  const [createForm, setCreateForm] = useState<EnhancedCreateExamForm>({
    exam_name: "",
    description: "",
    content_selection: {
      selection_type: "full_subject",
      subject_id: null,
      chapter_ids: [],
      difficulty_levels: [],
      question_types: [],
      adaptive_difficulty: false
    },
    scheduled_start_time: new Date(),
    duration_minutes: 60,
    question_count: 20,
    time_warnings: [10, 5, 1],
    enrolled_students: [],
    auto_assign_all_active: true,
    randomize_questions: true,
    allow_question_navigation: true,
    show_question_feedback: false,
    allow_question_review: true,
    auto_submit_on_expiry: true,
    proctoring_enabled: false,
    detailed_analytics: true,
    adaptive_config: {}
  });

  // Enhanced API Queries
  const { data: exams = [], isLoading: examsLoading } = useQuery({
    queryKey: ["enhanced-exams"],
    queryFn: async (): Promise<EnhancedScheduledExam[]> => {
      const response = await fetch("/api/v1/enhanced-exam/list-exams");
      if (!response.ok) throw new Error("Failed to fetch enhanced exams");
      return await response.json();
    }
  });

  // Fetch enhanced subjects with detailed info
  const { data: subjectsResponse } = useQuery({
    queryKey: ["enhanced-subjects"],
    queryFn: async () => {
      const response = await fetch("/api/v1/enhanced-exam/subjects-details");
      if (!response.ok) throw new Error("Failed to fetch enhanced subjects");
      return await response.json();
    }
  });

  // Extract subjects array from response
  const subjects = subjectsResponse?.subjects || [];
  
  // Get current selected subject data for chapter loading
  const selectedSubject = subjects.find((s: EnhancedSubject) => s.id === createForm.content_selection.subject_id);
  
  // Validate question pool when form data changes
  const { data: questionPoolData } = useQuery({
    queryKey: ["question-pool", createForm.content_selection],
    queryFn: async () => {
      if (!createForm.content_selection.subject_id) return null;
      
      const response = await fetch("/api/v1/enhanced-exam/validate-question-pool", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content_selection: createForm.content_selection,
          question_count: createForm.question_count
        })
      });
      
      if (!response.ok) return null;
      return await response.json();
    },
    enabled: !!createForm.content_selection.subject_id
  });

  // Fetch students for enrollment
  const { data: students = [] } = useQuery({
    queryKey: ["students"],
    queryFn: async () => {
      const response = await fetch("/api/admin/students");
      if (!response.ok) throw new Error("Failed to fetch students");
      const data = await response.json();
      return data.students || [];
    }
  });

  // Create enhanced exam mutation
  const createExamMutation = useMutation({
    mutationFn: async (examData: EnhancedCreateExamForm) => {
      const response = await fetch("/api/v1/enhanced-exam/create-exam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...examData,
          scheduled_start_time: examData.scheduled_start_time.toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to create enhanced exam");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
      setIsCreateDialogOpen(false);
      setCreateForm({
        exam_name: "",
        description: "",
        content_selection: {
          selection_type: "full_subject",
          subject_id: null,
          chapter_ids: [],
          difficulty_levels: [],
          question_types: [],
          adaptive_difficulty: false
        },
        scheduled_start_time: new Date(),
        duration_minutes: 60,
        question_count: 20,
        time_warnings: [10, 5, 1],
        enrolled_students: [],
        auto_assign_all_active: true,
        randomize_questions: true,
        allow_question_navigation: true,
        show_question_feedback: false,
        allow_question_review: true,
        auto_submit_on_expiry: true,
        proctoring_enabled: false,
        detailed_analytics: true,
        adaptive_config: {}
      });
    }
  });

  // Enroll students mutation
  const enrollStudentsMutation = useMutation({
    mutationFn: async (data: { exam_id: string; student_ids: string[] }) => {
      const response = await fetch("/api/exams/admin/enroll", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error("Failed to enroll students");
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["enhanced-exams"] });
      setIsEnrollDialogOpen(false);
    }
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "upcoming": return <Clock className="h-4 w-4 text-blue-500" />;
      case "active": return <AlertCircle className="h-4 w-4 text-orange-500" />;
      case "completed": return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "cancelled": return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleCreateExam = () => {
    createExamMutation.mutate(createForm);
  };

  const handleEnrollStudents = () => {
    if (selectedExam) {
      enrollStudentsMutation.mutate({
        exam_id: selectedExam.id,
        student_ids: createForm.enrolled_students
      });
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Enhanced Exam Management</h1>
        <Button onClick={() => setIsCreateDialogOpen(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Enhanced Exam
        </Button>
      </div>

      {/* Create Enhanced Exam Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Enhanced Exam</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="exam_name">Exam Name</Label>
                <Input
                  id="exam_name"
                  value={createForm.exam_name}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, exam_name: e.target.value }))}
                  placeholder="Mid-term Exam"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Select
                  value={createForm.content_selection.subject_id?.toString() || ""}
                  onValueChange={(value) => setCreateForm(prev => ({ 
                    ...prev, 
                    content_selection: {
                      ...prev.content_selection,
                      subject_id: parseInt(value),
                      chapter_ids: [] // Reset chapters when subject changes
                    }
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects.map((subject: EnhancedSubject) => (
                      <SelectItem key={subject.id} value={subject.id.toString()}>
                        {subject.name} ({subject.chapter_count} chapters, {subject.question_count} questions)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Dynamic Content Selection */}
            {selectedSubject && selectedSubject.chapters && selectedSubject.chapters.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Content Selection</Label>
                  <div className="text-sm text-gray-500">
                    {questionPoolData && (
                      <span className="font-medium text-green-600">
                        {questionPoolData.available_questions} questions available
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Select
                    value={createForm.content_selection.selection_type}
                    onValueChange={(value: "full_subject" | "specific_chapters") => 
                      setCreateForm(prev => ({
                        ...prev,
                        content_selection: {
                          ...prev.content_selection,
                          selection_type: value,
                          chapter_ids: value === "full_subject" ? [] : prev.content_selection.chapter_ids
                        }
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full_subject">Full Subject (All Chapters)</SelectItem>
                      <SelectItem value="specific_chapters">Specific Chapters</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {createForm.content_selection.selection_type === "specific_chapters" && (
                  <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto border rounded p-3">
                    {selectedSubject.chapters.map((chapter: EnhancedChapter) => (
                      <label key={chapter.id} className="flex items-center space-x-2 text-sm">
                        <input
                          type="checkbox"
                          checked={createForm.content_selection.chapter_ids.includes(chapter.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setCreateForm(prev => ({
                                ...prev,
                                content_selection: {
                                  ...prev.content_selection,
                                  chapter_ids: [...prev.content_selection.chapter_ids, chapter.id]
                                }
                              }));
                            } else {
                              setCreateForm(prev => ({
                                ...prev,
                                content_selection: {
                                  ...prev.content_selection,
                                  chapter_ids: prev.content_selection.chapter_ids.filter(id => id !== chapter.id)
                                }
                              }));
                            }
                          }}
                        />
                        <span>{chapter.name} ({chapter.question_count} questions)</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Enhanced Question Configuration */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="question_count">Number of Questions</Label>
                <Input
                  id="question_count"
                  type="number"
                  value={createForm.question_count}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, question_count: parseInt(e.target.value) || 20 }))}
                  min="1"
                  max="100"
                />
              </div>
              
              <div className="space-y-2">
                <Label>Adaptive Difficulty</Label>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={createForm.content_selection.adaptive_difficulty}
                    onChange={(e) => setCreateForm(prev => ({
                      ...prev,
                      content_selection: {
                        ...prev.content_selection,
                        adaptive_difficulty: e.target.checked
                      }
                    }))}
                  />
                  <span className="text-sm">Enable adaptive difficulty progression</span>
                </div>
              </div>
            </div>

            {/* Enhanced Time Configuration */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="duration">Duration (minutes)</Label>
                <Input
                  id="duration"
                  type="number"
                  value={createForm.duration_minutes}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) || 60 }))}
                  min="5"
                  max="300"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="scheduled_time">Scheduled Start Time</Label>
                <Input
                  id="scheduled_time"
                  type="datetime-local"
                  value={createForm.scheduled_start_time.toISOString().slice(0, 16)}
                  onChange={(e) => setCreateForm(prev => ({ 
                    ...prev, 
                    scheduled_start_time: new Date(e.target.value) 
                  }))}
                />
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={createForm.description}
                onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe the exam purpose and format..."
                rows={3}
              />
            </div>

            {/* Enhanced Settings */}
            <div className="space-y-3">
              <Label>Exam Settings</Label>
              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.randomize_questions}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, randomize_questions: e.target.checked }))}
                  />
                  <span>Randomize Questions</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.allow_question_navigation}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, allow_question_navigation: e.target.checked }))}
                  />
                  <span>Allow Question Navigation</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.allow_question_review}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, allow_question_review: e.target.checked }))}
                  />
                  <span>Allow Review Before Submit</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.auto_submit_on_expiry}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, auto_submit_on_expiry: e.target.checked }))}
                  />
                  <span>Auto Submit on Time Expiry</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.detailed_analytics}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, detailed_analytics: e.target.checked }))}
                  />
                  <span>Detailed Analytics</span>
                </label>
                
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={createForm.auto_assign_all_active}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, auto_assign_all_active: e.target.checked }))}
                  />
                  <span>Auto Assign All Active Students</span>
                </label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleCreateExam}
              disabled={createExamMutation.isPending || !createForm.exam_name || !createForm.content_selection.subject_id}
            >
              {createExamMutation.isPending ? "Creating..." : "Create Enhanced Exam"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="exams">Enhanced Exams</TabsTrigger>
          <TabsTrigger value="analytics">Analytics Dashboard</TabsTrigger>
          <TabsTrigger value="settings">System Settings</TabsTrigger>
        </TabsList>

        {/* Enhanced Exams List */}
        <TabsContent value="exams">
          {examsLoading ? (
            <div className="text-center py-8">Loading enhanced exams...</div>
          ) : (
            <div className="grid gap-4">
              {exams.map((exam) => (
                <Card key={exam.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold">{exam.exam_name}</h3>
                          <Badge variant="outline" className="capitalize">
                            {exam.status}
                          </Badge>
                          {exam.detailed_analytics && (
                            <Badge variant="secondary">Enhanced Analytics</Badge>
                          )}
                        </div>
                        
                        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4" />
                              <span>{exam.subject_name} ({exam.subject_code})</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4" />
                              <span>{exam.duration_minutes} minutes</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Settings className="h-4 w-4" />
                              <span>{exam.question_count} questions</span>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <CalendarIcon className="h-4 w-4" />
                              <span>{new Date(exam.scheduled_start_time).toLocaleString()}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Users className="h-4 w-4" />
                              <span>{exam.completed_count}/{exam.enrolled_count} completed</span>
                            </div>
                          </div>
                        </div>
                        
                        {/* Enhanced Content Info */}
                        <div className="text-xs text-gray-500 border-t pt-2">
                          <div>Content: {exam.content_selection.selection_type === "full_subject" ? "Full Subject" : `${exam.content_selection.chapter_ids.length} Specific Chapters`}</div>
                          {exam.content_selection.adaptive_difficulty && <div>Adaptive Difficulty Enabled</div>}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        {getStatusIcon(exam.status)}
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {exams.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No enhanced exams created yet.</p>
                  <p className="text-sm">Create your first enhanced exam to get started!</p>
                </div>
              )}
            </div>
          )}
        </TabsContent>

        {/* Analytics Dashboard */}
        <TabsContent value="analytics">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Total Enhanced Exams</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{exams.length}</div>
                <div className="text-sm text-gray-600">All time</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Active Exams</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {exams.filter(e => e.status === "active").length}
                </div>
                <div className="text-sm text-gray-600">Currently running</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Adaptive Exams</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {exams.filter(e => e.content_selection.adaptive_difficulty).length}
                </div>
                <div className="text-sm text-gray-600">With adaptive difficulty</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* System Settings */}
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Enhanced Exam System Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-sm text-gray-600">
                  <p>Enhanced exam system is active with the following features:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Dynamic subject and chapter selection</li>
                    <li>Real-time question pool validation</li>
                    <li>Adaptive difficulty progression</li>
                    <li>Enhanced time management with custom warnings</li>
                    <li>Detailed analytics and reporting</li>
                    <li>Advanced exam configuration options</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}