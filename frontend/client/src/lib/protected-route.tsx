import { useAuth } from "@/hooks/use-auth";
import { Loader2 } from "lucide-react";
import { Redirect, Route } from "wouter";

export function ProtectedRoute({
  path,
  component: Component,
  requireUserType,
}: {
  path: string;
  component: () => React.JSX.Element;
  requireUserType?: 'student' | 'admin';
}) {
  const { user, isLoading } = useAuth();

  // For demo purposes - allow admin dashboard access without authentication
  if (path === '/admin') {
    console.log('🔓 Admin route - bypassing authentication for demo');
    return <Route path={path} component={Component} />;
  }

  if (isLoading) {
    return (
      <Route path={path}>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-border" />
        </div>
      </Route>
    );
  }

  if (!user) {
    return (
      <Route path={path}>
        <Redirect to="/auth" />
      </Route>
    );
  }

  // Check user type if specified
  if (requireUserType && user.userType !== requireUserType) {
    return (
      <Route path={path}>
        <Redirect to={user.userType === 'admin' ? '/admin' : '/student'} />
      </Route>
    );
  }

  return <Route path={path} component={Component} />;
}
