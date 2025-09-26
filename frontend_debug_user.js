// Add this debugging code to see current user info
console.log("=== DEBUGGING CURRENT USER ===");
console.log("User object:", user);
console.log("Username:", user?.username);
console.log("API call will be made to:", `/history/student/${user?.username || ''}/`);

// Test the API call directly from frontend
fetch(`/history/student/${user?.username}/`)
  .then(response => response.json())
  .then(data => {
    console.log("=== API RESPONSE ===");
    console.log("Success:", data.success);
    console.log("Total sessions:", data.summary?.total_sessions);
    console.log("Adaptive sessions:", data.summary?.adaptive_sessions_count);
    console.log("Assessment sessions:", data.summary?.assessment_sessions_count);
    console.log("Full response:", data);
  })
  .catch(err => {
    console.error("API Error:", err);
  });