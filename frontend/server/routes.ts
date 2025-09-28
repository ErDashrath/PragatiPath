import type { Express } from "express";
import { createServer, type Server } from "http";
import path from "path";
import { storage } from "./storage";
import { insertStudentProfileSchema, insertAssessmentSessionSchema } from "@shared/schema";

// Add proxy middleware for Django Core API and Simple API
const proxyToDjango = async (req: any, res: any, next: any) => {
  // Proxy /api/core/*, /simple/*, /history/*, /api/user, and /api/admin/* requests to Django backend
  if (req.path.startsWith('/api/core/') || req.path.startsWith('/simple/') || req.path.startsWith('/history/') || req.path === '/api/user' || req.path.startsWith('/api/admin/')) {
    try {
      // Map /api/user to /api/core/user for Django
      const djangoPath = req.path === '/api/user' ? '/api/core/user' : req.path;
      const backendUrl = `http://localhost:8000${djangoPath}`;
      console.log(`🔗 Proxying ${req.method} ${req.path} to ${backendUrl}`);
      
      // Forward cookies and headers for authentication
      const headers: any = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5000'
      };
      
      // Forward cookies for Django session
      if (req.headers.cookie) {
        console.log(`🍪 Forwarding cookies to Django: ${req.headers.cookie}`);
        headers['Cookie'] = req.headers.cookie;
      } else {
        console.log(`🍪 No cookies to forward to Django`);
      }
      
      const response = await fetch(backendUrl, {
        method: req.method,
        headers,
        body: req.method === 'GET' ? undefined : JSON.stringify(req.body),
        credentials: 'include'
      });
      
      // Forward ALL set-cookie headers back to client (Django sends multiple)
      // Parse raw set-cookie header which contains all cookies separated by commas
      const rawSetCookieHeader = response.headers.get('set-cookie');
      if (rawSetCookieHeader) {
        // Split on commas that are followed by a space and cookie name pattern
        // This handles multiple Set-Cookie values that fetch combines into one header
        const cookieHeaders = rawSetCookieHeader.split(/,\s*(?=[a-zA-Z]+=)/);
        console.log(`🍪 Forwarding ${cookieHeaders.length} cookies:`, cookieHeaders);
        res.setHeader('Set-Cookie', cookieHeaders);
      }
      
      const contentType = response.headers.get('content-type') || '';
      
      if (contentType.includes('application/json')) {
        const data = await response.json();
        res.status(response.status).json(data);
      } else {
        const text = await response.text();
        res.status(response.status).send(text);
      }
      
      return; // Don't call next() as we handled the request
    } catch (error) {
      console.error(`❌ Proxy error for ${req.path}:`, error);
      res.status(500).json({ detail: 'Server error. Please try again.' });
      return;
    }
  }
  
  next(); // Continue to other routes if not a proxied request
};

// Helper functions for mapping backend data to frontend format
function getIconForSubject(subjectCode: string): string {
  const iconMap: Record<string, string> = {
    'quantitative_aptitude': 'Calculator',
    'logical_reasoning': 'Puzzle', 
    'verbal_ability': 'BookOpen',
    'data_interpretation': 'BarChart3'
  };
  return iconMap[subjectCode] || 'BookOpen';
}

function getColorForSubject(subjectCode: string): string {
  const colorMap: Record<string, string> = {
    'quantitative_aptitude': 'hsl(221 83% 53%)',
    'logical_reasoning': 'hsl(178 78% 35%)',
    'verbal_ability': 'hsl(43 96% 56%)',
    'data_interpretation': 'hsl(142 76% 36%)'
  };
  return colorMap[subjectCode] || 'hsl(221 83% 53%)';
}

