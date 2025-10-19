import React from "react";
import EnhancedExamInterface from "@/components/student/EnhancedExamInterface";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Calendar, Award } from "lucide-react";

const StudentExamDashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Student Exam Portal</h1>
          <p className="text-lg text-gray-600">
            Access both adaptive learning and scheduled exam systems
          </p>
        </div>

        <Tabs defaultValue="scheduled" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="scheduled" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Scheduled Exams
            </TabsTrigger>
            <TabsTrigger value="adaptive" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Adaptive Learning
            </TabsTrigger>
          </TabsList>

          <TabsContent value="scheduled" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-blue-600" />
                  Enhanced Exam System
                </CardTitle>
                <CardDescription>
                  Take scheduled exams with adaptive difficulty adjustment and comprehensive analytics.
                  Questions adapt based on your knowledge state using BKT (Bayesian Knowledge Tracing).
                </CardDescription>
              </CardHeader>
            </Card>
            
            <EnhancedExamInterface />
          </TabsContent>

          <TabsContent value="adaptive" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-green-600" />
                  Adaptive Learning System
                </CardTitle>
                <CardDescription>
                  Practice with adaptive questions that adjust to your learning pace and knowledge level.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Your existing adaptive learning system remains unchanged and fully functional.
                  </p>
                  <p className="text-sm text-blue-600">
                    Navigate to the adaptive learning section to continue your practice sessions.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default StudentExamDashboard;