import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function DebugSubjectsAPI() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const testAPI = async () => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      console.log("🧪 Testing API call from React...");
      const response = await fetch("http://localhost:8000/api/enhanced-exam/admin/subjects/details", {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log("📊 Response status:", response.status);
      console.log("📋 Response headers:", response.headers);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log("📄 API Result:", result);
      setData(result);
    } catch (err) {
      console.error("❌ API Error:", err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto mt-4">
      <CardHeader>
        <CardTitle>🧪 Debug Subjects API</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={testAPI} disabled={loading}>
          {loading ? "Testing..." : "Test API Call"}
        </Button>
        
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {data && (
          <div className="space-y-2">
            <div className="p-4 bg-green-50 border border-green-200 rounded">
              <strong>✅ Success!</strong> Got {Array.isArray(data) ? data.length : 'non-array'} subjects
            </div>
            
            <div className="p-4 bg-gray-50 border border-gray-200 rounded">
              <strong>Data Type:</strong> {typeof data} {Array.isArray(data) ? '(Array)' : '(Object)'}
            </div>
            
            {Array.isArray(data) && data.length > 0 && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <strong>Sample Subject:</strong>
                <pre className="mt-2 text-sm">{JSON.stringify(data[0], null, 2)}</pre>
              </div>
            )}
            
            <details className="p-4 bg-gray-50 border border-gray-200 rounded">
              <summary className="cursor-pointer font-semibold">Full Response</summary>
              <pre className="mt-2 text-xs overflow-auto max-h-96">{JSON.stringify(data, null, 2)}</pre>
            </details>
          </div>
        )}
      </CardContent>
    </Card>
  );
}