function getChaptersForSubject(subjectCode: string): Array<{id: number, title: string, status: string, progress: number}> {
  const chapterMap: Record<string, Array<{id: number, title: string, status: string, progress: number}>> = {
    'quantitative_aptitude': [
      { id: 1, title: "Percentages", status: "completed", progress: 100 },
      { id: 2, title: "Ratios and Proportions", status: "in-progress", progress: 65 },
      { id: 3, title: "Profit and Loss", status: "locked", progress: 0 }
    ],
    'logical_reasoning': [
      { id: 1, title: "Pattern Recognition", status: "completed", progress: 100 },
      { id: 2, title: "Syllogisms", status: "in-progress", progress: 45 },
      { id: 3, title: "Data Interpretation General", status: "locked", progress: 0 }
    ],
    'verbal_ability': [
      { id: 1, title: "Vocabulary", status: "completed", progress: 100 },
      { id: 2, title: "Grammar", status: "completed", progress: 100 },
      { id: 3, title: "Reading Comprehension", status: "in-progress", progress: 80 }
    ],
    'data_interpretation': [
      { id: 1, title: "Bar Charts", status: "completed", progress: 100 },
      { id: 2, title: "Line Graphs", status: "in-progress", progress: 61 },
      { id: 3, title: "Pie Charts", status: "locked", progress: 0 }
    ]
  };
  return chapterMap[subjectCode] || [];
}

function mapDifficultyToNumber(difficulty: string): number {
  const difficultyMap: Record<string, number> = {
    'very_easy': 1,
    'easy': 2,
    'moderate': 3,
    'difficult': 4
  };
  return difficultyMap[difficulty] || 3;
}

function getDescriptionForSubject(subjectCode: string): string {
  const descriptionMap: Record<string, string> = {
    'quantitative_aptitude': 'Mathematical problem solving and numerical reasoning',
    'logical_reasoning': 'Pattern recognition and logical thinking skills',
    'verbal_ability': 'Language comprehension and communication skills',
    'data_interpretation': 'Analysis and interpretation of charts, graphs, and tables'
  };
  return descriptionMap[subjectCode] || 'Study and practice questions';
}

