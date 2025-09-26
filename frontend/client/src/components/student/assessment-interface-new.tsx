import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Clock, Target, CheckCircle, X } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { 
  AssessmentAPI, 
  type Subject, 
  type Chapter, 
  type Question,
  type AssessmentResult
} from "@/lib/assessment-api";

interface AssessmentConfig {
  questionCount: number;
  timeLimit: number;
}

interface AssessmentInterfaceProps {
  chapter: Chapter;
  subject: Subject;
  onComplete: (result: AssessmentResult) => void;
  onBack: () => void;
  config?: AssessmentConfig;
}

type AssessmentState = 'setup' | 'active' | 'completed' | 'results';

export default function AssessmentInterface({ 
  chapter, 
  subject, 
  onComplete, 
  onBack,
  config 
}: AssessmentInterfaceProps) {
  const { user } = useAuth();
  const [assessmentState, setAssessmentState] = useState<AssessmentState>('setup');
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [confidence, setConfidence] = useState<number>(3);
  const [answers, setAnswers] = useState<Array<{
    questionId: string;
    selectedAnswer: string;
    timeSpent: number;
    confidence: number;
  }>>([]);

  // Assessment configuration - use passed config or defaults
  const [assessmentConfig, setAssessmentConfig] = useState({
    questionCount: config?.questionCount || 10,
    timeLimit: config?.timeLimit || 15,
    assessmentType: 'PRACTICE'
  });

  // Get questions for current assessment
  const { data: questionsData, isLoading: questionsLoading } = useQuery({
    queryKey: ['assessment-questions', assessmentId],
    queryFn: () => AssessmentAPI.getAssessmentQuestions(assessmentId!),
    enabled: !!assessmentId && assessmentState === 'active',
  });

  // Start assessment mutation
  const startAssessmentMutation = useMutation({
    mutationFn: AssessmentAPI.startAssessment,
    onSuccess: (response) => {
      setAssessmentId(response.assessment_id);
      setAssessmentState('active');
      // Use configured time limit or API response or default to 30 minutes
      const timeLimitSeconds = response.time_limit_minutes 
        ? response.time_limit_minutes * 60 
        : assessmentConfig.timeLimit * 60;
      setTimeRemaining(timeLimitSeconds);
      setQuestionStartTime(Date.now());
    },
    onError: (error) => {
      console.error('Failed to start assessment:', error);
    }
  });

  // Submit answer mutation
  const submitAnswerMutation = useMutation({
    mutationFn: AssessmentAPI.submitAnswer,
    onSuccess: (response) => {
      // Record the answer
      const timeSpent = Math.round((Date.now() - questionStartTime) / 1000);
      const newAnswer = {
        questionId: questionsData?.questions[currentQuestionIndex]?.question_id || '',
        selectedAnswer,
        timeSpent,
        confidence
      };
      
      setAnswers(prev => [...prev, newAnswer]);
      
      // Move to next question or complete assessment
      if (currentQuestionIndex < (questionsData?.questions.length || 0) - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        setSelectedAnswer('');
        setConfidence(3);
        setQuestionStartTime(Date.now());
      } else {
        completeAssessmentMutation.mutate(assessmentId!);
      }
    }
  });

  // Complete assessment mutation
  const completeAssessmentMutation = useMutation({
    mutationFn: AssessmentAPI.completeAssessment,
    onSuccess: (result) => {
      setAssessmentState('results');
      onComplete(result);
    }
  });

  // Timer effect
  useEffect(() => {
    if (assessmentState === 'active' && timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
      
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0 && assessmentState === 'active') {
      // Time's up, complete assessment
      completeAssessmentMutation.mutate(assessmentId!);
    }
  }, [timeRemaining, assessmentState, assessmentId]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartAssessment = () => {
    if (!user?.username) return;
    
    startAssessmentMutation.mutate({
      student_username: user.username,
      subject_code: subject.code,
      chapter_id: chapter.id,
      assessment_type: assessmentConfig.assessmentType,
      question_count: assessmentConfig.questionCount,
      time_limit_minutes: assessmentConfig.timeLimit
    });
  };

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    if (!selectedAnswer || !assessmentId || !questionsData) return;
    
    const timeSpent = Math.round((Date.now() - questionStartTime) / 1000);
    const currentQuestion = questionsData.questions[currentQuestionIndex];
    
    submitAnswerMutation.mutate({
      assessment_id: assessmentId,
      question_id: currentQuestion.question_id,
      selected_answer: selectedAnswer,
      time_taken_seconds: timeSpent,
      confidence_level: confidence
    });
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      // Restore previous answer if available
      const previousAnswer = answers[currentQuestionIndex - 1];
      if (previousAnswer) {
        setSelectedAnswer(previousAnswer.selectedAnswer);
        setConfidence(previousAnswer.confidence);
      }
    }
  };

  // Setup view
  if (assessmentState === 'setup') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Button
          variant="ghost"
          onClick={onBack}
          className="mb-4 p-0 h-auto font-normal text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Chapters
        </Button>

        <Card>
          <CardContent className="p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-foreground mb-2">
                Assessment Setup
              </h2>
              <p className="text-muted-foreground">
                {subject.name} - {chapter.name}
              </p>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 rounded-lg bg-muted/30">
                  <Target className="h-8 w-8 text-primary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-foreground">{assessmentConfig.questionCount}</div>
                  <div className="text-sm text-muted-foreground">Questions</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/30">
                  <Clock className="h-8 w-8 text-primary mx-auto mb-2" />
                  <div className="text-2xl font-bold text-foreground">{assessmentConfig.timeLimit}</div>
                  <div className="text-sm text-muted-foreground">Minutes</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-muted/30">
                  <CheckCircle className="h-8 w-8 text-primary mx-auto mb-2" />
                  <div className="text-lg font-bold text-foreground">Practice</div>
                  <div className="text-sm text-muted-foreground">Mode</div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground">Assessment Instructions</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-primary mr-2" />
                    Answer all questions to the best of your ability
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-primary mr-2" />
                    You can navigate between questions
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-primary mr-2" />
                    Indicate your confidence level for each answer
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-primary mr-2" />
                    Complete the assessment within the time limit
                  </li>
                </ul>
              </div>

              <Button 
                className="w-full" 
                onClick={handleStartAssessment}
                disabled={startAssessmentMutation.isPending}
              >
                {startAssessmentMutation.isPending ? 'Starting...' : 'Start Assessment'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Active assessment view
  if (assessmentState === 'active') {
    if (questionsLoading || !questionsData) {
      return (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      );
    }

    const currentQuestion = questionsData.questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questionsData.questions.length) * 100;

    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              {subject.name} Assessment
            </h3>
            <p className="text-sm text-muted-foreground">{chapter.name}</p>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            <Badge variant="outline">
              Question {currentQuestionIndex + 1} of {questionsData.questions.length}
            </Badge>
            <Badge variant="outline">
              <Clock className="h-3 w-3 mr-1" />
              {formatTime(timeRemaining)}
            </Badge>
          </div>
        </div>

        {/* Progress */}
        <div>
          <Progress value={progress} className="h-2" />
        </div>

        <Card>
          <CardContent className="p-8">
            {/* Question */}
            <div className="mb-8">
              <div className="bg-muted/30 rounded-lg p-6 mb-6">
                <p className="text-lg leading-relaxed text-foreground">
                  {currentQuestion.question_text}
                </p>
              </div>

              {/* Answer Options */}
              <div className="space-y-3">
                {Object.entries(currentQuestion.options).map(([key, value]) => (
                  <label
                    key={key}
                    className={`flex items-center space-x-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedAnswer === key
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="answer"
                      value={key}
                      checked={selectedAnswer === key}
                      onChange={(e) => handleAnswerSelect(e.target.value)}
                      className="text-primary focus:ring-primary"
                    />
                    <span className="text-foreground">{value}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Confidence Level */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-foreground mb-2">
                Confidence Level: {confidence}/5
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={confidence}
                onChange={(e) => setConfidence(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={handlePreviousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              
              <Button
                onClick={handleSubmitAnswer}
                disabled={!selectedAnswer || submitAnswerMutation.isPending}
              >
                {submitAnswerMutation.isPending ? 'Submitting...' : 
                 currentQuestionIndex === questionsData.questions.length - 1 ? 'Complete Assessment' : 'Next Question'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Results View
  if (assessmentState === 'results' || assessmentState === 'completed') {
    return (
      <div className="space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost" 
          onClick={onBack}
          className="mb-4 p-0 h-auto font-normal text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        {/* Results Header */}
        <Card>
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <CheckCircle className="h-16 w-16 text-chart-4 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-foreground mb-2">Assessment Completed!</h2>
              <p className="text-muted-foreground">
                {subject.name} - {chapter.name}
              </p>
            </div>
            
            {/* Overall Score */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary mb-1">
                  {Math.round(((completeAssessmentMutation.data?.questions_correct || 0) / (completeAssessmentMutation.data?.total_questions || 1)) * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-chart-4 mb-1">
                  {completeAssessmentMutation.data?.questions_correct || 0}/{completeAssessmentMutation.data?.total_questions || 0}
                </div>
                <div className="text-sm text-muted-foreground">Correct</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-accent mb-1">
                  {Math.floor((completeAssessmentMutation.data?.total_time_seconds || 0) / 60)}m {(completeAssessmentMutation.data?.total_time_seconds || 0) % 60}s
                </div>
                <div className="text-sm text-muted-foreground">Time Taken</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-secondary mb-1">
                  {completeAssessmentMutation.data?.grade || 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">Grade</div>
              </div>
            </div>

            {/* Performance Analysis */}
            {completeAssessmentMutation.data?.performance_analysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                {/* Strengths */}
                <div className="text-left">
                  <h4 className="font-semibold text-foreground mb-3 flex items-center">
                    <Target className="h-4 w-4 mr-2 text-chart-4" />
                    Strengths
                  </h4>
                  {completeAssessmentMutation.data.performance_analysis.strengths.length > 0 ? (
                    <div className="space-y-2">
                      {completeAssessmentMutation.data.performance_analysis.strengths.map((strength: string, index: number) => (
                        <Badge key={index} variant="secondary" className="mr-2 mb-2">
                          {strength}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground text-sm">Keep practicing to build your strengths!</p>
                  )}
                </div>

                {/* Improvement Areas */}
                <div className="text-left">
                  <h4 className="font-semibold text-foreground mb-3 flex items-center">
                    <X className="h-4 w-4 mr-2 text-destructive" />
                    Areas to Improve
                  </h4>
                  {completeAssessmentMutation.data.performance_analysis.improvement_areas.length > 0 ? (
                    <div className="space-y-2">
                      {completeAssessmentMutation.data.performance_analysis.improvement_areas.map((area: string, index: number) => (
                        <Badge key={index} variant="outline" className="mr-2 mb-2">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground text-sm">Great job! No specific areas need improvement.</p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Question by Question Results */}
        {completeAssessmentMutation.data?.question_results && (
          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold text-foreground mb-4">Question Review</h3>
              <div className="space-y-4">
                {completeAssessmentMutation.data.question_results.map((questionResult: any, index: number) => (
                  <div key={questionResult.question_id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div className="text-sm font-medium text-foreground">
                          Question {index + 1}
                        </div>
                        <Badge 
                          variant={questionResult.is_correct ? "default" : "destructive"}
                          className="text-xs"
                        >
                          {questionResult.is_correct ? "Correct" : "Incorrect"}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {questionResult.difficulty_level}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {questionResult.time_taken_seconds}s
                      </div>
                    </div>
                    
                    <p className="text-sm text-foreground mb-2">
                      {questionResult.question_text}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-xs">
                      <span className="text-muted-foreground">
                        Your answer: <span className="font-medium text-foreground">{questionResult.selected_answer.toUpperCase()}</span>
                      </span>
                      <span className="text-muted-foreground">
                        Correct answer: <span className="font-medium text-chart-4">{questionResult.correct_answer.toUpperCase()}</span>
                      </span>
                      <span className="text-muted-foreground">
                        Topic: <span className="font-medium text-foreground">{questionResult.topic}</span>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <Button onClick={onBack} variant="outline">
            Back to Dashboard  
          </Button>
          <Button onClick={() => {
            // Reset for new assessment
            setAssessmentState('setup');
            setAssessmentId(null);
            setCurrentQuestionIndex(0);
            setAnswers([]);
          }}>
            Take Another Assessment
          </Button>
        </div>
      </div>
    );
  }

  return null;
}