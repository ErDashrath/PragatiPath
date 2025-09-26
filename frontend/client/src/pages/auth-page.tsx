import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GraduationCap } from "lucide-react";


export default function AuthPage() {
  const [, navigate] = useLocation();
  const { user, loginMutation } = useAuth();
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [loginForm, setLoginForm] = useState({ username: "", password: "", userType: "student" });
  const [registerForm, setRegisterForm] = useState({ 
    username: "", 
    password: "", 
    confirmPassword: "", 
    name: "", 
    email: "", 
    userType: "student" 
  });
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);
  const [registerSuccess, setRegisterSuccess] = useState<string | null>(null);
  useEffect(() => {
    if (user) {
      if (user.userType === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    }
  }, [user, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate(loginForm);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterLoading(true);
    setRegisterError(null);
    setRegisterSuccess(null);
    
    // Client-side validation
    if (registerForm.password !== registerForm.confirmPassword) {
      setRegisterError("Passwords do not match");
      setRegisterLoading(false);
      return;
    }
    
    if (registerForm.password.length < 8) {
      setRegisterError("Password must be at least 8 characters long");
      setRegisterLoading(false);
      return;
    }
    
    try {
      // Register user with proper endpoint - try proxy first, fallback to direct
      const registerUrl = "/api/core/register"; // Will use Vite proxy if available
      const res = await fetch(registerUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: registerForm.username,
          password: registerForm.password,
          confirm_password: registerForm.confirmPassword,
          email: registerForm.email,
          full_name: registerForm.name
        }),
      });

      // Check content type before parsing
      const contentType = res.headers.get("content-type");
      let data;
      
      if (contentType && contentType.includes("application/json")) {
        data = await res.json();
      } else {
        // If not JSON, it's likely an HTML error page
        const text = await res.text();
        if (text.includes('DOCTYPE')) {
          throw new Error('Server error. Please try again.');
        }
        throw new Error(text || 'Registration failed. Please try again.');
      }

      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed. Please try again.');
      }

      // Registration successful - show success message and auto-login
      setRegisterSuccess("Registration successful! Logging you in...");
      
      // Auto login with same credentials
      setTimeout(() => {
        loginMutation.mutate({ 
          username: registerForm.username,
          password: registerForm.password
        });
      }, 1000);
      
      // Clear the form
      setRegisterForm({ username: "", password: "", confirmPassword: "", name: "", email: "", userType: "student" });

    } catch (err: any) {
      setRegisterError(err.message || "Registration failed");
      setTab('register'); // Stay on register tab on error
    } finally {
      setRegisterLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
        
        {/* Hero Section */}
        <div className="flex flex-col justify-center space-y-6">
          <div className="text-center space-y-6">
            <div className="space-y-2">
              <div className="mx-auto h-12 w-12 bg-primary rounded-lg"></div>
            </div>
            <h1 className="text-5xl font-bold text-foreground mb-4">PragatiPath</h1>
            <p className="text-xl text-muted-foreground max-w-md">
              Your AI-powered adaptive learning companion
            </p>
          </div>
        </div>

        {/* Authentication Form with Tabs */}
        <div className="flex items-center justify-center">
          <Card className="w-full max-w-md shadow-xl border-border">
            <CardContent className="p-8 space-y-4">
              <div className="flex justify-center mb-6">
                <button
                  className={`px-4 py-2 font-semibold rounded-t-md border-b-2 transition-colors duration-150 ${tab === 'login' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setTab('login')}
                  type="button"
                >
                  Login
                </button>
                <button
                  className={`px-4 py-2 font-semibold rounded-t-md border-b-2 transition-colors duration-150 ${tab === 'register' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground'}`}
                  onClick={() => setTab('register')}
                  type="button"
                >
                  Register
                </button>
              </div>

              {tab === 'login' && (
                <>
                  <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-foreground">Welcome Back</h2>
                    <p className="text-muted-foreground">Sign in to continue your learning journey</p>
                  </div>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="login-username">Username</Label>
                      <Input
                        id="login-username"
                        type="text"
                        value={loginForm.username}
                        onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                        placeholder="Enter your username"
                        required
                        data-testid="input-login-username"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="login-password">Password</Label>
                      <Input
                        id="login-password"
                        type="password"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                        placeholder="Enter your password"
                        required
                        data-testid="input-login-password"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="login-user-type">Account Type</Label>
                      <select
                        id="login-user-type"
                        value={loginForm.userType}
                        onChange={(e) => setLoginForm({ ...loginForm, userType: e.target.value })}
                        className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                        data-testid="select-login-user-type"
                      >
                        <option value="student">Student</option>
                        <option value="admin">Admin (Teacher/Parent)</option>
                      </select>
                    </div>
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={loginMutation.isPending}
                      data-testid="button-login-submit"
                    >
                      {loginMutation.isPending ? "Signing in..." : "Sign In"}
                    </Button>
                  </form>
                  <div className="text-center text-sm text-muted-foreground space-y-2">
                    <p>Demo Credentials:</p>
                    <p>Student: student / password</p>
                    <p>Admin: admin / password</p>
                  </div>
                </>
              )}

              {tab === 'register' && (
                <>
                  <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-foreground">Create Account</h2>
                    <p className="text-muted-foreground">Register to start your adaptive learning journey</p>
                  </div>
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="register-username">Username</Label>
                      <Input
                        id="register-username"
                        type="text"
                        value={registerForm.username}
                        onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                        placeholder="Choose a username"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-password">Password</Label>
                      <Input
                        id="register-password"
                        type="password"
                        value={registerForm.password}
                        onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                        placeholder="Create a password"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-confirm-password">Confirm Password</Label>
                      <Input
                        id="register-confirm-password"
                        type="password"
                        value={registerForm.confirmPassword}
                        onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                        placeholder="Confirm your password"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-name">Full Name</Label>
                      <Input
                        id="register-name"
                        type="text"
                        value={registerForm.name}
                        onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                        placeholder="Your full name"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-email">Email</Label>
                      <Input
                        id="register-email"
                        type="email"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                        placeholder="Your email address"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="register-user-type">Account Type</Label>
                      <select
                        id="register-user-type"
                        value={registerForm.userType}
                        onChange={(e) => setRegisterForm({ ...registerForm, userType: e.target.value })}
                        className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                      >
                        <option value="student">Student</option>
                        <option value="admin">Admin (Teacher/Parent)</option>
                      </select>
                    </div>
                    <Button
                      type="submit"
                      className="w-full"
                      disabled={registerLoading}
                    >
                      {registerLoading ? "Registering..." : "Register"}
                    </Button>
                  </form>
                  {registerError && <div className="text-red-500 text-center text-sm mt-2">{registerError}</div>}
                  {registerSuccess && <div className="text-green-600 text-center text-sm mt-2">{registerSuccess}</div>}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
