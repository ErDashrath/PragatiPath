import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth } from "@/hooks/use-auth";
import { apiRequest } from "@/lib/queryClient";

// Simple debug component to test API calls
export default function ExamDebugComponent() {
  const { user } = useAuth();
  const [debugLog, setDebugLog] = useState<string[]>([]);
  const [isTestRunning, setIsTestRunning] = useState(false);

  const addLog = (message: string) => {
    setDebugLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const runExamTest = async () => {
    setIsTestRunning(true);
    setDebugLog([]);
    
    try {
      addLog("🧪 Starting exam fetch test...");
      addLog(`👤 Current user: ${user?.username || 'Not logged in'} (ID: ${user?.id || 'N/A'})`);
      
      // Test 1: Direct fetch with apiRequest
      addLog("📚 Test 1: Fetching exams with apiRequest...");
      
      try {
        const response = await apiRequest("GET", "http://localhost:8000/api/enhanced-exam/student/exams/available");
        const data = await response.json();
        addLog(`✅ Success! Found ${data.length || 0} exams`);
        
        if (data.length > 0) {
          data.slice(0, 3).forEach((exam: any, i: number) => {
            addLog(`   ${i+1}. ${exam.exam_name || 'Unnamed'} - ${exam.status || 'Unknown status'}`);
          });
        }
      } catch (error: any) {
        addLog(`❌ apiRequest failed: ${error.message}`);
      }

      // Test 2: Direct fetch with credentials
      addLog("📚 Test 2: Direct fetch with credentials...");
      
      try {
        const response = await fetch("http://localhost:8000/api/enhanced-exam/student/exams/available", {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          addLog(`✅ Direct fetch success! Found ${data.length || 0} exams`);
        } else {
          addLog(`❌ Direct fetch failed: ${response.status} ${response.statusText}`);
          const errorText = await response.text();
          addLog(`   Error details: ${errorText}`);
        }
      } catch (error: any) {
        addLog(`❌ Direct fetch error: ${error.message}`);
      }

      // Test 3: User auth check
      addLog("👤 Test 3: Checking user authentication...");
      
      try {
        const response = await fetch("http://localhost:8000/api/core/user", {
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          addLog(`✅ User auth valid: ${userData.username} (${userData.userType || 'Unknown type'})`);
        } else {
          addLog(`❌ User auth failed: ${response.status}`);
        }
      } catch (error: any) {
        addLog(`❌ User auth error: ${error.message}`);
      }

    } catch (error: any) {
      addLog(`❌ Test failed: ${error.message}`);
    } finally {
      setIsTestRunning(false);
      addLog("🏁 Test completed!");
    }
  };

  // Real query test
  const { data: exams, isLoading, error, refetch } = useQuery({
    queryKey: ["debugExams"],
    queryFn: async () => {
      addLog("🔄 useQuery triggered...");
      const response = await apiRequest("GET", "http://localhost:8000/api/enhanced-exam/student/exams/available");
      const data = await response.json();
      addLog(`🔄 useQuery success: ${data.length} exams`);
      return data;
    },
    enabled: false // Don't run automatically, we'll trigger manually
  });

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>🧪 Exam API Debug Component</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          
          {/* User Info */}
          <div className="bg-blue-50 p-4 rounded">
            <h3 className="font-semibold">Current User:</h3>
            <p>Username: {user?.username || 'Not logged in'}</p>
            <p>ID: {user?.id || 'N/A'}</p>
            <p>Type: {user?.userType || 'Unknown'}</p>
          </div>

          {/* Test Button */}
          <Button 
            onClick={runExamTest} 
            disabled={isTestRunning}
            className="w-full"
          >
            {isTestRunning ? "Running Tests..." : "🚀 Run Exam API Tests"}
          </Button>

          {/* Trigger useQuery manually */}
          <Button 
            onClick={() => refetch()} 
            disabled={isLoading}
            className="w-full"
            variant="outline"
          >
            {isLoading ? "Loading..." : "🔄 Test useQuery"}
          </Button>

          {/* useQuery Status */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-semibold">useQuery Status:</h3>
            <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
            <p>Error: {error ? error.message : 'None'}</p>
            <p>Data: {exams ? `${exams.length} exams` : 'No data'}</p>
          </div>

          {/* Debug Log */}
          <div className="bg-black text-green-400 p-4 rounded font-mono text-sm max-h-96 overflow-y-auto">
            <h3 className="text-white font-semibold mb-2">Debug Log:</h3>
            {debugLog.length === 0 ? (
              <p className="text-gray-400">No logs yet. Click the test button to start.</p>
            ) : (
              debugLog.map((log, i) => (
                <div key={i} className="mb-1">{log}</div>
              ))
            )}
          </div>

        </CardContent>
      </Card>
    </div>
  );
}