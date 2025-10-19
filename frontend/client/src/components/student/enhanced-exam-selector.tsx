import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Brain, 
  BookOpen, 
  Clock, 
  Target, 
  TrendingUp, 
  Users,
  Play,
  Calendar,
  FileText
} from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

interface EnhancedExamSelectorProps {
  onStartExam: (examType: 'adaptive_subject' | 'practice_chapter' | 'scheduled_exam', examId: string, examName: string) => void;
  onViewScheduled: () => void;
}

export default function EnhancedExamSelector({ onStartExam, onViewScheduled }: EnhancedExamSelectorProps) {
  
  // Fetch available subjects using existing API
  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects"],
    queryFn: async () => {
      const response = await apiRequest("GET", "http://localhost:8000/api/subjects");
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    },
  });

  // Fetch available chapters for practice (when subject is selected)
  const [selectedSubject, setSelectedSubject] = useState<string>("");
  const { data: chapters = [] } = useQuery({
    queryKey: ["chapters", selectedSubject],
    queryFn: async () => {
      if (!selectedSubject) return [];
      const response = await apiRequest("GET", `http://localhost:8000/api/subjects/${selectedSubject}/chapters`);
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    },
    enabled: !!selectedSubject,
  });

  // Fetch scheduled exams (using existing API)
  const { data: scheduledExams = [] } = useQuery({
    queryKey: ["scheduledExamsSelector"],
    queryFn: async () => {
      const response = await apiRequest("GET", "http://localhost:8000/api/enhanced-exam/student/exams/available");
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-foreground">Enhanced Exam System</h2>
        <p className="text-muted-foreground">
          Choose from adaptive learning, practice chapters, or scheduled exams
        </p>
      </div>

      <Tabs defaultValue="adaptive" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="adaptive" className="flex items-center space-x-2">
            <Brain className="h-4 w-4" />
            <span>Adaptive Tests</span>
          </TabsTrigger>
          <TabsTrigger value="practice" className="flex items-center space-x-2">
            <BookOpen className="h-4 w-4" />
            <span>Practice Chapters</span>
          </TabsTrigger>
          <TabsTrigger value="scheduled" className="flex items-center space-x-2">
            <Calendar className="h-4 w-4" />
            <span>Scheduled Exams</span>
          </TabsTrigger>
        </TabsList>

        {/* Adaptive Subject Tests */}
        <TabsContent value="adaptive" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-blue-600" />
                <span>Adaptive Subject Tests</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                AI-powered tests that adapt to your performance in real-time
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {subjects.map((subject: any) => (
                  <Card 
                    key={subject.id || subject.subject_code} 
                    className="border-blue-200 hover:border-blue-400 transition-colors cursor-pointer"
                    onClick={() => onStartExam('adaptive_subject', subject.id || subject.subject_code, subject.name || subject.subject_name)}
                  >
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold">{subject.name || subject.subject_name}</h4>
                        <Badge variant="outline" className="bg-blue-50">
                          <Target className="h-3 w-3 mr-1" />
                          Adaptive
                        </Badge>
                      </div>
                      
                      <div className="space-y-2 text-sm text-muted-foreground">
                        <div className="flex items-center space-x-2">
                          <BookOpen className="h-3 w-3" />
                          <span>{subject.chapter_count || 'Multiple'} chapters</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="h-3 w-3" />
                          <span>~30-45 minutes</span>
                        </div>
                      </div>

                      <Button 
                        className="w-full" 
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onStartExam('adaptive_subject', subject.id || subject.subject_code, subject.name || subject.subject_name);
                        }}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start Adaptive Test
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              {subjects.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No subjects available for adaptive testing.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Practice Chapters */}
        <TabsContent value="practice" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-green-600" />
                <span>Practice Chapters</span>
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Practice specific chapters with focused question sets
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              
              {/* Subject Selector */}
              <div>
                <label className="text-sm font-medium mb-2 block">Select Subject:</label>
                <div className="grid gap-2 md:grid-cols-3">
                  {subjects.map((subject: any) => (
                    <Button
                      key={subject.id || subject.subject_code}
                      variant={selectedSubject === (subject.id || subject.subject_code) ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedSubject(subject.id || subject.subject_code)}
                      className="justify-start"
                    >
                      {subject.name || subject.subject_name}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Chapter Selector */}
              {selectedSubject && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Available Chapters:</label>
                  <div className="grid gap-4 md:grid-cols-2">
                    {chapters.map((chapter: any) => (
                      <Card 
                        key={chapter.id || chapter.chapter_id}
                        className="border-green-200 hover:border-green-400 transition-colors cursor-pointer"
                        onClick={() => onStartExam('practice_chapter', chapter.id || chapter.chapter_id, chapter.name || chapter.chapter_name)}
                      >
                        <CardContent className="p-4 space-y-3">
                          <h4 className="font-semibold">{chapter.name || chapter.chapter_name}</h4>
                          
                          <div className="space-y-2 text-sm text-muted-foreground">
                            <div className="flex items-center space-x-2">
                              <FileText className="h-3 w-3" />
                              <span>{chapter.question_count || '10-20'} questions available</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Clock className="h-3 w-3" />
                              <span>~15-30 minutes</span>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              <Badge variant="outline" className="text-xs">Easy</Badge>
                              <Badge variant="outline" className="text-xs">Medium</Badge>
                              <Badge variant="outline" className="text-xs">Hard</Badge>
                            </div>
                          </div>

                          <Button 
                            className="w-full" 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              onStartExam('practice_chapter', chapter.id || chapter.chapter_id, chapter.name || chapter.chapter_name);
                            }}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Start Practice
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                  
                  {chapters.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No practice chapters available for this subject.</p>
                    </div>
                  )}
                </div>
              )}
              
              {!selectedSubject && (
                <div className="text-center py-8 text-muted-foreground">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a subject to view available practice chapters.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scheduled Exams */}
        <TabsContent value="scheduled" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Calendar className="h-5 w-5 text-purple-600" />
                    <span>Scheduled Exams</span>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Pre-scheduled exams with enhanced features
                  </p>
                </div>
                <Button variant="outline" onClick={onViewScheduled}>
                  View All Scheduled
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {scheduledExams.slice(0, 4).map((exam: any) => (
                  <Card 
                    key={exam.id}
                    className="border-purple-200 hover:border-purple-400 transition-colors"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-2">
                          <h4 className="font-semibold">{exam.exam_name}</h4>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span className="flex items-center space-x-1">
                              <BookOpen className="h-3 w-3" />
                              <span>{exam.subject || 'General'}</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <Clock className="h-3 w-3" />
                              <span>{exam.duration_minutes} minutes</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <FileText className="h-3 w-3" />
                              <span>{exam.question_count || 'Dynamic'} questions</span>
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="bg-purple-50">
                            {exam.status || 'Available'}
                          </Badge>
                          <Button 
                            size="sm"
                            onClick={() => onStartExam('scheduled_exam', exam.id, exam.exam_name)}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Start
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              {scheduledExams.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No scheduled exams available.</p>
                </div>
              )}
              
              {scheduledExams.length > 4 && (
                <div className="text-center mt-4">
                  <Button variant="outline" onClick={onViewScheduled}>
                    View All {scheduledExams.length} Scheduled Exams
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}