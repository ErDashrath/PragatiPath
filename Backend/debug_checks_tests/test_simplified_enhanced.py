"""
Quick Test for Simplified Enhanced Adaptive System
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from simplified_enhanced_adaptive import get_simplified_enhanced_question
from assessment.improved_models import StudentSession

def test_simplified_enhanced():
    print("🧪 Testing Simplified Enhanced Adaptive System")
    print("=" * 50)
    
    # Get existing sessions
    sessions = StudentSession.objects.all()[:3]
    
    if not sessions.exists():
        print("❌ No sessions found")
        return
    
    success_count = 0
    
    for session in sessions:
        print(f"\n📍 Testing session: {session.id}")
        print(f"   Student: {session.student.username}")
        print(f"   Subject: {session.subject}")
        
        try:
            result = get_simplified_enhanced_question(str(session.id))
            
            if result.get('success'):
                print(f"   ✅ Success!")
                print(f"      Difficulty: {result.get('difficulty')}")
                print(f"      Strategy: {result.get('enhanced_info', {}).get('adaptation_strategy')}")
                print(f"      Mastery: {result.get('enhanced_info', {}).get('mastery_level', 0):.3f}")
                success_count += 1
            else:
                error_msg = result.get('error', result.get('message', 'Unknown'))
                print(f"   ❌ Failed: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{len(sessions)} successful")
    
    if success_count > 0:
        print("🎉 Simplified Enhanced System Working!")
    else:
        print("❌ System needs more debugging")

if __name__ == "__main__":
    test_simplified_enhanced()