import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Clock, Target, Settings, Globe } from "lucide-react";
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

export default function SessionConfig({ 
  title, 
  description, 
  onStartSession, 
  onCancel 
}: SessionConfigProps) {
  const [questionCount, setQuestionCount] = useState(15);
  const [timeLimit, setTimeLimit] = useState(600);
  const currentISTTime = useISTTime();

  const handleStartSession = () => {
    onStartSession({
      questionCount,
      timeLimit,
      difficulty: 'adaptive', // Always use adaptive for best experience
      startTime: IndianTimeUtils.getSessionStartTime()
    });
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    return minutes === 1 ? "1 minute" : `${minutes} minutes`;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-center mb-2">
            <Settings className="h-6 w-6 text-primary mr-2" />
          </div>
          <CardTitle className="text-xl">{title}</CardTitle>
          <p className="text-sm text-muted-foreground">{description}</p>
          
          {/* Current IST Time Display */}
          <div className="mt-3 p-2 bg-muted/50 rounded-lg">
            <div className="flex items-center justify-center gap-2 text-xs">
              <Globe className="h-3 w-3 text-primary" />
              <span className="font-medium">Current Time (IST):</span>
              <span className="text-primary font-mono">{currentISTTime}</span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {IndianTimeUtils.formatISTDate()} • {IndianTimeUtils.getTimezoneInfo()}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Question Count Selection */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              <h3 className="font-medium text-sm">Number of Questions</h3>
            </div>
            <Select value={questionCount.toString()} onValueChange={(value) => setQuestionCount(Number(value))}>
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {QUESTION_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    <div className="flex flex-col">
                      <span className="font-medium text-sm">{option.label}</span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Time Limit Selection */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" />
              <h3 className="font-medium text-sm">Time Limit</h3>
            </div>
            <Select value={timeLimit.toString()} onValueChange={(value) => setTimeLimit(Number(value))}>
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIME_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value.toString()}>
                    <div className="flex flex-col">
                      <span className="font-medium text-sm">{option.label}</span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Summary Card */}
          <Card className="bg-muted/50">
            <CardContent className="pt-3 pb-3">
              <h4 className="font-medium mb-2 flex items-center gap-2 text-sm">
                <Settings className="h-3 w-3" />
                Session Summary
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Questions:</span>
                  <Badge variant="secondary" className="text-xs">{questionCount}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Time Limit:</span>
                  <Badge variant="secondary" className="text-xs">{formatTime(timeLimit)}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            {onCancel && (
              <Button variant="outline" onClick={onCancel} className="flex-1 h-8 text-sm">
                Cancel
              </Button>
            )}
            <Button onClick={handleStartSession} className="flex-1 h-8 text-sm">
              Start Session
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}