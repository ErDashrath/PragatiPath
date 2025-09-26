import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calculator, Puzzle, BookOpen, BarChart3 } from "lucide-react";
import { AssessmentAPI, type Subject } from "@/lib/assessment-api";

interface ModulesViewProps {
  onModuleSelect: (subjectCode: string) => void;
}

export default function ModulesView({ onModuleSelect }: ModulesViewProps) {
  const { data: subjects, isLoading } = useQuery({
    queryKey: ["subjects"],
    queryFn: AssessmentAPI.getSubjects,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const getSubjectIcon = (subjectCode: string) => {
    switch (subjectCode) {
      case 'quantitative_aptitude': return Calculator;
      case 'logical_reasoning': return Puzzle;
      case 'verbal_ability': return BookOpen;
      case 'data_interpretation': return BarChart3;
      default: return Calculator;
    }
  };

  const getSubjectGradient = (subjectCode: string) => {
    switch (subjectCode) {
      case 'quantitative_aptitude': return 'bg-gradient-to-br from-primary to-primary/80';
      case 'logical_reasoning': return 'bg-gradient-to-br from-secondary to-secondary/80';
      case 'verbal_ability': return 'bg-gradient-to-br from-accent to-accent/80';
      case 'data_interpretation': return 'bg-gradient-to-br from-chart-4 to-chart-4/80';
      default: return 'bg-gradient-to-br from-primary to-primary/80';
    }
  };

  const getSubjectProgress = (subjectCode: string) => {
    // Mock progress data - in real app, this would come from user progress API
    const progressData: Record<string, number> = {
      'quantitative_aptitude': 68,
      'logical_reasoning': 52,
      'verbal_ability': 74,
      'data_interpretation': 61,
    };
    return progressData[subjectCode] || 0;
  };

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Learning Modules</h2>
        <p className="text-muted-foreground">Choose a module to begin your adaptive learning journey</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {subjects?.map((subject: Subject) => {
          const Icon = getSubjectIcon(subject.code);
          const progress = getSubjectProgress(subject.code);
          
          return (
            <Card
              key={subject.id}
              className="overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer group"
              onClick={() => onModuleSelect(subject.code)}
              data-testid={`subject-card-${subject.code}`}
            >
              <div className={`h-32 flex items-center justify-center ${getSubjectGradient(subject.code)}`}>
                <Icon className="h-16 w-16 text-white" />
              </div>
              
              <CardContent className="p-6">
                <h3 className="text-xl font-bold text-foreground mb-2 group-hover:text-primary transition-colors">
                  {subject.name}
                </h3>
                <p className="text-muted-foreground mb-4 text-sm">
                  {subject.description}
                </p>
                
                {/* Progress Bar */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium text-foreground">{progress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Start Assessment Button */}
                <Button 
                  className="w-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    onModuleSelect(subject.code);
                  }}
                >
                  Start Assessment
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Subject Statistics */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Your Subject Statistics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {subjects?.map((subject) => {
              const progress = getSubjectProgress(subject.code);
              return (
                <div key={subject.id} className="text-center p-4 rounded-lg bg-primary/10">
                  <div className="text-2xl font-bold text-primary mb-2">{progress}%</div>
                  <div className="text-sm font-medium text-foreground mb-1">{subject.name}</div>
                  <div className="text-xs text-muted-foreground">Ready for assessment</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
