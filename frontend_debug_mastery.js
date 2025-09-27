// Debug script to test frontend API calls
console.log('🔍 DEBUGGING FRONTEND API CALLS FOR MASTERY HISTORY...');
console.log('=' * 60);

// Test 1: Direct AdaptiveLearningAPI call
console.log('📡 Testing AdaptiveLearningAPI.getSessionHistory...');

// Simulate the API call that the frontend makes
const testUserId = 69;
const apiUrl = `http://localhost:8000/simple/session-history/${testUserId}/`;

console.log(`Making request to: ${apiUrl}`);

fetch(apiUrl)
  .then(response => {
    console.log('✅ Response status:', response.status);
    console.log('✅ Response headers:', [...response.headers.entries()]);
    return response.json();
  })
  .then(data => {
    console.log('✅ Raw API Response:');
    console.log(JSON.stringify(data, null, 2));
    
    console.log('\n📊 Parsed Data Summary:');
    console.log('- Success:', data.success);
    console.log('- Total Sessions:', data.total_sessions);
    console.log('- Sessions Array Length:', data.sessions?.length || 0);
    
    if (data.sessions && data.sessions.length > 0) {
      console.log('\n🎯 Latest Session Details:');
      const latest = data.sessions[0];
      console.log('- Date:', latest.session_date);
      console.log('- Subject:', latest.subject);
      console.log('- Accuracy:', latest.accuracy_percentage + '%');
      console.log('- Questions:', latest.questions_attempted);
      console.log('- Mastery Data:', latest.mastery_data ? 'Present' : 'Missing');
      
      if (latest.mastery_data) {
        console.log('- BKT Mastery:', latest.mastery_data.bkt_mastery);
        console.log('- DKT Prediction:', latest.mastery_data.dkt_prediction);
      }
    }
    
    console.log('\n🎉 API CALL SUCCESSFUL - Data is available!');
  })
  .catch(error => {
    console.error('❌ API Call Failed:', error);
  });

// Test 2: Check localStorage
console.log('\n💾 Checking localStorage...');
console.log('- pragatipath_backend_user_id:', localStorage.getItem('pragatipath_backend_user_id'));

// Test 3: Show current URL and confirm ports
console.log('\n🌐 Environment Check:');
console.log('- Current URL:', window.location.href);
console.log('- Expected Frontend Port: 5000');
console.log('- Expected Backend Port: 8000');