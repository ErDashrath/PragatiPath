import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Globe } from "lucide-react";
import { queryClient } from "@/lib/queryClient";
import SessionConfig, { type SessionConfig as SessionConfigType } from "./session-config";
import { IndianTimeUtils } from "@/lib/indian-time-utils";

interface AssessmentInterfaceProps {
  chapter: any;
  moduleId: string;
  onComplete: () => void;
}

export default function AssessmentInterface({ chapter, moduleId, onComplete }: AssessmentInterfaceProps) {
  const [phase, setPhase] = useState<'config' | 'assessment'>('config');
  const [sessionConfig, setSessionConfig] = useState<SessionConfigType | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(50);
  const [timeRemaining, setTimeRemaining] = useState(600); // Default 10 minutes, will be updated by config
  const [difficulty, setDifficulty] = useState(3);
  const [answers, setAnswers] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);

  const { data: questions, isLoading } = useQuery({
    queryKey: ["/api/assessment/questions", moduleId, chapter.id],
    enabled: !!moduleId && !!chapter.id,
  });

  const createSessionMutation = useMutation({
    mutationFn: async (sessionData: any) => {
      const response = await fetch("/api/assessment/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sessionData),
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to create session");
      return response.json();
    },
    onSuccess: (session) => {
      setSessionId(session.id);
    },
  });

  const updateSessionMutation = useMutation({
    mutationFn: async ({ sessionId, updates }: { sessionId: string; updates: any }) => {
      const response = await fetch(`/api/assessment/session/${sessionId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to update session");
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/student-profile"] });
    },
  });

  const handleStartSession = (config: SessionConfigType) => {
    setSessionConfig(config);
    setTimeRemaining(config.timeLimit);
    setSessionStartTime(IndianTimeUtils.getCurrentIST());
    setPhase('assessment');
  };

  useEffect(() => {
    if (questions && !sessionId && phase === 'assessment' && sessionConfig) {
      createSessionMutation.mutate({
        moduleId,
        chapterId: chapter.id,
        totalQuestions: sessionConfig.questionCount,
        finalDifficulty: difficulty,
        responses: [],
      });
    }
  }, [questions, moduleId, chapter.id, sessionId]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(prev => prev - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      handleFinishAssessment();
    }
  }, [timeRemaining]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyText = (level: number) => {
    const levels = ['Beginner', 'Basic', 'Intermediate', 'Advanced', 'Expert'];
    return levels[level - 1] || 'Intermediate';
  };

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleNextQuestion = () => {
    if (selectedAnswer) {
      const newAnswers = [...answers];
      newAnswers[currentQuestion - 1] = selectedAnswer;
      setAnswers(newAnswers);

      // Simulate adaptive difficulty adjustment
      adjustDifficulty(selectedAnswer === 'A'); // Assume A is correct for demo

      if (currentQuestion < totalQuestions) {
        setCurrentQuestion(prev => prev + 1);
        setSelectedAnswer(null);
      } else {
        handleFinishAssessment();
      }
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestion > 1) {
      setCurrentQuestion(prev => prev - 1);
      setSelectedAnswer(answers[currentQuestion - 2] || null);
    }
  };

  const adjustDifficulty = (isCorrect: boolean) => {
    if (isCorrect && difficulty < 5) {
      setDifficulty(Math.min(5, difficulty + 0.5));
    } else if (!isCorrect && difficulty > 1) {
      setDifficulty(Math.max(1, difficulty - 0.5));
    }
  };

  const handleShowHint = () => {
    alert('Hint: Consider the relationship between the given values and look for patterns or formulas that might apply.');
  };

  const handleFinishAssessment = () => {
    if (sessionId) {
      const correctAnswers = answers.filter(answer => answer === 'A').length; // Demo logic
      
      updateSessionMutation.mutate({
        sessionId,
        updates: {
          endTime: new Date().toISOString(),
          correctAnswers,
          finalDifficulty: difficulty,
          responses: answers.map((answer, index) => ({
            questionId: questionsArray[index]?.id,
            selectedAnswer: answer,
            confidence,
            timeSpent: 30, // Demo value
          })),
          isCompleted: true,
        },
      });
    }
    
    onComplete();
  };

  // Show configuration screen first
  if (phase === 'config') {
    return (
      <SessionConfig
        title="Configure Assessment"
        description={`Set up your assessment for Chapter ${chapter.id}: ${chapter.title}. Choose the number of questions, time limit, and difficulty level.`}
        onStartSession={handleStartSession}
        onCancel={onComplete}
      />
    );
  }

  if (isLoading || !questions) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const totalQuestions = sessionConfig?.questionCount || 15;
  const questionsArray = Array.isArray(questions) ? questions : [];
  const currentQuestionData = questionsArray[(currentQuestion - 1) % Math.max(questionsArray.length, 1)];
  const progressPercent = (currentQuestion / totalQuestions) * 100;

  return (
    <div className="max-w-4xl mx-auto" data-testid="assessment-interface">
      <Card className="shadow-lg">
        <CardContent className="p-8">
          {/* Assessment Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-foreground">Adaptive Assessment</h3>
              <p className="text-sm text-muted-foreground">
                Chapter {chapter.id}: {chapter.title}
              </p>
            </div>
            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <div data-testid="question-counter">
                Question <span className="font-medium">{currentQuestion}</span> of{" "}
                <span className="font-medium">{totalQuestions}</span>
              </div>
              <div data-testid="difficulty-level">
                Difficulty: <Badge variant="outline" className="ml-1">{getDifficultyText(difficulty)}</Badge>
              </div>
              <div data-testid="time-remaining">
                Time: <span className="font-medium text-primary font-mono">{IndianTimeUtils.formatCountdown(timeRemaining)}</span>
              </div>
              {/* IST Session Info */}
              {sessionConfig && sessionStartTime && (
                <div className="text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Globe className="h-3 w-3" />
                    <span>Started: {sessionConfig.startTime?.split(' ')[1] || 'N/A'} IST</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-muted rounded-full h-2 mb-8">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
              data-testid="assessment-progress"
            ></div>
          </div>

          {/* Question */}
          <div className="mb-8">
            <div className="bg-muted/30 rounded-lg p-6 mb-6">
              <p className="text-foreground text-lg leading-relaxed" data-testid="question-text">
                {currentQuestionData?.questionText}
              </p>
            </div>

            {/* Answer Options */}
            <div className="space-y-3" data-testid="answer-options">
              {currentQuestionData?.options?.map((option: string, index: number) => {
                const optionLetter = String.fromCharCode(65 + index);
                return (
                  <label
                    key={index}
                    className={`flex items-center space-x-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedAnswer === optionLetter
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                    data-testid={`option-${optionLetter}`}
                  >
                    <input
                      type="radio"
                      name="answer"
                      value={optionLetter}
                      checked={selectedAnswer === optionLetter}
                      onChange={(e) => handleAnswerSelect(e.target.value)}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="text-foreground">{option}</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Assessment Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleShowHint}
                className="flex items-center space-x-2"
                data-testid="button-hint"
              >
                <Lightbulb className="h-4 w-4" />
                <span>Hint</span>
              </Button>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">Confidence:</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={confidence}
                  onChange={(e) => setConfidence(Number(e.target.value))}
                  className="w-24"
                  data-testid="confidence-slider"
                />
                <span className="text-sm font-medium text-foreground w-12">
                  {confidence}%
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={handlePrevQuestion}
                disabled={currentQuestion === 1}
                data-testid="button-prev-question"
              >
                Previous
              </Button>
              <Button
                onClick={handleNextQuestion}
                disabled={!selectedAnswer}
                data-testid="button-next-question"
              >
                {currentQuestion === totalQuestions ? 'Finish Assessment' : 'Next Question'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
