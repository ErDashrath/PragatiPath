import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calculator, Puzzle, BookOpen, BarChart3, Lock } from "lucide-react";
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
      'logical_reasoning': 80,
      'verbal_ability': 74,
      'data_interpretation': 61,
    };
    return progressData[subjectCode] || 0;
  };

  const getSubjectChapters = (subjectCode: string) => {
    const chaptersData: Record<string, Array<{title: string, description: string, progress: number, questions: number, time: string}>> = {
      'quantitative_aptitude': [
        { title: 'Percentages', description: 'Chapter 1 of Quantitative Aptitude: Percentages', progress: 75, questions: 10, time: '15min' },
        { title: 'Profit and Loss', description: 'Chapter 2 of Quantitative Aptitude: Profit and Loss', progress: 60, questions: 10, time: '15min' },
        { title: 'Ratios and Proportions', description: 'Chapter 3 of Quantitative Aptitude: Ratios and Proportions', progress: 65, questions: 10, time: '15min' },
        { title: 'Arithmetic', description: 'Chapter 4 of Quantitative Aptitude: Arithmetic', progress: 70, questions: 10, time: '15min' }
      ],
      'logical_reasoning': [
        { title: 'Pattern Recognition', description: 'Chapter 1 of Logical Reasoning: Pattern Recognition', progress: 85, questions: 10, time: '15min' },
        { title: 'Syllogisms', description: 'Chapter 2 of Logical Reasoning: Syllogisms', progress: 78, questions: 10, time: '15min' },
        { title: 'Coding-Decoding', description: 'Chapter 3 of Logical Reasoning: Coding-Decoding', progress: 82, questions: 10, time: '15min' },
        { title: 'Blood Relations', description: 'Chapter 4 of Logical Reasoning: Blood Relations', progress: 75, questions: 10, time: '15min' }
      ],
      'verbal_ability': [
        { title: 'Vocabulary', description: 'Chapter 1 of Verbal Ability: Vocabulary', progress: 85, questions: 10, time: '15min' },
        { title: 'Grammar', description: 'Chapter 2 of Verbal Ability: Grammar', progress: 75, questions: 10, time: '15min' },
        { title: 'Reading Comprehension', description: 'Chapter 3 of Verbal Ability: Reading Comprehension', progress: 80, questions: 10, time: '15min' },
        { title: 'Sentence Correction', description: 'Chapter 4 of Verbal Ability: Sentence Correction', progress: 68, questions: 10, time: '15min' }
      ],
      'data_interpretation': [
        { title: 'Bar Charts', description: 'Chapter 1 of Data Interpretation: Bar Charts', progress: 70, questions: 10, time: '15min' },
        { title: 'Line Graphs', description: 'Chapter 2 of Data Interpretation: Line Graphs', progress: 65, questions: 10, time: '15min' },
        { title: 'Pie Charts', description: 'Chapter 3 of Data Interpretation: Pie Charts', progress: 58, questions: 10, time: '15min' },
        { title: 'Case Studies', description: 'Chapter 4 of Data Interpretation: Case Studies', progress: 45, questions: 10, time: '15min' }
      ]
    };
    return chaptersData[subjectCode] || [];
  };

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Learning Modules</h2>
        <p className="text-muted-foreground">Choose a module to begin your adaptive learning journey</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects?.filter((subject: Subject) => 
          ['quantitative_aptitude', 'logical_reasoning', 'verbal_ability', 'data_interpretation'].includes(subject.code)
        ).map((subject: Subject) => {
          const Icon = getSubjectIcon(subject.code);
          const progress = getSubjectProgress(subject.code);
          const chapters = getSubjectChapters(subject.code);
          
          return (
            <Card
              key={subject.id}
              className="overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group transform hover:-translate-y-2 border-2 border-gray-200 hover:border-primary/50 h-auto min-h-[500px] bg-gradient-to-br from-white to-gray-50"
              onClick={() => onModuleSelect(subject.code)}
              data-testid={`subject-card-${subject.code}`}
            >
              <div className={`h-24 flex items-center justify-center ${getSubjectGradient(subject.code)} relative`}>
                <div className="relative bg-white/20 backdrop-blur-sm rounded-xl p-3">
                  <Icon className="h-7 w-7 text-white" />
                </div>
              </div>
              
              <CardContent className="p-5 flex flex-col justify-between flex-1">
                <div className="space-y-3 flex-1">
                  <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors leading-tight">
                    {subject.name}
                  </h3>
                  <p className="text-muted-foreground text-xs leading-relaxed">
                    {subject.description}
                  </p>

                  {/* Chapter/Topic List */}
                  {chapters.length > 0 && (
                    <div className="space-y-2 mt-3">
                      <h4 className="text-sm font-semibold text-foreground">Topics:</h4>
                      {chapters.map((chapter, index) => {
                        const isLocked = index === 3; // 4th card (index 3) is locked
                        return (
                          <div 
                            key={index} 
                            className={`relative rounded-lg p-2 border transition-all duration-200 ${
                              isLocked 
                                ? 'bg-gray-100 border-gray-300 opacity-75 cursor-not-allowed' 
                                : 'bg-gray-50 border-gray-200 hover:bg-primary/10 hover:border-primary/30 cursor-pointer hover:shadow-sm'
                            }`}
                            onClick={(e) => {
                              e.stopPropagation();
                              if (!isLocked) {
                                onModuleSelect(`${subject.code}_${chapter.title.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}`);
                              }
                            }}
                          >
                            {isLocked && (
                              <div className="absolute -top-2 -right-2 bg-gray-600 rounded-full p-1 shadow-md">
                                <Lock className="h-3 w-3 text-white" />
                              </div>
                            )}
                            <div className="flex items-center justify-between">
                              <span className={`text-xs font-medium ${
                                isLocked ? 'text-gray-500' : 'text-foreground hover:text-primary'
                              }`}>
                                {chapter.title}
                              </span>
                              <span className={`text-xs font-bold ${
                                isLocked ? 'text-gray-400' : 'text-primary'
                              }`}>
                                {isLocked ? '--' : `${chapter.progress}%`}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
                  
                {/* Progress Bar */}
                <div className="space-y-3 mt-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground font-medium">Overall Progress</span>
                    <span className="text-foreground font-bold">{progress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2.5">
                    <div 
                      className="bg-gradient-to-r from-primary to-primary/80 h-full rounded-full transition-all duration-300" 
                      style={{ width: `${progress}%` }}
                    >
                    </div>
                  </div>
                  
                  <Button 
                    className="w-full h-9 text-sm font-semibold rounded-lg mt-3"
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
            {subjects?.filter((subject) => 
              ['quantitative_aptitude', 'logical_reasoning', 'verbal_ability', 'data_interpretation'].includes(subject.code)
            ).map((subject) => {
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
