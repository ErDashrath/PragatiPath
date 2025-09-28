import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Headphones, Brain, Database, Rocket, Calculator, Puzzle, BookOpen, Play, Dumbbell, Target, TrendingUp, Zap } from "lucide-react";
import ProgressCircle from "@/components/ui/progress-circle";

type StudentView = 'dashboard' | 'adaptive' | 'modules' | 'practice' | 'history' | 'reports' | 'chapter' | 'assessment';

interface DashboardOverviewProps {
  onNavigate: (view: StudentView) => void;
}

export default function DashboardOverview({ onNavigate }: DashboardOverviewProps) {
  const { user } = useAuth();
  
  const { data: studentProfile, isLoading } = useQuery({
    queryKey: ["/api/student-profile", user?.id],
    enabled: !!user?.id,
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

  // const fundamentalsData = [
  //   {
  //     title: "Listening",
  //     description: "Audio comprehension",
  //     score: studentProfile?.listeningScore || 65,
  //     icon: Headphones,
  //     color: "hsl(221 83% 53%)",
  //     status: (studentProfile?.listeningScore || 65) < 60 ? "critical" : 
  //             (studentProfile?.listeningScore || 65) < 75 ? "needs-improvement" : "good"
  //   },
  //   {
  //     title: "Grasping",
  //     description: "Concept understanding",
  //     score: studentProfile?.graspingScore || 72,
  //     icon: Brain,
  //     color: "hsl(178 78% 35%)",
  //     status: (studentProfile?.graspingScore || 72) < 60 ? "critical" : 
  //             (studentProfile?.graspingScore || 72) < 75 ? "stable" : "good"
  //   },
  //   {
  //     title: "Retention",
  //     description: "Memory & recall",
  //     score: studentProfile?.retentionScore || 58,
  //     icon: Database,
  //     color: "hsl(43 96% 56%)",
  //     status: (studentProfile?.retentionScore || 58) < 60 ? "critical" : 
  //             (studentProfile?.retentionScore || 58) < 75 ? "needs-improvement" : "good"
  //   },
  //   {
  //     title: "Application",
  //     description: "Problem solving",
  //     score: studentProfile?.applicationScore || 81,
  //     icon: Rocket,
  //     color: "hsl(142 76% 36%)",
  //     status: (studentProfile?.applicationScore || 81) < 60 ? "critical" : 
  //             (studentProfile?.applicationScore || 81) < 75 ? "needs-improvement" : "excellent"
  //   }
  // ];

  const getStatusText = (status: string): { text: string; className: string } => {
    switch (status) {
      case 'critical': return { text: '▼ Critical gap', className: 'text-destructive' };
      case 'needs-improvement': return { text: '▼ Needs improvement', className: 'text-destructive' };
      case 'stable': return { text: '— Stable', className: 'text-muted-foreground' };
      case 'good': return { text: '▲ Good', className: 'text-chart-4' };
      case 'excellent': return { text: '▲ Excellent', className: 'text-chart-4' };
      default: return { text: '— Stable', className: 'text-muted-foreground' };
    }
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Welcome back, {user?.name}!
        </h2>
        <p className="text-muted-foreground">Here's your learning progress overview</p>
      </div>

      

      {/* Recent Activity and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Recent Activity</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/50" data-testid="activity-percentages">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Calculator className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">Percentages Practice</p>
                  <p className="text-xs text-muted-foreground">Quantitative Aptitude • 2 hours ago</p>
                </div>
                <span className="text-sm font-medium text-chart-4">+12%</span>
              </div>
              
              <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/50" data-testid="activity-pattern-recognition">
                <div className="h-8 w-8 rounded-full bg-secondary/10 flex items-center justify-center">
                  <Puzzle className="h-4 w-4 text-secondary" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">Pattern Recognition</p>
                  <p className="text-xs text-muted-foreground">Logical Reasoning • Yesterday</p>
                </div>
                <span className="text-sm font-medium text-chart-4">+8%</span>
              </div>
              
              <div className="flex items-center space-x-3 p-3 rounded-lg bg-muted/50" data-testid="activity-reading-comprehension">
                <div className="h-8 w-8 rounded-full bg-accent/10 flex items-center justify-center">
                  <BookOpen className="h-4 w-4 text-accent" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">Reading Comprehension</p>
                  <p className="text-xs text-muted-foreground">Verbal Ability • 2 days ago</p>
                </div>
                <span className="text-sm font-medium text-destructive">-3%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
            {/* Adaptive Learning Feature Highlight */}
            <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 dark:from-blue-950 dark:to-purple-950 dark:border-blue-800">
              <Button
                onClick={() => onNavigate('adaptive')}
                className="w-full h-auto p-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 flex items-center justify-center space-x-3 group transition-all duration-300 shadow-lg hover:shadow-xl"
                data-testid="adaptive-learning-cta"
              >
                <Zap className="h-6 w-6 text-white group-hover:scale-110 transition-transform" />
                <div className="text-center">
                  <div className="text-lg font-bold text-white">🧠 AI Adaptive Learning</div>
                  <div className="text-sm text-blue-100">Personalized practice powered by AI</div>
                </div>
              </Button>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2 group hover:border-primary/50 transition-colors"
                onClick={() => onNavigate('adaptive')}
                data-testid="quick-action-assessment"
              >
                <Play className="h-8 w-8 text-primary group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium">Adaptive Learning</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2 group hover:border-secondary/50 transition-colors"
                onClick={() => onNavigate('modules')}
                data-testid="quick-action-practice"
              >
                <Dumbbell className="h-8 w-8 text-secondary group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium">Modules</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2 group hover:border-accent/50 transition-colors"
                onClick={() => onNavigate('history')}
                data-testid="quick-action-targeted"
              >
                <Target className="h-8 w-8 text-accent group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium">History</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-auto p-4 flex flex-col items-center space-y-2 group hover:border-chart-4/50 transition-colors"
                onClick={() => onNavigate('reports')}
                data-testid="quick-action-progress"
              >
                <TrendingUp className="h-8 w-8 text-chart-4 group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium">View Progress</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
