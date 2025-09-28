import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { AssessmentAPI, type Subject, type Chapter } from "@/lib/assessment-api";
import { 
  Target, 
  TrendingUp, 
  AlertTriangle,
  Clock,
  CheckCircle,
  BookOpen,
  Award,
  Calendar,
  BarChart3,
  PieChart
} from "lucide-react";
import {
  LineChart,
  Line,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

interface AssessmentConfig {
  questionCount: number;
  timeLimit: number;
}

interface PersonalReportsViewProps {
  onNavigateToModule?: (subjectCode: string) => void;
  onNavigateToChapter?: (subjectCode: string) => void;
  onChapterSelect?: (chapter: Chapter, subject: Subject, config?: AssessmentConfig) => void;
}

export default function PersonalReportsView({ 
  onNavigateToModule, 
  onNavigateToChapter,
  onChapterSelect 
}: PersonalReportsViewProps) {
  const { user } = useAuth();

  // Get subjects to find Quantitative Aptitude
  const { data: subjects } = useQuery({
    queryKey: ["subjects"],
    queryFn: AssessmentAPI.getSubjects,
  });

  const quantitativeAptitudeSubject = subjects?.find(s => s.code === 'quantitative_aptitude');

  // Get chapters for Quantitative Aptitude
  const { data: chapters } = useQuery({
    queryKey: ["chapters", quantitativeAptitudeSubject?.id],
    queryFn: () => AssessmentAPI.getChapters(quantitativeAptitudeSubject!.id),
    enabled: !!quantitativeAptitudeSubject?.id,
  });

  const profitAndLossChapter = chapters?.find(c => 
    c.name.toLowerCase().includes('profit') && c.name.toLowerCase().includes('loss')
  );

  const handleStartProfitAndLossAssessment = () => {
    if (profitAndLossChapter && quantitativeAptitudeSubject && onChapterSelect) {
      onChapterSelect(profitAndLossChapter, quantitativeAptitudeSubject, {
        questionCount: 10,
        timeLimit: 15
      });
    } else {
      // Fallback to chapter navigation if direct assessment isn't available
      onNavigateToChapter?.('quantitative_aptitude');
    }
  };

  // Personal performance data
  const personalStats = {
    totalSessions: 42,
    totalQuestions: 350,
    averageAccuracy: 78,
    studyHours: 24,
    conceptsMastered: 15,
    currentStreak: 7,
    bestStreak: 12,
    totalPoints: 2840
  };

  const performanceTrend = [
    { day: 'Mon', accuracy: 65, time: 45 },
    { day: 'Tue', accuracy: 72, time: 38 },
    { day: 'Wed', accuracy: 68, time: 42 },
    { day: 'Thu', accuracy: 85, time: 35 },
    { day: 'Fri', accuracy: 82, time: 40 },
    { day: 'Sat', accuracy: 78, time: 50 },
    { day: 'Sun', accuracy: 90, time: 28 }
  ];

  const subjectProgress = [
    { name: 'Quantitative Aptitude', mastery: 85, sessions: 12, lastStudied: '2 hours ago' },
    { name: 'Logical Reasoning', mastery: 72, sessions: 8, lastStudied: '1 day ago' },
    { name: 'Verbal Ability', mastery: 68, sessions: 10, lastStudied: '3 hours ago' },
    { name: 'Data Interpretation', mastery: 91, sessions: 7, lastStudied: '5 hours ago' }
  ];

  const weakAreas = [
    { topic: 'Profit and Loss', accuracy: 45, priority: 'High' },
    { topic: 'Blood Relations', accuracy: 52, priority: 'High' },
    { topic: 'Sentence Correction', accuracy: 61, priority: 'Medium' },
    { topic: 'Pie Charts', accuracy: 68, priority: 'Low' }
  ];

  const recentActivity = [
    { subject: 'Quantitative Aptitude', chapter: 'Percentages', score: 85, date: 'Today', correct: 17, total: 20 },
    { subject: 'Logical Reasoning', chapter: 'Syllogisms', score: 72, date: 'Yesterday', correct: 14, total: 20 },
    { subject: 'Verbal Ability', chapter: 'Reading Comprehension', score: 68, date: '2 days ago', correct: 13, total: 19 },
    { subject: 'Data Interpretation', chapter: 'Bar Charts', score: 94, date: '3 days ago', correct: 18, total: 19 }
  ];

  const studyInsights = [
    {
      icon: <Clock className="h-5 w-5 text-blue-500" />,
      title: 'Peak Study Time',
      value: '4:00 PM - 6:00 PM',
      description: 'Your highest accuracy period'
    },
    {
      icon: <Target className="h-5 w-5 text-green-500" />,
      title: 'Best Subject',
      value: 'Data Interpretation',
      description: '91% average accuracy'
    },
    {
      icon: <TrendingUp className="h-5 w-5 text-purple-500" />,
      title: 'Improvement Rate',
      value: '+12%',
      description: 'This month vs last month'
    },
    {
      icon: <Award className="h-5 w-5 text-orange-500" />,
      title: 'Achievement Level',
      value: 'Advanced',
      description: 'Top 15% of students'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-foreground">My Learning Dashboard</h2>
          <p className="text-muted-foreground">Personal insights and progress tracking</p>
        </div>
        <Badge variant="outline" className="px-4 py-2">
          <Calendar className="h-4 w-4 mr-2" />
          Last updated: Today
        </Badge>
      </div>

      {/* Personal Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary mb-1">{personalStats.totalSessions}</div>
            <div className="text-sm text-muted-foreground">Practice Sessions</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">{personalStats.averageAccuracy}%</div>
            <div className="text-sm text-muted-foreground">Average Accuracy</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">{personalStats.studyHours}h</div>
            <div className="text-sm text-muted-foreground">Study Hours</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">{personalStats.currentStreak}</div>
            <div className="text-sm text-muted-foreground">Day Streak</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Trend Chart */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Weekly Performance Trend
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={performanceTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="accuracy" 
                    stroke="#0088FE" 
                    fill="#0088FE" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Study Insights */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Personal Insights</h3>
            <div className="space-y-4">
              {studyInsights.map((insight, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-muted/30 rounded-lg">
                  {insight.icon}
                  <div>
                    <div className="font-medium text-foreground">{insight.title}</div>
                    <div className="text-lg font-bold text-primary">{insight.value}</div>
                    <div className="text-xs text-muted-foreground">{insight.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subject Progress */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              Subject Mastery
            </h3>
            <div className="space-y-4">
              {subjectProgress.map((subject, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{subject.name}</span>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{subject.mastery}%</Badge>
                      <span className="text-xs text-muted-foreground">{subject.sessions} sessions</span>
                    </div>
                  </div>
                  <Progress value={subject.mastery} className="h-2" />
                  <div className="text-xs text-muted-foreground">Last studied: {subject.lastStudied}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Areas to Improve */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Areas to Improve
            </h3>
            <div className="space-y-3">
              {weakAreas.map((area, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                  <div>
                    <div className="font-medium text-foreground">{area.topic}</div>
                    <div className="text-sm text-muted-foreground">{area.accuracy}% accuracy</div>
                  </div>
                  <Badge variant={
                    area.priority === 'High' ? 'destructive' : 
                    area.priority === 'Medium' ? 'default' : 'secondary'
                  }>
                    {area.priority}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <PieChart className="h-5 w-5 mr-2" />
            Recent Assessment History
          </h3>
          <div className="space-y-3">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-muted/20 rounded-lg hover:bg-muted/40 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    activity.score >= 80 ? 'bg-green-500' : 
                    activity.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <div className="font-medium text-foreground">{activity.subject}</div>
                    <div className="text-sm text-muted-foreground">{activity.chapter}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-right">
                  <div>
                    <div className="font-bold text-foreground">{activity.score}%</div>
                    <div className="text-xs text-muted-foreground">{activity.correct}/{activity.total}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">{activity.date}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Action Recommendations */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-primary flex items-center">
            <Target className="h-5 w-5 mr-2" />
            Personalized Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white rounded-lg border">
              <CheckCircle className="h-5 w-5 text-green-500 mb-2" />
              <div className="font-medium mb-2">Focus on Profit and Loss</div>
              <div className="text-sm text-muted-foreground mb-3">
                Your accuracy in profit and loss problems is 45%. Practice 20 more questions to improve.
              </div>
              <Button 
                size="sm" 
                className="w-full"
                onClick={handleStartProfitAndLossAssessment}
              >
                Start Practice
              </Button>
            </div>
            <div className="p-4 bg-white rounded-lg border">
              <TrendingUp className="h-5 w-5 text-blue-500 mb-2" />
              <div className="font-medium mb-2">Maintain Data Interpretation Excellence</div>
              <div className="text-sm text-muted-foreground mb-3">
                Great job! Keep up the 91% accuracy with regular practice sessions.
              </div>
              <Button size="sm" variant="outline" className="w-full">Continue</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}