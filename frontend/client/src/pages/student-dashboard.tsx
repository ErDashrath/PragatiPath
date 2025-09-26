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
import ReportsView from "@/components/student/enhanced-reports-view";
import { AssessmentHistory } from "@/components/student/assessment-history";
import { DetailedResultView } from "@/components/student/detailed-result-view";
import AdaptiveLearningInterface from "@/components/student/adaptive-learning-interface";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { type Subject, type Chapter, type AssessmentResult } from "@/lib/assessment-api";

type StudentView = 'dashboard' | 'modules' | 'chapter' | 'assessment' | 'practice' | 'reports' | 'history' | 'historyDetail' | 'adaptive';

export default function StudentDashboard() {
  const [, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();
  const [currentView, setCurrentView] = useState<StudentView>('dashboard');
  const [selectedSubjectCode, setSelectedSubjectCode] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<Chapter | null>(null);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<string | null>(null);

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

  const handleChapterSelect = (chapter: Chapter, subject: Subject) => {
    setSelectedChapter(chapter);
    setSelectedSubject(subject);
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

  const navigationItems = [
    { key: 'dashboard', label: 'Dashboard', active: currentView === 'dashboard' },
    { key: 'adaptive', label: 'Adaptive Learning 🧠', active: currentView === 'adaptive' },
    { key: 'modules', label: 'Modules', active: currentView === 'modules' || currentView === 'chapter' },
    { key: 'practice', label: 'Practice', active: currentView === 'practice' },
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
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-primary-foreground" />
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
              
              <div className="flex items-center space-x-2">
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
          />
        )}
        {currentView === 'practice' && <PracticeView />}
        {currentView === 'history' && (
          <AssessmentHistory 
            studentUsername={user?.username || ''}
            onViewDetails={handleViewAssessmentDetails}
          />
        )}
        {currentView === 'historyDetail' && selectedAssessmentId && (
          <DetailedResultView 
            sessionId={selectedAssessmentId}
            studentUsername={user?.username || ''}
            onBack={() => setCurrentView('history')}
          />
        )}
        {currentView === 'reports' && <ReportsView />}
      </main>
    </div>
  );
}