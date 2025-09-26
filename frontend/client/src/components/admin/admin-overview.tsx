import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, UserCheck, TrendingUp, AlertTriangle, FileText, Megaphone, CalendarPlus } from "lucide-react";

export default function AdminOverview() {
  const { data: classOverview, isLoading } = useQuery({
    queryKey: ["/api/admin/class-overview"],
  });

  const { data: students } = useQuery({
    queryKey: ["/api/admin/students"],
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

  const classStats = [
    {
      title: 'Total Students',
      value: classOverview?.totalStudents || 0,
      icon: Users,
      color: 'text-primary',
    },
    {
      title: 'Active This Week',
      value: classOverview?.activeThisWeek || 0,
      icon: UserCheck,
      color: 'text-chart-4',
    },
    {
      title: 'Average Progress',
      value: `${classOverview?.averageProgress || 0}%`,
      icon: TrendingUp,
      color: 'text-secondary',
    },
    {
      title: 'Need Attention',
      value: classOverview?.needingAttention || 0,
      icon: AlertTriangle,
      color: 'text-destructive',
    },
  ];

  const gapDistribution = classOverview?.gapDistribution || {};
  const gapData = [
    { name: 'Listening', score: gapDistribution.listening || 45, color: 'bg-destructive' },
    { name: 'Grasping', score: gapDistribution.grasping || 68, color: 'bg-accent' },
    { name: 'Retention', score: gapDistribution.retention || 38, color: 'bg-destructive' },
    { name: 'Application', score: gapDistribution.application || 72, color: 'bg-chart-4' },
  ];

  const getStudentsByPriority = () => {
    if (!students) return { critical: [], moderate: [] };
    
    const critical = students.filter((student: any) => {
      const fundamentalScores = [
        student.listeningScore,
        student.graspingScore, 
        student.retentionScore,
        student.applicationScore
      ];
      return fundamentalScores.some((score: number) => (score || 50) < 50);
    }).slice(0, 3);

    const moderate = students.filter((student: any) => {
      const fundamentalScores = [
        student.listeningScore,
        student.graspingScore, 
        student.retentionScore,
        student.applicationScore
      ];
      return fundamentalScores.some((score: number) => (score || 50) >= 50 && (score || 50) < 70);
    }).slice(0, 3);

    return { critical, moderate };
  };

  const { critical, moderate } = getStudentsByPriority();

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'report':
        alert('Generating comprehensive class performance report...');
        break;
      case 'intervention':
        alert('Creating intervention plan for students requiring attention...');
        break;
      case 'assessment':
        alert('Scheduling new adaptive assessment for the class...');
        break;
    }
  };

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Class Overview - Section A</h2>
        <p className="text-muted-foreground">Monitor student progress and identify areas needing attention</p>
      </div>

      {/* Class Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {classStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} data-testid={`class-stat-${stat.title.toLowerCase().replace(/\s+/g, '-')}`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                  </div>
                  <Icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Learning Gap Distribution and Students Needing Attention */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Gap Distribution */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Class-wide Learning Gap Distribution</h3>
            <div className="space-y-4" data-testid="gap-distribution">
              {gapData.map((gap) => (
                <div key={gap.name} className="flex items-center justify-between">
                  <span className="text-sm text-foreground">{gap.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 h-3 bg-muted rounded-full">
                      <div 
                        className={`h-3 ${gap.color} rounded-full transition-all duration-300`}
                        style={{ width: `${(gap.score / 100) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-foreground w-12">{gap.score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Students Requiring Attention */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Students Requiring Attention</h3>
            <div className="space-y-3" data-testid="students-attention">
              {critical.map((student: any, index: number) => (
                <div 
                  key={student.id} 
                  className="flex items-center justify-between p-3 rounded-lg bg-destructive/10"
                  data-testid={`critical-student-${index}`}
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {student.userId} {/* In real app, this would be user name */}
                    </p>
                    <p className="text-xs text-muted-foreground">Critical retention gap</p>
                  </div>
                  <Badge className="bg-destructive text-destructive-foreground">Critical</Badge>
                </div>
              ))}
              
              {moderate.map((student: any, index: number) => (
                <div 
                  key={student.id} 
                  className="flex items-center justify-between p-3 rounded-lg bg-accent/10"
                  data-testid={`moderate-student-${index}`}
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {student.userId} {/* In real app, this would be user name */}
                    </p>
                    <p className="text-xs text-muted-foreground">Moderate listening gap</p>
                  </div>
                  <Badge className="bg-accent text-accent-foreground">Moderate</Badge>
                </div>
              ))}
              
              <Button 
                variant="ghost" 
                className="w-full text-center text-primary hover:bg-primary/10"
                data-testid="view-all-students"
              >
                View All Students →
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              variant="outline"
              className="flex items-center space-x-3 p-4 hover:border-primary/50 justify-start"
              onClick={() => handleQuickAction('report')}
              data-testid="quick-action-report"
            >
              <FileText className="h-5 w-5 text-primary" />
              <span className="text-foreground">Generate Class Report</span>
            </Button>
            
            <Button
              variant="outline"
              className="flex items-center space-x-3 p-4 hover:border-secondary/50 justify-start"
              onClick={() => handleQuickAction('intervention')}
              data-testid="quick-action-intervention"
            >
              <Megaphone className="h-5 w-5 text-secondary" />
              <span className="text-foreground">Send Intervention Plan</span>
            </Button>
            
            <Button
              variant="outline"
              className="flex items-center space-x-3 p-4 hover:border-accent/50 justify-start"
              onClick={() => handleQuickAction('assessment')}
              data-testid="quick-action-assessment"
            >
              <CalendarPlus className="h-5 w-5 text-accent" />
              <span className="text-foreground">Schedule Assessment</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Class Performance Summary */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Weekly Performance Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-testid="performance-summary">
            <div className="text-center p-4 rounded-lg bg-primary/10">
              <div className="text-2xl font-bold text-primary mb-2">320</div>
              <div className="text-sm font-medium text-foreground">Total Assessments</div>
              <div className="text-xs text-muted-foreground">Completed this week</div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-secondary/10">
              <div className="text-2xl font-bold text-secondary mb-2">76%</div>
              <div className="text-sm font-medium text-foreground">Class Average</div>
              <div className="text-xs text-muted-foreground">+5% from last week</div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-chart-4/10">
              <div className="text-2xl font-bold text-chart-4 mb-2">18</div>
              <div className="text-sm font-medium text-foreground">Top Performers</div>
              <div className="text-xs text-muted-foreground">Above 80% overall</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
