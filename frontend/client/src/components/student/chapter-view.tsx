import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { ArrowLeft, CheckCircle, PlayCircle, Lock, Clock, HelpCircle, Settings } from "lucide-react";
import { AssessmentAPI, type Subject, type Chapter } from "@/lib/assessment-api";

interface ChapterViewProps {
  subjectCode: string;
  onBackToModules: () => void;
  onChapterSelect: (chapter: Chapter, subject: Subject, config?: AssessmentConfig) => void;
}

interface AssessmentConfig {
  questionCount: number;
  timeLimit: number; // in minutes
}

export default function ChapterView({ subjectCode, onBackToModules, onChapterSelect }: ChapterViewProps) {
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [questionCount, setQuestionCount] = useState<number>(10);
  const [timeLimit, setTimeLimit] = useState<number>(15);
  const [showConfig, setShowConfig] = useState<number | null>(null);
  // Get subject details
  const { data: subjects } = useQuery({
    queryKey: ["subjects"],
    queryFn: AssessmentAPI.getSubjects,
  });

  const subject = subjects?.find(s => s.code === subjectCode);

  // Get chapters for this subject
  const { data: chapters, isLoading } = useQuery({
    queryKey: ["chapters", subject?.id],
    queryFn: () => AssessmentAPI.getChapters(subject!.id),
    enabled: !!subject?.id,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-chart-4" />;
      case 'in-progress':
        return <PlayCircle className="h-6 w-6 text-accent" />;
      case 'locked':
        return <Lock className="h-6 w-6 text-muted-foreground" />;
      default:
        return <Lock className="h-6 w-6 text-muted-foreground" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in-progress': return 'In Progress';
      case 'locked': return 'Locked';
      default: return 'Locked';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-chart-4';
      case 'in-progress': return 'text-accent';
      case 'locked': return 'text-muted-foreground';
      default: return 'text-muted-foreground';
    }
  };

  if (isLoading || !chapters || !subject) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={onBackToModules}
          className="mb-4 p-0 h-auto font-normal text-muted-foreground hover:text-foreground"
          data-testid="button-back-to-modules"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Subjects
        </Button>
        
        <h2 className="text-2xl font-bold text-foreground mb-2">
          {subject.name}
        </h2>
        <p className="text-muted-foreground mb-4">Select a chapter to start assessment</p>
        
        {/* Default Configuration Display */}
        <Card className="mb-6 border-primary/20 bg-primary/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1 text-muted-foreground">
                <Settings className="h-4 w-4" />
                <span className="font-medium">Default Settings:</span>
              </div>
              <div className="flex items-center gap-1">
                <HelpCircle className="h-3 w-3" />
                <span>{questionCount} Questions</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{timeLimit} Minutes</span>
              </div>
              <Badge variant="secondary" className="text-xs">Customizable per chapter</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="chapters-grid">
        {chapters?.map((chapter: Chapter) => {
          const isLocked = chapter.chapter_number === 4; // 4th chapter is locked
          return (
            <Card
              key={chapter.id}
              className={`transition-all duration-300 border-2 relative ${
                isLocked 
                  ? 'opacity-75 border-gray-300 cursor-not-allowed' 
                  : 'hover:shadow-lg hover:border-primary/30'
              }`}
              data-testid={`chapter-card-${chapter.id}`}
            >
              {isLocked && (
                <div className="absolute -top-3 -right-3 bg-gray-600 rounded-full p-2 shadow-lg z-10">
                  <Lock className="h-4 w-4 text-white" />
                </div>
              )}
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className={`text-lg font-semibold ${
                    isLocked ? 'text-gray-500' : 'text-foreground'
                  }`}>
                    {chapter.name}
                  </h3>
                  <PlayCircle className={`h-6 w-6 ${
                    isLocked ? 'text-gray-400' : 'text-primary'
                  }`} />
                </div>
                
                <p className={`text-sm mb-4 min-h-[40px] ${
                  isLocked ? 'text-gray-400' : 'text-muted-foreground'
                }`}>
                  {chapter.description}
                </p>
                
                <div className="space-y-4">
                  <Badge variant="outline" className={`text-xs ${
                    isLocked ? 'border-gray-300 text-gray-400' : ''
                  }`}>
                    Chapter {chapter.chapter_number}
                  </Badge>

                  {/* Assessment Configuration */}
                  {!isLocked && showConfig === chapter.id ? (
                  <div className="space-y-4 p-4 bg-muted/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <Settings className="h-4 w-4 text-primary" />
                      <span className="text-sm font-semibold text-foreground">Assessment Settings</span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="space-y-2">
                        <Label className="text-xs font-medium flex items-center gap-1">
                          <HelpCircle className="h-3 w-3" />
                          Number of Questions
                        </Label>
                        <Select value={questionCount.toString()} onValueChange={(value) => setQuestionCount(parseInt(value))}>
                          <SelectTrigger className="h-8 text-xs">
                            <SelectValue placeholder="Select questions" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="5">5 Questions</SelectItem>
                            <SelectItem value="10">10 Questions</SelectItem>
                            <SelectItem value="15">15 Questions</SelectItem>
                            <SelectItem value="20">20 Questions</SelectItem>
                            <SelectItem value="25">25 Questions</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-xs font-medium flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Time Limit
                        </Label>
                        <Select value={timeLimit.toString()} onValueChange={(value) => setTimeLimit(parseInt(value))}>
                          <SelectTrigger className="h-8 text-xs">
                            <SelectValue placeholder="Select time" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="5">5 Minutes</SelectItem>
                            <SelectItem value="10">10 Minutes</SelectItem>
                            <SelectItem value="15">15 Minutes</SelectItem>
                            <SelectItem value="20">20 Minutes</SelectItem>
                            <SelectItem value="30">30 Minutes</SelectItem>
                            <SelectItem value="45">45 Minutes</SelectItem>
                            <SelectItem value="60">60 Minutes</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                      <Button
                        size="sm"
                        className="flex-1 h-8 text-xs"
                        onClick={() => {
                          const config: AssessmentConfig = { questionCount, timeLimit };
                          onChapterSelect(chapter, subject, config);
                        }}
                        data-testid={`button-start-chapter-${chapter.id}`}
                      >
                        Start Assessment
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8 text-xs"
                        onClick={() => setShowConfig(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                  ) : !isLocked ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <HelpCircle className="h-3 w-3" />
                          Questions: {questionCount}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Time: {timeLimit}min
                        </span>
                      </div>
                      
                      <Button
                        size="sm"
                        className="w-full h-8 text-xs"
                        onClick={() => setShowConfig(chapter.id)}
                        data-testid={`button-configure-chapter-${chapter.id}`}
                      >
                        Configure & Start
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center justify-center text-xs text-gray-400 py-2">
                        <Lock className="h-3 w-3 mr-1" />
                        Complete previous chapters to unlock
                      </div>
                      
                      <Button
                        size="sm"
                        className="w-full h-8 text-xs"
                        disabled
                        variant="secondary"
                      >
                        Locked
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Chapter Information */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Chapter Learning Path</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 rounded-lg bg-muted/30">
              <div className="w-8 h-8 rounded-full bg-chart-4 text-white flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <p className="font-medium text-foreground">Initial Assessment</p>
                <p className="text-sm text-muted-foreground">Adaptive test to determine your current skill level</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 rounded-lg bg-muted/30">
              <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <p className="font-medium text-foreground">Personalized Learning</p>
                <p className="text-sm text-muted-foreground">Targeted content based on your fundamental gaps</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 rounded-lg bg-muted/30">
              <div className="w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <p className="font-medium text-foreground">Spaced Practice</p>
                <p className="text-sm text-muted-foreground">Regular practice sessions to reinforce learning</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 rounded-lg bg-muted/30">
              <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center text-sm font-bold">
                4
              </div>
              <div>
                <p className="font-medium text-foreground">Mastery Assessment</p>
                <p className="text-sm text-muted-foreground">Final evaluation to confirm chapter completion</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
