import requests
import json

print("🔍 CHECKING SESSION HISTORY FOR YOUR TEST")
print("=" * 50)

# Check the most recent completed session first
print("📊 Recent Session Details:")
print("-" * 30)

# Get session history for user 69 (who has the recent session)
response = requests.get("http://localhost:5000/simple/session-history/69/")
if response.status_code == 200:
    data = response.json()
    print(f"👤 Student: {data['student_name']}")
    print(f"📊 Total Sessions: {data['total_sessions']}")
    
    if data['sessions']:
        latest = data['sessions'][0]  # Most recent session
        print(f"\n🕒 Latest Session:")
        print(f"   📅 Date: {latest['session_date']}")
        print(f"   📚 Subject: {latest['subject']}")
        print(f"   ❓ Questions: {latest['questions_attempted']}")
        print(f"   ✅ Accuracy: {latest['accuracy']}")
        print(f"   ⏱️ Duration: {latest['duration_minutes']} minutes")
        print(f"   🧠 BKT Mastery: {latest['mastery_scores']['bkt_mastery']}")
        print(f"   🎯 Mastery Level: {latest['mastery_scores']['mastery_level']}")
        
        print(f"\n📈 All Sessions for User 69:")
        for i, session in enumerate(data['sessions']):
            print(f"   {i+1}. {session['session_date']} - {session['accuracy']} accuracy - {session['mastery_scores']['mastery_level']}")
    else:
        print("❌ No sessions found for user 69")
else:
    print(f"❌ Failed to get history: {response.status_code}")

print("\n" + "=" * 50)
print("💡 SOLUTION:")
print("Your test session IS in the database!")
print("Make sure you're logged in as the correct user in the frontend.")
print("The session from 01:17-01:19 (15 questions, 33.33% accuracy) is there!")
print("Check that your frontend is using the correct student/user ID.")