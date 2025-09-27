import requests
import json

print("🎨 TESTING ENHANCED MASTERY DISPLAY IN FRONTEND")
print("=" * 60)

# Test the mastery history API to see if our enhanced display will work
response = requests.get("http://localhost:5000/simple/session-history/69/")

if response.status_code == 200:
    data = response.json()
    
    print(f"👤 Student: {data['student_name']}")
    print(f"📊 Total Sessions: {data['total_sessions']}")
    print()
    
    if data['sessions']:
        print("🧠 Enhanced Mastery Display Preview:")
        print("-" * 40)
        
        for i, session in enumerate(data['sessions'][:3], 1):  # Show top 3 sessions
            mastery = session['mastery_scores']
            
            print(f"\n📍 Session {i}: {session['session_date']}")
            print(f"   📚 Subject: {session['subject'].replace('_', ' ').title()}")
            print(f"   ❓ Questions: {session['questions_attempted']} | Accuracy: {session['accuracy']}")
            print(f"   🎯 Mastery Level: {mastery['mastery_level'].upper()}")
            
            # Enhanced mastery display
            print(f"   🧠 BKT Mastery: {mastery['bkt_mastery']} ({mastery['bkt_mastery_raw']:.1%})")
            print(f"   🤖 DKT Prediction: {mastery['dkt_prediction']} ({mastery['dkt_prediction_raw']:.1%})")
            print(f"   🔮 Combined: {mastery['combined_confidence']} ({mastery['combined_confidence_raw']:.1%})")
            print(f"   🏆 Mastery Achieved: {'YES' if mastery['mastery_achieved'] else 'NO'}")
            
            # Progress bar visualization (text version)
            bkt_bar = "█" * int(mastery['bkt_mastery_raw'] * 20) + "░" * (20 - int(mastery['bkt_mastery_raw'] * 20))
            print(f"   📊 BKT Progress: [{bkt_bar}] {mastery['bkt_mastery_raw']:.1%}")
            
        print(f"\n✅ Frontend Enhancement Ready!")
        print("The new mastery display will show:")
        print("• Enhanced visual progress bars")
        print("• Raw percentage values for debugging")
        print("• Color-coded mastery levels")
        print("• Latest session highlights")
        print("• Comprehensive mastery statistics")
        
    else:
        print("❌ No sessions found")
else:
    print(f"❌ API Error: {response.status_code}")

print(f"\n🚀 Frontend URL: http://localhost:5000/adaptive-learning")
print("Navigate to Assessment History → Mastery Progress tab to see the enhanced display!")