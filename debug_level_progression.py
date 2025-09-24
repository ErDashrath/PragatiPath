#!/usr/bin/env python3
"""
Detailed Level Progression Debugging Test
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
sys.path.append('.')
django.setup()

import json
import urllib.request
import urllib.parse

def test_detailed_progression():
    """Test level progression with detailed debugging"""
    
    # Test data
    payload_template = {
        "student_id": "fec9dc2b-f347-498e-a66f-f01a976b9cee",
        "answer": "",
        "response_time": 5.0,
        "skill_id": "algebra",
        "metadata": {
            "attempt_number": 1,
            "hint_used": False
        }
    }
    
    questions = [
        {"id": "b80eda84-b166-4d1a-8029-8abe9e94ad0f", "answer": "x = 5"},
        {"id": "63629016-6ea3-463e-a330-0d4dd5f4b02b", "answer": "12"},
        {"id": "a3b84c12-9876-4321-abcd-ef1234567890", "answer": "x = 5"}  # This might not exist
    ]
    
    print("🔍 DETAILED LEVEL PROGRESSION DEBUG TEST")
    print("=" * 60)
    
    # Get initial student state
    print("\n📊 Checking initial student state...")
    try:
        from core.models import StudentProfile
        student = StudentProfile.objects.get(id="fec9dc2b-f347-498e-a66f-f01a976b9cee")
        
        print(f"   Current Level: {student.current_level.get('algebra', 'not set')}")
        print(f"   Consecutive Count: {student.consecutive_correct_count}")
        print(f"   BKT Parameters: {student.bkt_parameters.get('algebra', 'not set')}")
        print(f"   Mastery Threshold: {student.mastery_threshold}")
        
    except Exception as e:
        print(f"   Error getting student: {e}")
    
    # Test each question submission
    for i, q_data in enumerate(questions[:2], 1):  # Only test first 2 questions that exist
        print(f"\n📝 Test {i}: Submitting answer to question")
        
        payload = payload_template.copy()
        payload["question_id"] = q_data["id"]
        payload["answer"] = q_data["answer"]
        
        try:
            # Send request
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                "http://127.0.0.1:8000/api/assessment/submit-answer",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                print(f"   ✅ Response received")
                print(f"   📊 Was Correct: {result.get('was_correct')}")
                
                # Check BKT results
                bkt_results = result.get('algorithm_results', {}).get('bkt', {})
                print(f"   🧠 BKT Status: {bkt_results.get('status')}")
                print(f"   🧠 BKT Mastery: {bkt_results.get('new_mastery', 'unknown')}")
                
                # Check level progression
                level_progression = bkt_results.get('level_progression', {})
                print(f"   📚 Level Changed: {level_progression.get('level_changed', False)}")
                print(f"   📚 New Level: {level_progression.get('new_level', 'unknown')}")
                print(f"   📚 Consecutive Count: {level_progression.get('consecutive_count', 'unknown')}")
                print(f"   📚 Mastery Achieved: {level_progression.get('mastery_achieved', False)}")
                
                # Check congratulations
                congrats = level_progression.get('congratulations_message', '')
                if congrats:
                    print(f"   🎉 Message: {congrats}")
                
                # Check recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"   💡 Recommendations: {recommendations}")
                
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP Error {e.code}")
            error_response = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_response)
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {error_response}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Final student state check
    print("\n📊 Final student state...")
    try:
        student.refresh_from_db()
        
        print(f"   Current Level: {student.current_level.get('algebra', 'not set')}")
        print(f"   Unlocked Levels: {student.level_lock_status.get('algebra', [])}")
        print(f"   Consecutive Count: {student.consecutive_correct_count}")
        print(f"   BKT Parameters: {student.bkt_parameters.get('algebra', {})}")
        
        # Get progression service status
        from student_model.level_progression import LevelProgressionService
        progression_service = LevelProgressionService()
        status = progression_service.get_progression_status(student, 'algebra')
        
        print(f"\n🔍 Progression Service Status:")
        print(f"   Current Level: {status['current_level']}")
        print(f"   BKT Mastery: {status['bkt_mastery']:.3f}")
        print(f"   Mastery Threshold: {status['mastery_threshold']}")
        print(f"   Consecutive Count: {status['consecutive_correct_count']}")
        print(f"   Required Consecutive: {status['required_consecutive']}")
        print(f"   Mastery Achieved: {status['mastery_achieved']}")
        
    except Exception as e:
        print(f"   Error getting final state: {e}")
    
    print("\n🏁 Debug test completed!")

if __name__ == "__main__":
    test_detailed_progression()