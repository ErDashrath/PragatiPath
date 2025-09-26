import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Eye, UserPlus } from "lucide-react";

export default function StudentsList() {
  const { data: students, isLoading } = useQuery({
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

  const getStatusBadge = (student: any) => {
    const fundamentalScores = [
      student.listeningScore || 50,
      student.graspingScore || 50,
      student.retentionScore || 50,
      student.applicationScore || 50,
    ];
    
    const avgScore = fundamentalScores.reduce((sum, score) => sum + score, 0) / 4;
    const hasLowScore = fundamentalScores.some(score => score < 60);
    
    if (hasLowScore && avgScore < 60) {
      return <Badge className="bg-destructive/10 text-destructive">Needs Attention</Badge>;
    } else if (avgScore >= 80) {
      return <Badge className="bg-chart-4/10 text-chart-4">Excellent</Badge>;
    } else {
      return <Badge className="bg-accent/10 text-accent">Good</Badge>;
    }
  };

  const getOverallProgress = (student: any) => {
    const moduleProgress = student.moduleProgress || {};
    const modules = [moduleProgress.quantitative, moduleProgress.logical, moduleProgress.verbal];
    const validModules = modules.filter(score => score !== undefined);
    
    if (validModules.length === 0) return 0;
    return Math.floor(validModules.reduce((sum, score) => sum + score, 0) / validModules.length);
  };

  const getProgressBarWidth = (progress: number) => {
    return Math.max(0, Math.min(100, progress));
  };

  const getScoreColor = (score: number) => {
    if (score < 60) return 'text-destructive';
    if (score >= 80) return 'text-chart-4';
    return 'text-accent';
  };

  const handleViewStudent = (studentId: string) => {
    alert(`Viewing detailed profile for student: ${studentId}`);
  };

  const handleAssignWork = (studentId: string) => {
    alert(`Assigning targeted practice for student: ${studentId}`);
  };

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Student Management</h2>
        <p className="text-muted-foreground">Monitor individual student progress and performance</p>
      </div>

      {/* Student List */}
      <Card className="overflow-hidden">
        <div className="p-6 border-b border-border">
          <div className="flex flex-col sm:flex-row gap-4 justify-between">
            <h3 className="text-lg font-semibold text-foreground">All Students</h3>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search students..."
                  className="pl-10 w-full sm:w-64"
                  data-testid="search-students"
                />
              </div>
              <select 
                className="px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                data-testid="filter-status"
              >
                <option>All Status</option>
                <option>Active</option>
                <option>Needs Attention</option>
                <option>Excellent</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* Desktop Table View */}
        <div className="hidden lg:block overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Overall Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Listening
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Grasping
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Retention
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Application
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {students?.map((student: any, index: number) => {
                const overallProgress = getOverallProgress(student);
                const initials = student.userId?.substring(0, 2).toUpperCase() || 'ST';
                
                return (
                  <tr 
                    key={student.id} 
                    className="hover:bg-muted/30 transition-colors"
                    data-testid={`student-row-${index}`}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-sm font-medium text-primary">{initials}</span>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-foreground">Student {index + 1}</p>
                          <p className="text-xs text-muted-foreground">ID: {student.userId?.substring(0, 8)}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 h-2 bg-muted rounded-full mr-2">
                          <div 
                            className="h-2 bg-primary rounded-full transition-all duration-300"
                            style={{ width: `${getProgressBarWidth(overallProgress)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-foreground">{overallProgress}%</span>
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(student.listeningScore || 50)}`}>
                      {student.listeningScore || 50}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(student.graspingScore || 50)}`}>
                      {student.graspingScore || 50}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(student.retentionScore || 50)}`}>
                      {student.retentionScore || 50}%
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${getScoreColor(student.applicationScore || 50)}`}>
                      {student.applicationScore || 50}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(student)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleViewStudent(student.id)}
                          className="text-primary hover:text-primary/80 hover:bg-primary/10"
                          data-testid={`view-student-${index}`}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleAssignWork(student.id)}
                          className="text-secondary hover:text-secondary/80 hover:bg-secondary/10"
                          data-testid={`assign-student-${index}`}
                        >
                          <UserPlus className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Mobile Card View */}
        <div className="lg:hidden divide-y divide-border">
          {students?.map((student: any, index: number) => {
            const overallProgress = getOverallProgress(student);
            const initials = student.userId?.substring(0, 2).toUpperCase() || 'ST';
            
            return (
              <div 
                key={student.id} 
                className="p-6 space-y-4"
                data-testid={`mobile-student-card-${index}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-sm font-medium text-primary">{initials}</span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-foreground">Student {index + 1}</p>
                      <p className="text-xs text-muted-foreground">ID: {student.userId?.substring(0, 8)}</p>
                    </div>
                  </div>
                  {getStatusBadge(student)}
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-muted-foreground">Overall Progress</span>
                      <span className="font-medium">{overallProgress}%</span>
                    </div>
                    <div className="w-full h-2 bg-muted rounded-full">
                      <div 
                        className="h-2 bg-primary rounded-full transition-all duration-300"
                        style={{ width: `${getProgressBarWidth(overallProgress)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Listening:</span>
                      <span className={getScoreColor(student.listeningScore || 50)}>
                        {student.listeningScore || 50}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Grasping:</span>
                      <span className={getScoreColor(student.graspingScore || 50)}>
                        {student.graspingScore || 50}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Retention:</span>
                      <span className={getScoreColor(student.retentionScore || 50)}>
                        {student.retentionScore || 50}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Application:</span>
                      <span className={getScoreColor(student.applicationScore || 50)}>
                        {student.applicationScore || 50}%
                      </span>
                    </div>
                  </div>

                  <div className="flex space-x-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleViewStudent(student.id)}
                      className="flex-1"
                      data-testid={`mobile-view-student-${index}`}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAssignWork(student.id)}
                      className="flex-1"
                      data-testid={`mobile-assign-student-${index}`}
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Assign
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Students Summary */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Class Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4" data-testid="class-summary">
            <div className="text-center p-4 rounded-lg bg-chart-4/10">
              <div className="text-2xl font-bold text-chart-4 mb-2">
                {students?.filter((s: any) => getOverallProgress(s) >= 80).length || 0}
              </div>
              <div className="text-sm font-medium text-foreground">Excellent Students</div>
              <div className="text-xs text-muted-foreground">≥80% overall</div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-accent/10">
              <div className="text-2xl font-bold text-accent mb-2">
                {students?.filter((s: any) => {
                  const progress = getOverallProgress(s);
                  return progress >= 60 && progress < 80;
                }).length || 0}
              </div>
              <div className="text-sm font-medium text-foreground">Good Students</div>
              <div className="text-xs text-muted-foreground">60-79% overall</div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-destructive/10">
              <div className="text-2xl font-bold text-destructive mb-2">
                {students?.filter((s: any) => getOverallProgress(s) < 60).length || 0}
              </div>
              <div className="text-sm font-medium text-foreground">Need Support</div>
              <div className="text-xs text-muted-foreground">&lt;60% overall</div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-primary/10">
              <div className="text-2xl font-bold text-primary mb-2">
                {Math.floor((students?.reduce((sum: number, s: any) => sum + getOverallProgress(s), 0) || 0) / (students?.length || 1))}%
              </div>
              <div className="text-sm font-medium text-foreground">Class Average</div>
              <div className="text-xs text-muted-foreground">Overall progress</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
