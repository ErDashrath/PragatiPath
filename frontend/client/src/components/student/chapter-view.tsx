import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, CheckCircle, PlayCircle, Lock } from "lucide-react";
import { AssessmentAPI, type Subject, type Chapter } from "@/lib/assessment-api";

interface ChapterViewProps {
  subjectCode: string;
  onBackToModules: () => void;
  onChapterSelect: (chapter: Chapter, subject: Subject) => void;
}

export default function ChapterView({ subjectCode, onBackToModules, onChapterSelect }: ChapterViewProps) {
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
        <p className="text-muted-foreground">Select a chapter to start assessment</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="chapters-grid">
        {chapters?.map((chapter: Chapter) => (
          <Card
            key={chapter.id}
            className="hover:shadow-md transition-all duration-300 cursor-pointer"
            onClick={() => onChapterSelect(chapter, subject)}
            data-testid={`chapter-card-${chapter.id}`}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-foreground">
                  {chapter.name}
                </h3>
                <PlayCircle className="h-6 w-6 text-primary" />
              </div>
              
              <p className="text-sm text-muted-foreground mb-4">
                {chapter.description}
              </p>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-primary">
                  Chapter {chapter.chapter_number}
                </span>
                
                <Button
                  size="sm"
                  className="ml-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    onChapterSelect(chapter, subject);
                  }}
                  data-testid={`button-start-chapter-${chapter.id}`}
                >
                  Start Assessment
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
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
