import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { GraduationCap, LogOut, Menu } from "lucide-react";
import AdminOverview from "@/components/admin/admin-overview";
import StudentsList from "@/components/admin/students-list";
import EnhancedReportsView from "@/components/admin/enhanced-reports-view";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

type AdminView = 'overview' | 'students' | 'analytics' | 'reports';

export default function AdminDashboard() {
  const [, navigate] = useLocation();
  const { user, logoutMutation } = useAuth();
  const [currentView, setCurrentView] = useState<AdminView>('overview');

  useEffect(() => {
    if (user?.userType !== 'admin') {
      navigate('/auth');
    }
  }, [user, navigate]);

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const navigationItems = [
    { key: 'overview', label: 'Overview', active: currentView === 'overview' },
    { key: 'students', label: 'Students', active: currentView === 'students' },
    { key: 'analytics', label: 'Analytics', active: currentView === 'analytics' },
    { key: 'reports', label: 'Reports', active: currentView === 'reports' },
  ];

  const NavigationContent = () => (
    <>
      {navigationItems.map((item) => (
        <button
          key={item.key}
          onClick={() => setCurrentView(item.key as AdminView)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            item.active
              ? 'text-secondary border-b-2 border-secondary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
          data-testid={`admin-nav-${item.key}`}
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
              <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-secondary-foreground" />
              </div>
              <h1 className="text-xl font-bold text-foreground">PragatiPath Admin</h1>
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
                    <Button variant="ghost" size="sm" data-testid="admin-mobile-menu-trigger">
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
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                disabled={logoutMutation.isPending}
                data-testid="admin-button-logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'overview' && <AdminOverview />}
        {currentView === 'students' && <StudentsList />}
        {currentView === 'analytics' && (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-foreground mb-4">Analytics Dashboard</h2>
            <p className="text-muted-foreground">Advanced analytics and insights coming soon...</p>
          </div>
        )}
        {currentView === 'reports' && <EnhancedReportsView />}
      </main>
    </div>
  );
}
