import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { BookOpen, Shuffle, Target, Zap } from "lucide-react";

export default function PracticeView() {
  const practiceModes = [
    {
      id: 'chapter',
      title: 'Chapter Practice',
      description: 'Focus on specific chapters and topics',
      icon: BookOpen,
      color: 'primary',
      buttonText: 'Select Chapter',
    },
    {
      id: 'mixed',
      title: 'Mixed Practice',
      description: 'Balanced mix from all topics',
      icon: Shuffle,
      color: 'secondary',
      buttonText: 'Start Mixed',
    },
    {
      id: 'targeted',
      title: 'Targeted Practice',
      description: 'Focus on your weak areas',
      icon: Target,
      color: 'accent',
      buttonText: 'Find Weaknesses',
    },
    {
      id: 'quick',
      title: 'Quick Challenge',
      description: '5-minute timed sessions',
      icon: Zap,
      color: 'chart-4',
      buttonText: 'Quick Start',
    },
  ];

  const handlePracticeModeSelect = (modeId: string) => {
    switch (modeId) {
      case 'chapter':
        alert('Select a specific chapter to practice from the modules section.');
        break;
      case 'mixed':
        alert('Starting mixed practice session with questions from all topics...');
        break;
      case 'targeted':
        alert('Analyzing your weak areas and generating targeted practice questions...');
        break;
      case 'quick':
        alert('Starting 5-minute quick challenge session...');
        break;
      default:
        break;
    }
  };

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'primary':
        return {
          iconBg: 'bg-primary/10',
          iconColor: 'text-primary',
          button: 'bg-primary hover:bg-primary/90 text-primary-foreground',
        };
      case 'secondary':
        return {
          iconBg: 'bg-secondary/10',
          iconColor: 'text-secondary',
          button: 'bg-secondary hover:bg-secondary/90 text-secondary-foreground',
        };
      case 'accent':
        return {
          iconBg: 'bg-accent/10',
          iconColor: 'text-accent',
          button: 'bg-accent hover:bg-accent/90 text-accent-foreground',
        };
      case 'chart-4':
        return {
          iconBg: 'bg-chart-4/10',
          iconColor: 'text-chart-4',
          button: 'bg-chart-4 hover:bg-chart-4/90 text-white',
        };
      default:
        return {
          iconBg: 'bg-primary/10',
          iconColor: 'text-primary',
          button: 'bg-primary hover:bg-primary/90 text-primary-foreground',
        };
    }
  };

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">Practice Modes</h2>
        <p className="text-muted-foreground">Choose your preferred practice method</p>
      </div>

      {/* Practice Mode Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {practiceModes.map((mode) => {
          const Icon = mode.icon;
          const colors = getColorClasses(mode.color);

          return (
            <Card
              key={mode.id}
              className="hover:shadow-md transition-all duration-300 cursor-pointer group"
              onClick={() => handlePracticeModeSelect(mode.id)}
              data-testid={`practice-mode-${mode.id}`}
            >
              <CardContent className="p-6 text-center">
                <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${colors.iconBg} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  <Icon className={`h-8 w-8 ${colors.iconColor}`} />
                </div>
                
                <h3 className="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                  {mode.title}
                </h3>
                
                <p className="text-sm text-muted-foreground mb-4">
                  {mode.description}
                </p>
                
                <Button
                  className={`w-full ${colors.button}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePracticeModeSelect(mode.id);
                  }}
                  data-testid={`button-${mode.id}`}
                >
                  {mode.buttonText}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Practice Settings */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Practice Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="difficulty" className="text-sm font-medium text-foreground mb-2 block">
                Difficulty Level
              </Label>
              <select
                id="difficulty"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                data-testid="select-difficulty"
              >
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
                <option>Expert</option>
              </select>
            </div>
            
            <div>
              <Label htmlFor="questions" className="text-sm font-medium text-foreground mb-2 block">
                Number of Questions
              </Label>
              <select
                id="questions"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                data-testid="select-questions"
              >
                <option>10 Questions</option>
                <option>15 Questions</option>
                <option>20 Questions</option>
                <option>25 Questions</option>
              </select>
            </div>
            
            <div>
              <Label htmlFor="time-limit" className="text-sm font-medium text-foreground mb-2 block">
                Time Limit
              </Label>
              <select
                id="time-limit"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-background"
                data-testid="select-time-limit"
              >
                <option>No Limit</option>
                <option>5 Minutes</option>
                <option>10 Minutes</option>
                <option>15 Minutes</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Practice Tips */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Practice Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-foreground">For Better Results:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <span>Practice regularly for at least 30 minutes daily</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <span>Focus on your identified weak areas first</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <span>Review explanations for incorrect answers</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-foreground">Adaptive Features:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-secondary rounded-full mt-2"></div>
                  <span>Questions adapt to your performance in real-time</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-secondary rounded-full mt-2"></div>
                  <span>Spaced repetition for better retention</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-secondary rounded-full mt-2"></div>
                  <span>Progress tracking across four fundamentals</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
