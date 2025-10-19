import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Clock, Users, BookOpen, Brain, Settings, Target, 
  Calendar, CheckCircle, AlertCircle, Eye, Edit, Trash,
  Plus, Filter, Search, BarChart3, TrendingUp,
  ChevronRight, ChevronDown, Info, Zap
} from 'lucide-react';

const EnhancedExamManagement = () => {
  // State management
  const [subjects, setSubjects] = useState([]);
  const [exams, setExams] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapters, setSelectedChapters] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [questionPool, setQuestionPool] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form state for exam creation
  const [examForm, setExamForm] = useState({
    exam_name: '',
    description: '',
    content_selection: {
      selection_type: 'full_subject',
      subject_id: null,
      chapter_ids: [],
      difficulty_levels: [],
      question_types: [],
      adaptive_difficulty: false
    },
    scheduled_start_time: '',
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

  // Fetch subjects with detailed information
  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/enhanced-exam/admin/subjects/details');
      const data = await response.json();
      setSubjects(data);
    } catch (err) {
      setError('Failed to fetch subjects');
    } finally {
      setLoading(false);
    }
  };

  // Fetch existing exams
  const fetchExams = async () => {
    try {
      const response = await fetch('/api/enhanced-exam/admin/exams/enhanced/list');
      const data = await response.json();
      setExams(data);
    } catch (err) {
      setError('Failed to fetch exams');
    }
  };

  // Validate question pool based on current selection
  const validateQuestionPool = async () => {
    if (!examForm.content_selection.subject_id) return;
    
    try {
      const response = await fetch('/api/enhanced-exam/admin/exams/validate-question-pool', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(examForm.content_selection)
      });
      const data = await response.json();
      setQuestionPool(data);
    } catch (err) {
      console.error('Failed to validate question pool:', err);
    }
  };

  // Handle subject selection
  const handleSubjectChange = (subjectId) => {
    const subject = subjects.find(s => s.id === parseInt(subjectId));
    setSelectedSubject(subject);
    setExamForm(prev => ({
      ...prev,
      content_selection: {
        ...prev.content_selection,
        subject_id: parseInt(subjectId),
        chapter_ids: []
      }
    }));
    setSelectedChapters([]);
  };

  // Handle chapter selection
  const handleChapterToggle = (chapterId, checked) => {
    if (checked) {
      setSelectedChapters(prev => [...prev, chapterId]);
      setExamForm(prev => ({
        ...prev,
        content_selection: {
          ...prev.content_selection,
          chapter_ids: [...prev.content_selection.chapter_ids, chapterId]
        }
      }));
    } else {
      setSelectedChapters(prev => prev.filter(id => id !== chapterId));
      setExamForm(prev => ({
        ...prev,
        content_selection: {
          ...prev.content_selection,
          chapter_ids: prev.content_selection.chapter_ids.filter(id => id !== chapterId)
        }
      }));
    }
  };

  // Handle selection type change
  const handleSelectionTypeChange = (type) => {
    setExamForm(prev => ({
      ...prev,
      content_selection: {
        ...prev.content_selection,
        selection_type: type,
        chapter_ids: type === 'full_subject' ? [] : prev.content_selection.chapter_ids
      }
    }));
    if (type === 'full_subject') {
      setSelectedChapters([]);
    }
  };

  // Create exam
  const createExam = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/enhanced-exam/admin/exams/create-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(examForm)
      });
      
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
        return;
      }
      
      await fetchExams(); // Refresh exams list
      setShowCreateDialog(false);
      resetForm();
    } catch (err) {
      setError('Failed to create exam');
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setExamForm({
      exam_name: '',
      description: '',
      content_selection: {
        selection_type: 'full_subject',
        subject_id: null,
        chapter_ids: [],
        difficulty_levels: [],
        question_types: [],
        adaptive_difficulty: false
      },
      scheduled_start_time: '',
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
    setSelectedSubject(null);
    setSelectedChapters([]);
    setQuestionPool(null);
  };

  // Format date for display
  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'upcoming': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'expired': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Component effects
  useEffect(() => {
    fetchSubjects();
    fetchExams();
  }, []);

  useEffect(() => {
    if (examForm.content_selection.subject_id) {
      validateQuestionPool();
    }
  }, [examForm.content_selection]);

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Enhanced Exam Management</h1>
          <p className="text-gray-600 mt-2">Create and manage dynamic exams with intelligent content selection</p>
        </div>
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Create Enhanced Exam
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs defaultValue="exams" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="exams">Active Exams</TabsTrigger>
          <TabsTrigger value="subjects">Subject Overview</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Exams Tab */}
        <TabsContent value="exams" className="space-y-4">
          <div className="grid gap-4">
            {exams.map((exam) => (
              <Card key={exam.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold">{exam.exam_name}</h3>
                        <Badge className={getStatusColor(exam.status)}>
                          {exam.status.toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
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
                            <Target className="h-4 w-4" />
                            <span>{exam.question_count} questions</span>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>{formatDateTime(exam.scheduled_start_time)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            <span>{exam.enrolled_students_count} students</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <BarChart3 className="h-4 w-4" />
                            <span>
                              {exam.completed_sessions_count} completed
                              {exam.avg_score && ` (Avg: ${exam.avg_score.toFixed(1)}%)`}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Content Selection Info */}
                      {exam.content_selection && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <div className="text-sm">
                            <strong>Content Selection:</strong> {exam.content_selection.selection_type.replace('_', ' ').toUpperCase()}
                            {exam.content_selection.selection_type === 'specific_chapters' && exam.chapters.length > 0 && (
                              <span className="ml-2">
                                ({exam.chapters.length} chapters selected)
                              </span>
                            )}
                            {exam.content_selection.adaptive_difficulty && (
                              <Badge className="ml-2 bg-purple-100 text-purple-800">
                                <Zap className="h-3 w-3 mr-1" />
                                Adaptive
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Subjects Tab */}
        <TabsContent value="subjects" className="space-y-4">
          <div className="grid gap-6">
            {subjects.map((subject) => (
              <Card key={subject.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <BookOpen className="h-5 w-5" />
                      {subject.name}
                    </div>
                    <Badge variant="outline">{subject.total_questions} questions</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Chapters ({subject.chapters.length})</h4>
                      <div className="space-y-2">
                        {subject.chapters.slice(0, 5).map((chapter) => (
                          <div key={chapter.id} className="flex justify-between text-sm">
                            <span>{chapter.name}</span>
                            <span className="text-gray-500">{chapter.question_count} questions</span>
                          </div>
                        ))}
                        {subject.chapters.length > 5 && (
                          <div className="text-sm text-gray-500">
                            ... and {subject.chapters.length - 5} more
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-3">Statistics</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Success Rate:</span>
                          <span className="font-medium">{subject.success_rate.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Response Time:</span>
                          <span className="font-medium">{subject.avg_response_time.toFixed(1)}s</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Question Types:</span>
                          <span className="font-medium">{subject.question_types.length}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Exams</p>
                    <p className="text-2xl font-bold">{exams.length}</p>
                  </div>
                  <Calendar className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Exams</p>
                    <p className="text-2xl font-bold">
                      {exams.filter(e => e.status === 'active').length}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Students</p>
                    <p className="text-2xl font-bold">
                      {exams.reduce((sum, e) => sum + e.enrolled_students_count, 0)}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Completion Rate</p>
                    <p className="text-2xl font-bold">
                      {exams.length > 0 ? 
                        Math.round(exams.reduce((sum, e) => sum + e.completed_sessions_count, 0) / 
                        exams.reduce((sum, e) => sum + e.enrolled_students_count, 1) * 100) : 0}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Exam Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Create Enhanced Exam
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Basic Information</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="exam_name">Exam Name*</Label>
                  <Input
                    id="exam_name"
                    value={examForm.exam_name}
                    onChange={(e) => setExamForm(prev => ({
                      ...prev,
                      exam_name: e.target.value
                    }))}
                    placeholder="Enter exam name"
                  />
                </div>
                <div>
                  <Label htmlFor="scheduled_start_time">Start Time*</Label>
                  <Input
                    id="scheduled_start_time"
                    type="datetime-local"
                    value={examForm.scheduled_start_time}
                    onChange={(e) => setExamForm(prev => ({
                      ...prev,
                      scheduled_start_time: e.target.value
                    }))}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={examForm.description}
                  onChange={(e) => setExamForm(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  placeholder="Enter exam description"
                />
              </div>
            </div>

            {/* Dynamic Subject & Chapter Selection */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Dynamic Content Selection
              </h3>
              
              {/* Subject Selection */}
              <div>
                <Label>Subject*</Label>
                <Select 
                  value={examForm.content_selection.subject_id?.toString()} 
                  onValueChange={handleSubjectChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects.map((subject) => (
                      <SelectItem key={subject.id} value={subject.id.toString()}>
                        {subject.name} ({subject.total_questions} questions)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Selection Type */}
              {selectedSubject && (
                <div>
                  <Label>Selection Mode</Label>
                  <Select 
                    value={examForm.content_selection.selection_type} 
                    onValueChange={handleSelectionTypeChange}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full_subject">Entire Subject</SelectItem>
                      <SelectItem value="specific_chapters">Specific Chapters</SelectItem>
                      <SelectItem value="adaptive_mixed">Adaptive Mixed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Chapter Selection */}
              {selectedSubject && examForm.content_selection.selection_type === 'specific_chapters' && (
                <div>
                  <Label>Select Chapters ({selectedChapters.length} selected)</Label>
                  <div className="max-h-48 overflow-y-auto border rounded-lg p-4 space-y-3">
                    {selectedSubject.chapters.map((chapter) => (
                      <div key={chapter.id} className="flex items-start space-x-3">
                        <Checkbox
                          id={`chapter-${chapter.id}`}
                          checked={selectedChapters.includes(chapter.id)}
                          onCheckedChange={(checked) => handleChapterToggle(chapter.id, checked)}
                        />
                        <div className="flex-1">
                          <Label 
                            htmlFor={`chapter-${chapter.id}`}
                            className="text-sm font-medium cursor-pointer"
                          >
                            {chapter.name}
                          </Label>
                          <div className="text-xs text-gray-500 mt-1">
                            {chapter.question_count} questions • 
                            Avg difficulty: {chapter.avg_difficulty.toFixed(1)} • 
                            Est. time: {chapter.estimated_time_minutes}min
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Adaptive Mode Toggle */}
              <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-purple-600" />
                  <div>
                    <Label>Adaptive Difficulty</Label>
                    <p className="text-xs text-gray-600">
                      Questions adapt based on student performance
                    </p>
                  </div>
                </div>
                <Switch
                  checked={examForm.content_selection.adaptive_difficulty}
                  onCheckedChange={(checked) => setExamForm(prev => ({
                    ...prev,
                    content_selection: {
                      ...prev.content_selection,
                      adaptive_difficulty: checked
                    }
                  }))}
                />
              </div>
            </div>

            {/* Question Pool Validation */}
            {questionPool && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Question Pool Analysis</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <Card className="p-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Available Questions</span>
                      <span className="font-bold text-lg">{questionPool.total_available}</span>
                    </div>
                  </Card>
                  <Card className="p-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Selected for Exam</span>
                      <span className="font-bold text-lg">{questionPool.selected_count}</span>
                    </div>
                  </Card>
                </div>
                
                {Object.keys(questionPool.difficulty_breakdown).length > 0 && (
                  <div>
                    <Label className="text-sm font-medium">Difficulty Distribution</Label>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(questionPool.difficulty_breakdown).map(([level, count]) => (
                        <Badge key={level} variant="outline" className="text-xs">
                          {level}: {count}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Exam Configuration */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Exam Configuration</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="duration_minutes">Duration (minutes)*</Label>
                  <Input
                    id="duration_minutes"
                    type="number"
                    min="1"
                    value={examForm.duration_minutes}
                    onChange={(e) => setExamForm(prev => ({
                      ...prev,
                      duration_minutes: parseInt(e.target.value) || 60
                    }))}
                  />
                </div>
                <div>
                  <Label htmlFor="question_count">Number of Questions*</Label>
                  <Input
                    id="question_count"
                    type="number"
                    min="1"
                    max={questionPool?.total_available || 100}
                    value={examForm.question_count}
                    onChange={(e) => setExamForm(prev => ({
                      ...prev,
                      question_count: parseInt(e.target.value) || 20
                    }))}
                  />
                </div>
                <div className="flex items-center space-x-2 pt-6">
                  <Switch
                    checked={examForm.auto_assign_all_active}
                    onCheckedChange={(checked) => setExamForm(prev => ({
                      ...prev,
                      auto_assign_all_active: checked
                    }))}
                  />
                  <Label>Auto-assign to all active students</Label>
                </div>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Advanced Settings
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Randomize Questions</Label>
                    <Switch
                      checked={examForm.randomize_questions}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        randomize_questions: checked
                      }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Allow Navigation</Label>
                    <Switch
                      checked={examForm.allow_question_navigation}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        allow_question_navigation: checked
                      }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Question Review</Label>
                    <Switch
                      checked={examForm.allow_question_review}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        allow_question_review: checked
                      }))}
                    />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Auto Submit on Expiry</Label>
                    <Switch
                      checked={examForm.auto_submit_on_expiry}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        auto_submit_on_expiry: checked
                      }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Detailed Analytics</Label>
                    <Switch
                      checked={examForm.detailed_analytics}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        detailed_analytics: checked
                      }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Proctoring</Label>
                    <Switch
                      checked={examForm.proctoring_enabled}
                      onCheckedChange={(checked) => setExamForm(prev => ({
                        ...prev,
                        proctoring_enabled: checked
                      }))}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-4 pt-6 border-t">
              <Button 
                variant="outline" 
                onClick={() => setShowCreateDialog(false)}
              >
                Cancel
              </Button>
              <Button 
                onClick={createExam}
                disabled={loading || !examForm.exam_name || !examForm.content_selection.subject_id || !examForm.scheduled_start_time}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Create Enhanced Exam
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedExamManagement;