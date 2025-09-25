# Test the comprehensive orchestration endpoint

$payload = @{
    student_id = 'fec9dc2b-f347-498e-a66f-f01a976b9cee'
    question_id = 'b80eda84-b166-4d1a-8029-8abe9e94ad0f'
    answer = 'x = 5'
    response_time = 8.5
    skill_id = 'algebra'
    metadata = @{
        attempt_number = 1
        hint_used = $false
    }
} | ConvertTo-Json -Depth 3

Write-Host "🚀 Testing Orchestration Endpoint..." -ForegroundColor Green
Write-Host "Payload:" -ForegroundColor Yellow
Write-Host $payload -ForegroundColor Cyan

Write-Host "`n📡 Sending request..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/assessment/submit-answer' -Method POST -Body $payload -ContentType 'application/json'
    
    Write-Host "✅ SUCCESS! Response received:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ ERROR occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body:" -ForegroundColor Yellow
        Write-Host $responseBody -ForegroundColor Cyan
    }
}

Write-Host "`n🎯 Test completed!" -ForegroundColor Green