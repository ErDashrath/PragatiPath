import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Clock, Brain, Target, Settings, Globe } from "lucide-react";
import { IndianTimeUtils, useISTTime } from "@/lib/indian-time-utils";

interface SessionConfigProps {
  title: string;
  description: string;
  onStartSession: (config: SessionConfig) => void;
  onCancel?: () => void;
}

export interface SessionConfig {
  questionCount: number;
  timeLimit: number; // in seconds
  difficulty?: 'easy' | 'medium' | 'hard' | 'adaptive';
  startTime?: string; // IST start time
}

const QUESTION_OPTIONS = [
  { value: 10, label: "10 Questions", description: "Quick assessment (~10-15 mins)" },
  { value: 15, label: "15 Questions", description: "Standard assessment (~15-20 mins)" },
  { value: 20, label: "20 Questions", description: "Comprehensive assessment (~20-30 mins)" },
  { value: 30, label: "30 Questions", description: "Full assessment (~30-45 mins)" }
];

const TIME_OPTIONS = [
  { value: 300, label: "5 Minutes", description: "Quick practice" },
  { value: 600, label: "10 Minutes", description: "Standard timing" },
  { value: 900, label: "15 Minutes", description: "Extended time" },
  { value: 1200, label: "20 Minutes", description: "Full duration" },
  { value: 1800, label: "30 Minutes", description: "Maximum time" }
];

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: "Easy", description: "Basic concepts", icon: "🟢" },
  { value: 'medium', label: "Medium", description: "Moderate difficulty", icon: "🟡" },
  { value: 'hard', label: "Hard", description: "Advanced level", icon: "🔴" },
  { value: 'adaptive', label: "Adaptive", description: "AI adjusts difficulty", icon: "🧠" }
];

export default function SessionConfig({ 
  title, 
  description, 
  onStartSession, 
  onCancel 
}: SessionConfigProps) {
  const [questionCount, setQuestionCount] = useState(15);
  const [timeLimit, setTimeLimit] = useState(600);
  const [difficulty, setDifficulty] = useState<SessionConfig['difficulty']>('medium');
  const currentISTTime = useISTTime();

  const handleStartSession = () => {
    onStartSession({
      questionCount,
      timeLimit,
      difficulty,
      startTime: IndianTimeUtils.getSessionStartTime()
    });
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    return minutes === 1 ? "1 minute" : `${minutes} minutes`;
  };

  const selectedQuestionOption = QUESTION_OPTIONS.find(opt => opt.value === questionCount);
  const selectedTimeOption = TIME_OPTIONS.find(opt => opt.value === timeLimit);
  const selectedDifficultyOption = DIFFICULTY_OPTIONS.find(opt => opt.value === difficulty);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center mb-2">
            <Settings className="h-8 w-8 text-primary mr-2" />
          </div>
          <CardTitle className="text-2xl">{title}</CardTitle>
          <p className="text-muted-foreground">{description}</p>
          
          {/* Current IST Time Display */}
          <div className="mt-4 p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center justify-center gap-2 text-sm">
              <Globe className="h-4 w-4 text-primary" />
              <span className="font-medium">Current Time (IST):</span>
              <span className="text-primary font-mono">{currentISTTime}</span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {IndianTimeUtils.formatISTDate()} • {IndianTimeUtils.getTimezoneInfo()}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Question Count Selection */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Number of Questions</h3>
            </div>
            <Select value={questionCount.toString()} onValueChange={(value) => setQuestionCount(Number(value))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {QUESTION_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    <div className="flex flex-col">
                      <span className="font-medium">{option.label}</span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedQuestionOption && (
              <p className="text-sm text-muted-foreground">
                {selectedQuestionOption.description}
              </p>
            )}
          </div>

          {/* Time Limit Selection */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Time Limit</h3>
            </div>
            <Select value={timeLimit.toString()} onValueChange={(value) => setTimeLimit(Number(value))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIME_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    <div className="flex flex-col">
                      <span className="font-medium">{option.label}</span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedTimeOption && (
              <p className="text-sm text-muted-foreground">
                {selectedTimeOption.description}
              </p>
            )}
          </div>

          {/* Difficulty Selection */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Difficulty Level</h3>
            </div>
            <Select value={difficulty} onValueChange={(value) => setDifficulty(value as SessionConfig['difficulty'])}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DIFFICULTY_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div className="flex items-center gap-2">
                      <span>{option.icon}</span>
                      <div className="flex flex-col">
                        <span className="font-medium">{option.label}</span>
                        <span className="text-xs text-muted-foreground">{option.description}</span>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedDifficultyOption && (
              <p className="text-sm text-muted-foreground">
                {selectedDifficultyOption.description}
              </p>
            )}
          </div>

          {/* Summary Card */}
          <Card className="bg-muted/50">
            <CardContent className="pt-4">
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Session Summary
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Questions:</span>
                  <Badge variant="secondary">{questionCount}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Time Limit:</span>
                  <Badge variant="secondary">{formatTime(timeLimit)}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Difficulty:</span>
                  <Badge variant="outline" className="capitalize">
                    {selectedDifficultyOption?.icon} {difficulty}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            {onCancel && (
              <Button variant="outline" onClick={onCancel} className="flex-1">
                Cancel
              </Button>
            )}
            <Button onClick={handleStartSession} className="flex-1">
              Start Session
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}