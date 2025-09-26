// Mock data for demonstration purposes - replace with real API calls in production

export const mockStudentProfile = {
  id: "student-1",
  userId: "user-123",
  listeningScore: 65,
  graspingScore: 72,
  retentionScore: 58,
  applicationScore: 81,
  moduleProgress: {
    quantitative: 68,
    logical: 52,
    verbal: 74
  },
  chapterProgress: {
    quantitative: {
      1: 100, // Percentages
      2: 65,  // Ratios & Proportions
      3: 0    // Profit & Loss
    },
    logical: {
      1: 100, // Pattern Recognition
      2: 45,  // Syllogisms
      3: 0    // Data Interpretation
    },
    verbal: {
      1: 100, // Vocabulary
      2: 100, // Grammar
      3: 80   // Reading Comprehension
    }
  },
  learningGaps: [
    {
      type: "critical",
      fundamental: "retention",
      topic: "Formula memorization",
      severity: 0.8
    },
    {
      type: "moderate",
      fundamental: "listening",
      topic: "Audio comprehension",
      severity: 0.6
    }
  ],
  assessmentHistory: [],
  practiceHistory: []
};

export const mockModules = [
  {
    id: "quantitative",
    title: "Quantitative Aptitude",
    description: "Mathematical problem solving and numerical reasoning",
    icon: "Calculator",
    color: "hsl(221 83% 53%)",
    chapters: [
      { id: 1, title: "Percentages", status: "completed", progress: 100 },
      { id: 2, title: "Ratios & Proportions", status: "in-progress", progress: 65 },
      { id: 3, title: "Profit & Loss", status: "locked", progress: 0 }
    ]
  },
  {
    id: "logical",
    title: "Logical Reasoning & Data Interpretation",
    description: "Pattern recognition and data interpretation skills",
    icon: "Puzzle",
    color: "hsl(178 78% 35%)",
    chapters: [
      { id: 1, title: "Pattern Recognition", status: "completed", progress: 100 },
      { id: 2, title: "Syllogisms", status: "in-progress", progress: 45 },
      { id: 3, title: "Data Interpretation", status: "locked", progress: 0 }
    ]
  },
  {
    id: "verbal",
    title: "Verbal Ability & Reading Comprehension",
    description: "Language comprehension and communication skills",
    icon: "BookOpen",
    color: "hsl(43 96% 56%)",
    chapters: [
      { id: 1, title: "Vocabulary", status: "completed", progress: 100 },
      { id: 2, title: "Grammar", status: "completed", progress: 100 },
      { id: 3, title: "Reading Comprehension", status: "in-progress", progress: 80 }
    ]
  }
];

export const mockAssessmentQuestions = [
  {
    id: "q1",
    moduleId: "quantitative",
    chapterId: 1,
    questionText: "A shopkeeper marks his goods 40% above the cost price and gives a discount of 15%. What is his profit percentage?",
    options: ["19%", "21%", "25%", "28%"],
    correctAnswer: 0,
    difficulty: 3,
    fundamentalType: "application",
    questionType: "multiple-choice"
  },
  {
    id: "q2",
    moduleId: "logical",
    chapterId: 1,
    questionText: "In a series: 2, 6, 18, 54, ?, what is the next number?",
    options: ["108", "162", "216", "324"],
    correctAnswer: 1,
    difficulty: 2,
    fundamentalType: "grasping",
    questionType: "multiple-choice"
  },
  {
    id: "q3",
    moduleId: "verbal",
    chapterId: 1,
    questionText: "Choose the word that is most similar in meaning to 'METICULOUS':",
    options: ["Careless", "Careful", "Lazy", "Quick"],
    correctAnswer: 1,
    difficulty: 2,
    fundamentalType: "retention",
    questionType: "multiple-choice"
  },
  {
    id: "q4",
    moduleId: "quantitative",
    chapterId: 2,
    questionText: "If the ratio of two numbers is 3:4 and their sum is 84, what is the larger number?",
    options: ["36", "42", "48", "54"],
    correctAnswer: 2,
    difficulty: 3,
    fundamentalType: "application",
    questionType: "multiple-choice"
  },
  {
    id: "q5",
    moduleId: "logical",
    chapterId: 2,
    questionText: "All birds have wings. Some birds can fly. Therefore:",
    options: [
      "All birds can fly",
      "Some winged creatures can fly", 
      "Only birds can fly",
      "Wings are necessary for flying"
    ],
    correctAnswer: 1,
    difficulty: 4,
    fundamentalType: "grasping",
    questionType: "multiple-choice"
  }
];

export const mockClassOverview = {
  totalStudents: 28,
  activeThisWeek: 26,
  averageProgress: 68,
  needingAttention: 5,
  gapDistribution: {
    listening: 45,
    grasping: 68,
    retention: 38,
    application: 72
  }
};

export const mockStudents = [
  {
    id: "student-1",
    userId: "user-1",
    listeningScore: 65,
    graspingScore: 72,
    retentionScore: 58,
    applicationScore: 81,
    moduleProgress: { quantitative: 68, logical: 52, verbal: 74 }
  },
  {
    id: "student-2", 
    userId: "user-2",
    listeningScore: 68,
    graspingScore: 82,
    retentionScore: 76,
    applicationScore: 84,
    moduleProgress: { quantitative: 75, logical: 68, verbal: 82 }
  },
  {
    id: "student-3",
    userId: "user-3", 
    listeningScore: 45,
    graspingScore: 55,
    retentionScore: 42,
    applicationScore: 58,
    moduleProgress: { quantitative: 48, logical: 42, verbal: 55 }
  },
  {
    id: "student-4",
    userId: "user-4",
    listeningScore: 78,
    graspingScore: 85,
    retentionScore: 82,
    applicationScore: 88,
    moduleProgress: { quantitative: 85, logical: 78, verbal: 90 }
  },
  {
    id: "student-5",
    userId: "user-5",
    listeningScore: 62,
    graspingScore: 68,
    retentionScore: 55,
    applicationScore: 72,
    moduleProgress: { quantitative: 65, logical: 58, verbal: 70 }
  }
];