export function registerRoutes(app: Express): Server {

  // Add Django Core API proxy middleware BEFORE other routes
  app.use(proxyToDjango);

  // Track current user in memory (for demo purposes)
  let currentUser: any = null;

  // Check current user session - DISABLED: Now proxied to Django
  // app.get("/api/user", (req, res) => {
  //   if (!currentUser) {
  //     return res.status(401).json({ message: "Not authenticated" });
  //   }
  //   res.json(currentUser);
  // });

  // Basic login endpoint
  app.post("/api/login", async (req, res) => {
    const { username, password } = req.body;
    const user = await storage.getUserByUsername(username);
    if (!user || user.password !== password) {
      return res.status(401).json({ message: "Invalid username or password" });
    }
    currentUser = { id: user.id, username: user.username, userType: user.userType, name: user.name };
    res.status(200).json(currentUser);
  });

  // Logout endpoint
  app.post("/api/logout", (req, res) => {
    currentUser = null;
    res.status(200).json({ message: "Logged out successfully" });
  });

  // Student profile endpoints
  app.get("/api/student-profile/:userId", async (req, res) => {
    try {
      const profile = await storage.getStudentProfile(req.params.userId);
      if (!profile) {
        return res.status(404).json({ message: "Student profile not found" });
      }
      res.json(profile);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch student profile" });
    }
  });

  app.post("/api/student-profile", async (req, res) => {
    try {
      const data = insertStudentProfileSchema.parse(req.body);
      const profile = await storage.createStudentProfile(data);
      res.status(201).json(profile);
    } catch (error) {
      res.status(400).json({ message: "Invalid student profile data" });
    }
  });

  app.put("/api/student-profile/:userId", async (req, res) => {
    try {
      const profile = await storage.updateStudentProfile(req.params.userId, req.body);
      res.json(profile);
    } catch (error) {
      res.status(500).json({ message: "Failed to update student profile" });
    }
  });

  // Module endpoints - Proxy to backend
  app.get("/api/modules", async (req, res) => {
    try {
      // Fetch from Django backend's new chapter-aware endpoint
      const response = await fetch('http://localhost:8000/api/assessment/subjects-with-chapters');
      if (!response.ok) {
        throw new Error(`Backend responded with ${response.status}`);
      }
      
      const backendData = await response.json();
      
      if (backendData.success && backendData.subjects) {
        // Transform backend data to frontend format
        const modules = backendData.subjects.map((subject: any) => ({
          id: subject.subject_code,
          title: subject.subject_name,
          description: getDescriptionForSubject(subject.subject_code),
          icon: getIconForSubject(subject.subject_code),
          color: getColorForSubject(subject.subject_code),
          chapters: subject.chapters.map((chapter: any, index: number) => ({
            id: chapter.id,
            title: chapter.name,
            status: index === 0 ? "completed" : index === 1 ? "in-progress" : "locked",
            progress: index === 0 ? 100 : index === 1 ? 65 : 0
          }))
        }));
        
        return res.json(modules);
      }
      
      throw new Error('Invalid backend response');
    } catch (error) {
      console.error('Error fetching modules from backend:', error);
      // Fallback to storage if backend is not available
      const modules = await storage.getModules();
      res.json(modules);
    }
  });

  app.get("/api/modules/:moduleId", async (req, res) => {
    try {
      const module = await storage.getModule(req.params.moduleId);
      if (!module) {
        return res.status(404).json({ message: "Module not found" });
      }
      res.json(module);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch module" });
    }
  });

  // Assessment endpoints - Proxy to backend with chapter-specific questions
  app.get("/api/assessment/questions/:moduleId/:chapterId", async (req, res) => {
    try {
      const { moduleId, chapterId } = req.params;
      const { difficulty = "moderate", count = "15" } = req.query;
      
      // Try to fetch chapter-specific questions from Django backend
      try {
        const response = await fetch('http://localhost:8000/api/assessment/chapter-questions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            student_id: currentUser?.id || 'demo-student',
            subject: moduleId,
            chapter_id: parseInt(chapterId),
            difficulty_level: difficulty === "3" ? "moderate" : difficulty, // Handle numeric difficulty
            count: parseInt(count as string)
          })
        });
        
        if (response.ok) {
          const backendData = await response.json();
          if (backendData.success && backendData.questions) {
            // Transform backend questions to frontend format
            const questions = backendData.questions.map((q: any) => ({
              id: q.id,
              moduleId: q.subject,
              chapterId: parseInt(chapterId),
              questionText: q.question_text,
              options: Array.isArray(q.options) ? q.options : Object.values(q.options || {}),
              correctAnswer: 0, // Backend doesn't expose correct answer for security
              difficulty: mapDifficultyToNumber(q.difficulty_level),
              fundamentalType: "application",
              questionType: q.question_type || "multiple-choice"
            }));
            
            console.log(`✅ Loaded ${questions.length} questions for ${moduleId} chapter ${chapterId}`);
            return res.json(questions);
          }
        } else {
          console.warn(`Backend responded with status ${response.status}`);
        }
      } catch (backendError) {
        console.warn('Backend not available, falling back to mock data:', backendError);
      }
      
      // Fallback to mock storage
      const questions = await storage.getAssessmentQuestions(
        moduleId, 
        parseInt(chapterId), 
        3, // Default difficulty as number
        parseInt(count as string)
      );
      res.json(questions);
    } catch (error) {
      console.error('Error in questions endpoint:', error);
      res.status(500).json({ message: "Failed to fetch assessment questions" });
    }
  });

  app.post("/api/assessment/session", async (req, res) => {
    try {
      const data = insertAssessmentSessionSchema.parse(req.body);
      const session = await storage.createAssessmentSession(data);
      res.status(201).json(session);
    } catch (error) {
      res.status(400).json({ message: "Invalid assessment session data" });
    }
  });

  app.put("/api/assessment/session/:sessionId", async (req, res) => {
    try {
      const session = await storage.updateAssessmentSession(req.params.sessionId, req.body);
      res.json(session);
    } catch (error) {
      res.status(500).json({ message: "Failed to update assessment session" });
    }
  });

  // Admin endpoints - Now proxied to Django backend
  // app.get("/api/admin/students", async (req, res) => {
  //   try {
  //     const students = await storage.getAllStudentProfiles();
  //     res.json(students);
  //   } catch (error) {
  //     res.status(500).json({ message: "Failed to fetch students" });
  //   }
  // });

  // app.get("/api/admin/class-overview", async (req, res) => {
  //   try {
  //     const overview = await storage.getClassOverview();
  //     res.json(overview);
  //   } catch (error) {
  //     res.status(500).json({ message: "Failed to fetch class overview" });
  //   }
  // });

  // Test route for auth testing
  app.get("/auth-test", (req, res) => {
    res.sendFile(path.resolve(import.meta.dirname, "..", "public", "auth-test.html"));
  });

  const httpServer = createServer(app);
  return httpServer;
}
