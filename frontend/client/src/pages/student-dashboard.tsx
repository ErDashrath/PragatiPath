import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { GraduationCap, User, Menu, LogOut } from "lucide-react";
import DashboardOverview from "@/components/student/dashboard-overview";
import ModulesView from "@/components/student/modules-view";
import ChapterView from "@/components/student/chapter-view";
import AssessmentInterface from "@/components/student/assessment-interface-new";
import PracticeView from "@/components/student/practice-view";
import ReportsView from "@/components/student/personal-reports-view";
import { AssessmentHistory } from "@/components/student/assessment-history";
import { DetailedResultView } from "@/components/student/detailed-result-view";
import AdaptiveLearningInterface from "@/components/student/adaptive-learning-interface";
import ScheduledExamsView from "@/components/student/scheduled-exams-view";
import EnhancedExamInterface from "@/components/student/EnhancedExamInterface";
import DynamicExamInterface from "@/components/student/dynamic-exam-interface";
import EnhancedExamSelector from "@/components/student/enhanced-exam-selector";
import ExamDebugComponent from "@/components/debug/exam-debug";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { type Subject, type Chapter, type AssessmentResult } from "@/lib/assessment-api";

type StudentView = 'dashboard' | 'modules' | 'chapter' | 'assessment' | 'practice' | 'reports' | 'history' | 'historyDetail' | 'adaptive' | 'exams' | 'timedExam' | 'debug' | 'enhancedExams' | 'dynamicExam';

interface AssessmentConfig {
  questionCount: number;
  timeLimit: number;
}

