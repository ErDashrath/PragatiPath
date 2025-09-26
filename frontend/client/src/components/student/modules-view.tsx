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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects?.map((subject: Subject) => {
          const Icon = getSubjectIcon(subject.code);
          const progress = getSubjectProgress(subject.code);
          
          return (
            <Card
              key={subject.id}
              className="overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group transform hover:-translate-y-2 border-2 border-gray-200 hover:border-primary/50 h-64 bg-gradient-to-br from-white to-gray-50"
              onClick={() => onModuleSelect(subject.code)}
              data-testid={`subject-card-${subject.code}`}
            >
              <div className={`h-24 flex items-center justify-center ${getSubjectGradient(subject.code)} relative`}>
                <div className="relative bg-white/20 backdrop-blur-sm rounded-xl p-3">
                  <Icon className="h-8 w-8 text-white" />
                </div>
              </div>
              
              <CardContent className="p-4 h-40 flex flex-col justify-between">
                <div className="space-y-2">
                  <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors leading-tight">
                    {subject.name}
                  </h3>
                  <p className="text-muted-foreground text-sm leading-relaxed line-clamp-2">
                    {subject.description}
                  </p>
                </div>
                  
                {/* Compact Progress Bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="text-foreground font-semibold">{progress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-primary to-primary/80 h-full rounded-full transition-all duration-300" 
                      style={{ width: `${progress}%` }}
                    >
                    </div>
                  </div>
                  
                  <Button 
                    className="w-full h-8 text-sm font-semibold rounded-lg"
                    onClick={(e) => {
                      e.stopPropagation();
                      onModuleSelect(subject.code);
                    }}
                  >
                    Start Assessment
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Subject Statistics - More Dramatic */}
      <Card className="border-4 border-gray-200 shadow-2xl hover:shadow-3xl transition-all duration-500">
        <CardContent className="p-12">
          <h3 className="text-3xl font-black text-foreground mb-10 text-center">Your Learning Statistics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {subjects?.map((subject) => {
              const progress = getSubjectProgress(subject.code);
              const Icon = getSubjectIcon(subject.code);
              return (
                <div key={subject.id} className="text-center p-8 rounded-3xl bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border-2 border-primary/20 hover:border-primary/40 transition-all duration-300 hover:scale-105 hover:shadow-xl min-h-[200px] flex flex-col justify-between">
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-2xl mb-4 shadow-lg">
                      <Icon className="h-8 w-8 text-white" />
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="text-5xl font-black text-primary mb-3 drop-shadow-sm">{progress}%</div>
                    <div className="text-lg font-black text-foreground mb-2 leading-tight">{subject.name}</div>
                    <div className={`text-sm font-bold px-4 py-2 rounded-full ${
                      progress >= 80 ? 'bg-green-100 text-green-800' :
                      progress >= 50 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {progress >= 80 ? '🏆 Mastered' : progress >= 50 ? '📚 Learning' : '🚀 Starting'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
