import { type User, type InsertUser, type StudentProfile, type InsertStudentProfile, type Module, type AssessmentQuestion, type AssessmentSession, type InsertAssessmentSession } from "@shared/schema";
import { randomUUID } from "crypto";
export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getStudentProfile(userId: string): Promise<StudentProfile | undefined>;
  createStudentProfile(profile: InsertStudentProfile): Promise<StudentProfile>;
  updateStudentProfile(userId: string, updates: Partial<StudentProfile>): Promise<StudentProfile>;
  getAllStudentProfiles(): Promise<StudentProfile[]>;
  getModules(): Promise<Module[]>;
  getModule(moduleId: string): Promise<Module | undefined>;
  getAssessmentQuestions(moduleId: string, chapterId: number, difficulty: number, count: number): Promise<AssessmentQuestion[]>;
  createAssessmentSession(session: InsertAssessmentSession): Promise<AssessmentSession>;
  updateAssessmentSession(sessionId: string, updates: Partial<AssessmentSession>): Promise<AssessmentSession>;
  getClassOverview(): Promise<any>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private studentProfiles: Map<string, StudentProfile>;
  private modules: Map<string, Module>;
  private assessmentQuestions: Map<string, AssessmentQuestion[]>;
  private assessmentSessions: Map<string, AssessmentSession>;

  constructor() {
    this.users = new Map();
    this.studentProfiles = new Map();
    this.modules = new Map();
    this.assessmentQuestions = new Map();
    this.assessmentSessions = new Map();
    this.initializeData();
    this.initializeDemoUsers();
  }

  private initializeData() {
    // Initialize modules
    const modules: Module[] = [
      {
        id: "quantitative_aptitude",
        title: "Quantitative Aptitude",
        description: "Mathematical problem solving and numerical reasoning",
        icon: "Calculator",
        color: "hsl(221 83% 53%)",
        chapters: [
          { id: 1, title: "Percentages", status: "completed", progress: 100 },
          { id: 2, title: "Ratios and Proportions", status: "in-progress", progress: 65 },
          { id: 3, title: "Profit and Loss", status: "locked", progress: 0 }
        ]
      },
      {
        id: "logical_reasoning",
        title: "Logical Reasoning",
        description: "Pattern recognition and logical thinking skills",
        icon: "Puzzle",
        color: "hsl(178 78% 35%)",
        chapters: [
          { id: 1, title: "Pattern Recognition", status: "completed", progress: 100 },
          { id: 2, title: "Syllogisms", status: "in-progress", progress: 45 },
          { id: 3, title: "Data Interpretation General", status: "locked", progress: 0 }
        ]
      },
      {
        id: "verbal_ability",
        title: "Verbal Ability & Reading Comprehension",
        description: "Language comprehension and communication skills",
        icon: "BookOpen",
        color: "hsl(43 96% 56%)",
        chapters: [
          { id: 1, title: "Vocabulary", status: "completed", progress: 100 },
          { id: 2, title: "Grammar", status: "completed", progress: 100 },
          { id: 3, title: "Reading Comprehension", status: "in-progress", progress: 80 }
        ]
      },
      {
        id: "data_interpretation",
        title: "Data Interpretation",
        description: "Analysis and interpretation of charts, graphs, and tables",
        icon: "BarChart3",
        color: "hsl(142 76% 36%)",
        chapters: [
          { id: 1, title: "Bar Charts", status: "completed", progress: 100 },
          { id: 2, title: "Line Graphs", status: "in-progress", progress: 61 },
          { id: 3, title: "Pie Charts", status: "locked", progress: 0 }
        ]
      }
    ];

    modules.forEach(module => this.modules.set(module.id, module));

    // Initialize sample assessment questions
    const sampleQuestions: AssessmentQuestion[] = [
      {
        id: randomUUID(),
        moduleId: "quantitative_aptitude",
        chapterId: 1,
        questionText: "A shopkeeper marks his goods 40% above the cost price and gives a discount of 15%. What is his profit percentage?",
        options: ["19%", "21%", "25%", "19%"],
        correctAnswer: 0,
        difficulty: 3,
        fundamentalType: "application",
        questionType: "multiple-choice"
      },
      {
        id: randomUUID(),
        moduleId: "logical_reasoning",
        chapterId: 1,
        questionText: "In a series: 2, 6, 18, 54, ?, what is the next number?",
        options: ["108", "162", "216", "324"],
        correctAnswer: 1,
        difficulty: 2,
        fundamentalType: "grasping",
        questionType: "multiple-choice"
      },
      {
        id: randomUUID(),
        moduleId: "verbal_ability",
        chapterId: 1,
        questionText: "Choose the word that is most similar in meaning to 'METICULOUS':",
        options: ["Careless", "Careful", "Lazy", "Quick"],
        correctAnswer: 1,
        difficulty: 2,
        fundamentalType: "retention",
        questionType: "multiple-choice"
      },
      {
        id: randomUUID(),
        moduleId: "data_interpretation",
        chapterId: 1,
        questionText: "Based on the bar chart showing sales data, which quarter had the highest sales?",
        options: ["Q1", "Q2", "Q3", "Q4"],
        correctAnswer: 2,
        difficulty: 2,
        fundamentalType: "application",
        questionType: "multiple-choice"
      }
    ];

    this.assessmentQuestions.set("all", sampleQuestions);
  }

  private async initializeDemoUsers() {

    // Create demo student user (plain password for basic login)
    const studentUser: User = {
      id: randomUUID(),
      username: "student",
      password: "password",
      userType: "student",
      name: "Demo Student"
    };
    this.users.set(studentUser.id, studentUser);

    // Create demo admin user (plain password for basic login)
    const adminUser: User = {
      id: randomUUID(),
      username: "admin", 
      password: "password",
      userType: "admin",
      name: "Demo Admin"
    };
    this.users.set(adminUser.id, adminUser);

    // Create student profile for demo student
    const studentProfile: StudentProfile = {
      id: randomUUID(),
      userId: studentUser.id,
      listeningScore: 65,
      graspingScore: 72,
      retentionScore: 58,
      applicationScore: 81,
      moduleProgress: {
        quantitative_aptitude: 68,
        logical_reasoning: 52,
        verbal_ability: 74,
        data_interpretation: 61
      },
      chapterProgress: {},
      learningGaps: [],
      assessmentHistory: [],
      practiceHistory: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.studentProfiles.set(studentProfile.id, studentProfile);
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { 
      ...insertUser, 
      id,
      userType: insertUser.userType || 'student',
    };
    this.users.set(id, user);

    // Create default student profile if user is a student
    if (insertUser.userType === 'student') {
      await this.createStudentProfile({
        userId: id,
        listeningScore: Math.floor(Math.random() * 40) + 40, // 40-80
        graspingScore: Math.floor(Math.random() * 40) + 50, // 50-90
        retentionScore: Math.floor(Math.random() * 30) + 40, // 40-70
        applicationScore: Math.floor(Math.random() * 30) + 60, // 60-90
        moduleProgress: {
          quantitative_aptitude: Math.floor(Math.random() * 30) + 50,
          logical_reasoning: Math.floor(Math.random() * 30) + 40,
          verbal_ability: Math.floor(Math.random() * 30) + 60,
          data_interpretation: Math.floor(Math.random() * 30) + 50
        },
        chapterProgress: {},
        learningGaps: [],
        assessmentHistory: [],
        practiceHistory: []
      });
    }

    return user;
  }

  async getStudentProfile(userId: string): Promise<StudentProfile | undefined> {
    return Array.from(this.studentProfiles.values()).find(
      profile => profile.userId === userId
    );
  }

  async createStudentProfile(profile: InsertStudentProfile): Promise<StudentProfile> {
    const id = randomUUID();
    const newProfile: StudentProfile = {
      ...profile,
      id,
      listeningScore: profile.listeningScore ?? null,
      graspingScore: profile.graspingScore ?? null,
      retentionScore: profile.retentionScore ?? null,
      applicationScore: profile.applicationScore ?? null,
      moduleProgress: profile.moduleProgress ?? {},
      chapterProgress: profile.chapterProgress ?? {},
      learningGaps: profile.learningGaps ?? [],
      assessmentHistory: profile.assessmentHistory ?? [],
      practiceHistory: profile.practiceHistory ?? [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.studentProfiles.set(id, newProfile);
    return newProfile;
  }

  async updateStudentProfile(userId: string, updates: Partial<StudentProfile>): Promise<StudentProfile> {
    const existing = await this.getStudentProfile(userId);
    if (!existing) {
      throw new Error("Student profile not found");
    }
    
    const updated = {
      ...existing,
      ...updates,
      updatedAt: new Date()
    };
    
    this.studentProfiles.set(existing.id, updated);
    return updated;
  }

  async getAllStudentProfiles(): Promise<StudentProfile[]> {
    return Array.from(this.studentProfiles.values());
  }

  async getModules(): Promise<Module[]> {
    return Array.from(this.modules.values());
  }

  async getModule(moduleId: string): Promise<Module | undefined> {
    return this.modules.get(moduleId);
  }

  async getAssessmentQuestions(
    moduleId: string, 
    chapterId: number, 
    difficulty: number, 
    count: number
  ): Promise<AssessmentQuestion[]> {
    const allQuestions = this.assessmentQuestions.get("all") || [];
    
    // Filter questions by module and chapter
    let filtered = allQuestions.filter(q => 
      q.moduleId === moduleId && 
      (!chapterId || q.chapterId === chapterId)
    );

    // If not enough questions, generate more or repeat existing ones
    while (filtered.length < count) {
      filtered = [...filtered, ...filtered];
    }

    return filtered.slice(0, count);
  }

  async createAssessmentSession(sessionData: InsertAssessmentSession): Promise<AssessmentSession> {
    const id = randomUUID();
    const session: AssessmentSession = {
      ...sessionData,
      id,
      userId: sessionData.userId ?? null,
      moduleId: sessionData.moduleId ?? null,
      chapterId: sessionData.chapterId ?? null,
      totalQuestions: sessionData.totalQuestions ?? null,
      correctAnswers: sessionData.correctAnswers ?? null,
      finalDifficulty: sessionData.finalDifficulty ?? null,
      startTime: new Date(),
      endTime: null,
      responses: sessionData.responses ?? [],
      isCompleted: false
    };
    this.assessmentSessions.set(id, session);
    return session;
  }

  async updateAssessmentSession(sessionId: string, updates: Partial<AssessmentSession>): Promise<AssessmentSession> {
    const existing = this.assessmentSessions.get(sessionId);
    if (!existing) {
      throw new Error("Assessment session not found");
    }
    
    const updated = {
      ...existing,
      ...updates
    };
    
    this.assessmentSessions.set(sessionId, updated);
    return updated;
  }

  async getClassOverview(): Promise<any> {
    const profiles = await this.getAllStudentProfiles();
    
    return {
      totalStudents: profiles.length,
      activeThisWeek: Math.floor(profiles.length * 0.9),
      averageProgress: Math.floor(profiles.reduce((acc, p) => {
        const moduleProgress = p.moduleProgress as any;
        const avg = (moduleProgress.quantitative_aptitude + moduleProgress.logical_reasoning + moduleProgress.verbal_ability + (moduleProgress.data_interpretation || 0)) / 4;
        return acc + avg;
      }, 0) / profiles.length),
      needingAttention: profiles.filter(p => {
        const fundamentalScores = [p.listeningScore, p.graspingScore, p.retentionScore, p.applicationScore];
        return fundamentalScores.some(score => (score || 50) < 60);
      }).length,
      gapDistribution: {
        listening: Math.floor(profiles.reduce((acc, p) => acc + (p.listeningScore || 50), 0) / profiles.length),
        grasping: Math.floor(profiles.reduce((acc, p) => acc + (p.graspingScore || 50), 0) / profiles.length),
        retention: Math.floor(profiles.reduce((acc, p) => acc + (p.retentionScore || 50), 0) / profiles.length),
        application: Math.floor(profiles.reduce((acc, p) => acc + (p.applicationScore || 50), 0) / profiles.length),
      }
    };
  }
}

export const storage = new MemStorage();
