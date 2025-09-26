import { sql } from "drizzle-orm";
import { pgTable, text, varchar, jsonb, timestamp, integer, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  userType: text("user_type").notNull().default("student"), // 'student' or 'admin'
  name: text("name").notNull(),
});

export const studentProfiles = pgTable("student_profiles", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id).notNull(),
  listeningScore: integer("listening_score").default(50),
  graspingScore: integer("grasping_score").default(50),
  retentionScore: integer("retention_score").default(50),
  applicationScore: integer("application_score").default(50),
  moduleProgress: jsonb("module_progress").default({}), // { quantitative: 68, logical: 52, verbal: 74 }
  chapterProgress: jsonb("chapter_progress").default({}), // nested chapter progress
  learningGaps: jsonb("learning_gaps").default([]), // identified learning gaps
  assessmentHistory: jsonb("assessment_history").default([]),
  practiceHistory: jsonb("practice_history").default([]),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const modules = pgTable("modules", {
  id: varchar("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  icon: text("icon"),
  color: text("color"),
  chapters: jsonb("chapters").default([]), // chapter metadata
});

export const assessmentQuestions = pgTable("assessment_questions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  moduleId: varchar("module_id").references(() => modules.id),
  chapterId: integer("chapter_id"),
  questionText: text("question_text").notNull(),
  options: jsonb("options").notNull(), // array of options
  correctAnswer: integer("correct_answer").notNull(),
  difficulty: integer("difficulty").default(3), // 1-5 scale
  fundamentalType: text("fundamental_type"), // listening, grasping, retention, application
  questionType: text("question_type"),
});

export const assessmentSessions = pgTable("assessment_sessions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => users.id),
  moduleId: varchar("module_id").references(() => modules.id),
  chapterId: integer("chapter_id"),
  startTime: timestamp("start_time").defaultNow(),
  endTime: timestamp("end_time"),
  totalQuestions: integer("total_questions"),
  correctAnswers: integer("correct_answers"),
  finalDifficulty: integer("final_difficulty"),
  responses: jsonb("responses").default([]),
  isCompleted: boolean("is_completed").default(false),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
  userType: true,
  name: true,
});

export const insertStudentProfileSchema = createInsertSchema(studentProfiles).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertModuleSchema = createInsertSchema(modules);
export const insertAssessmentQuestionSchema = createInsertSchema(assessmentQuestions).omit({
  id: true,
});

export const insertAssessmentSessionSchema = createInsertSchema(assessmentSessions).omit({
  id: true,
  startTime: true,
  endTime: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type StudentProfile = typeof studentProfiles.$inferSelect;
export type InsertStudentProfile = z.infer<typeof insertStudentProfileSchema>;
export type Module = typeof modules.$inferSelect;
export type AssessmentQuestion = typeof assessmentQuestions.$inferSelect;
export type AssessmentSession = typeof assessmentSessions.$inferSelect;
export type InsertAssessmentSession = z.infer<typeof insertAssessmentSessionSchema>;