export default function StudentDashboard() {
  const [, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();
  const [currentView, setCurrentView] = useState<StudentView>('dashboard');
  const [selectedSubjectCode, setSelectedSubjectCode] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<string | null>(null);
  const [assessmentConfig, setAssessmentConfig] = useState<AssessmentConfig>({ questionCount: 10, timeLimit: 15 });
  // Enhanced exam state
  const [currentDynamicExam, setCurrentDynamicExam] = useState<{
    type: 'adaptive_subject' | 'practice_chapter' | 'scheduled_exam';
    id: string;
    name: string;
  } | null>(null);
  const [currentExamSessionId, setCurrentExamSessionId] = useState<string | null>(null);
  const [currentExamName, setCurrentExamName] = useState<string>('');

  useEffect(() => {
    if (user?.userType === 'admin') {
      navigate('/admin');
    }
  }, [user, navigate]);

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const handleViewChange = (view: StudentView) => {
    setCurrentView(view);
    if (view !== 'chapter' && view !== 'assessment' && view !== 'historyDetail') {
      setSelectedSubject(null);
      setSelectedChapter(null);
      setAssessmentResult(null);
      setSelectedAssessmentId(null);
    }
  };

  const handleModuleSelect = (subjectCode: string) => {
    setSelectedSubjectCode(subjectCode);
    setCurrentView('chapter');
  };

  const handleChapterSelect = (chapter: Chapter, subject: Subject, config?: AssessmentConfig) => {
    setSelectedChapter(chapter);
    setSelectedSubject(subject);
    if (config) {
      setAssessmentConfig(config);
    }
    setCurrentView('assessment');
  };

  const handleAssessmentComplete = (result: AssessmentResult) => {
    setAssessmentResult(result);
    // Could navigate to results view or stay in assessment view
  };

  const handleViewAssessmentDetails = (assessmentId: string) => {
    setSelectedAssessmentId(assessmentId);
    setCurrentView('historyDetail');
  };

  const handleStartExam = (examSessionId: string, examName: string) => {
    setCurrentExamSessionId(examSessionId);
    setCurrentExamName(examName);
    setCurrentView('timedExam');
  };

  // Enhanced exam handlers
  const handleStartDynamicExam = (
    examType: 'adaptive_subject' | 'practice_chapter' | 'scheduled_exam',
    examId: string,
    examName: string
  ) => {
    setCurrentDynamicExam({ type: examType, id: examId, name: examName });
    setCurrentView('dynamicExam');
  };

  const handleDynamicExamComplete = (results: any) => {
    console.log('Dynamic exam completed:', results);
    // Store results, show completion screen, etc.
    setCurrentView('enhancedExams');
    setCurrentDynamicExam(null);
  };

  const handleDynamicExamExit = () => {
    setCurrentView('enhancedExams');
    setCurrentDynamicExam(null);
  };

  const handleExamComplete = (sessionId: string, results: any) => {
    // Handle exam completion - could show results or redirect
    console.log('Exam completed:', sessionId, results);
    setCurrentView('exams'); // Return to exam list
    setCurrentExamSessionId(null);
    setCurrentExamName('');
  };

  const handleExamExit = () => {
    // Handle exam exit
    setCurrentView('exams');
    setCurrentExamSessionId(null);
    setCurrentExamName('');
  };

  const navigationItems = [
    { key: 'dashboard', label: 'Dashboard', active: currentView === 'dashboard' },
    { key: 'enhancedExams', label: '🚀 Enhanced Exams', active: currentView === 'enhancedExams' || currentView === 'dynamicExam' },
    { key: 'exams', label: 'Scheduled Exams ⏰', active: currentView === 'exams' || currentView === 'timedExam' },
    { key: 'debug', label: '🧪 Exam Debug', active: currentView === 'debug' },
    { key: 'adaptive', label: 'Adaptive Learning 🧠', active: currentView === 'adaptive' },
    { key: 'modules', label: 'Modules', active: currentView === 'modules' || currentView === 'chapter' },
    { key: 'history', label: 'History', active: currentView === 'history' },
    { key: 'reports', label: 'Reports', active: currentView === 'reports' },
  ];

  const NavigationContent = () => (
    <>
      {navigationItems.map((item) => (
        <button
          key={item.key}
          onClick={() => handleViewChange(item.key as StudentView)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            item.active
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
          data-testid={`nav-${item.key}`}
        >
          {item.label}
        </button>
      ))}
    </>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="h-8 w-8 rounded-full overflow-hidden">
                <img 
                  src="/logo.png" 
                  alt="PragatiPath Logo" 
                  className="w-full h-full object-cover"
                />
              </div>
              <h1 className="text-xl font-bold text-foreground">PragatiPath</h1>
            </div>
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              <NavigationContent />
            </nav>
            
            <div className="flex items-center space-x-4">
              <span className="hidden sm:block text-sm text-muted-foreground">
                {user?.name}
              </span>
              
              {/* Mobile Navigation */}
              <div className="md:hidden">
                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="ghost" size="sm" data-testid="mobile-menu-trigger">
                      <Menu className="h-5 w-5" />
                    </Button>
                  </SheetTrigger>
                  <SheetContent side="right" className="w-64">
                    <div className="flex flex-col space-y-4 mt-8">
                      <NavigationContent />
                    </div>
                  </SheetContent>
                </Sheet>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Quick Admin Switch for Demo */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/admin')}
                  className="bg-blue-50 hover:bg-blue-100 border-blue-300"
                >
                  🔐 Admin View
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  data-testid="button-user-info"
                >
                  <User className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  disabled={logoutMutation.isPending}
                  data-testid="button-logout"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' && <DashboardOverview onNavigate={setCurrentView} />}
        {currentView === 'adaptive' && <AdaptiveLearningInterface />}
        {currentView === 'modules' && (
          <ModulesView onModuleSelect={handleModuleSelect} />
        )}
        {currentView === 'chapter' && selectedSubjectCode && (
          <ChapterView 
            subjectCode={selectedSubjectCode}
            onBackToModules={() => setCurrentView('modules')}
            onChapterSelect={handleChapterSelect}
          />
        )}
        {currentView === 'assessment' && selectedChapter && selectedSubject && (
          <AssessmentInterface 
            subject={selectedSubject}
            chapter={selectedChapter}
            onComplete={handleAssessmentComplete}
            onBack={() => setCurrentView('chapter')}
            config={assessmentConfig}
          />
        )}
        {currentView === 'practice' && <PracticeView />}
        {currentView === 'history' && (
          <AssessmentHistory 
            studentUsername={user?.username || ''}
            onViewDetails={handleViewAssessmentDetails}
            backendUserId={user?.id ? Number(user.id) : undefined}
          />
        )}
        {currentView === 'historyDetail' && selectedAssessmentId && (
          <DetailedResultView 
            sessionId={selectedAssessmentId}
            studentUsername={user?.username || ''}
            onBack={() => setCurrentView('history')}
          />
        )}
        {currentView === 'exams' && (
          <ScheduledExamsView onStartExam={handleStartExam} />
        )}
        {currentView === 'debug' && (
          <ExamDebugComponent />
        )}
        {currentView === 'enhancedExams' && (
          <EnhancedExamSelector 
            onStartExam={handleStartDynamicExam}
            onViewScheduled={() => setCurrentView('exams')}
          />
        )}
        {currentView === 'dynamicExam' && currentDynamicExam && (
          <DynamicExamInterface
            examType={currentDynamicExam.type}
            examId={currentDynamicExam.id}
            onExamComplete={handleDynamicExamComplete}
            onExamExit={handleDynamicExamExit}
          />
        )}
        {currentView === 'timedExam' && (
          <EnhancedExamInterface />
        )}
        {currentView === 'reports' && (
          <ReportsView 
            onNavigateToModule={(subjectCode: string) => {
              setSelectedSubjectCode(subjectCode);
              setCurrentView('modules');
            }}
            onNavigateToChapter={(subjectCode: string) => {
              setSelectedSubjectCode(subjectCode);
              setCurrentView('chapter');
            }}
            onChapterSelect={handleChapterSelect}
          />
        )}
      </main>
    </div>
  );
}