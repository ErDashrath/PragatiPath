#!/usr/bin/env python3
"""
FIXED Orchestration - Working Implementation 
Direct test of orchestration without Django server complications
"""

import os
import sys
import django
from datetime import datetime

# Add Backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assessment.settings')
django.setup()

# Now import Django models and services
from django.contrib.auth.models import User
from assessment.models import StudentSession
from student_model.bkt import BKTService
from orchestration.orchestration_service import OrchestrationService

def test_orchestration_directly():
    """Test orchestration service directly without server complications"""
    print("🔧 DIRECT ORCHESTRATION TEST")
    print("="*50)
    
    # Initialize services
    orchestration = OrchestrationService()
    bkt_service = BKTService()
    
    # Test student
    student_name = "DirectTestStudent"
    subject = "quantitative_aptitude"
    
    # Get or create user
    user, created = User.objects.get_or_create(username=student_name)
    print(f"✅ User {'created' if created else 'found'}: {student_name}")
    
    # Test BKT initialization
    skill_id = f"{subject}_skill"
    initial_bkt = bkt_service.get_skill_bkt_params(user, skill_id)
    print(f"📊 Initial BKT mastery: {initial_bkt.P_L:.3f}")
    
    # Test knowledge state retrieval
    knowledge_state = orchestration.get_comprehensive_knowledge_state(student_name, subject)
    print(f"🧠 Knowledge state result: {knowledge_state}")
    
    if knowledge_state.get('success'):
        print(f"   BKT Mastery: {knowledge_state['bkt_mastery']:.3f}")
        print(f"   DKT Prediction: {knowledge_state['dkt_prediction']:.3f}")
        print(f"   Combined Confidence: {knowledge_state['combined_confidence']:.3f}")
    
    # Simulate wrong answers to test adaptation
    print("\n🎯 Testing adaptation with wrong answers...")
    
    for i in range(3):
        print(f"\nAnswer {i+1} - INCORRECT")
        
        # Process wrong answer
        response = orchestration.process_student_response(
            student_username=student_name,
            subject=subject,
            question_id=f"test_q_{i}",
            is_correct=False,
            time_spent=10.0,
            difficulty_level="medium"
        )
        
        if response.get('success'):
            new_mastery = response.get('new_mastery_level', 0)
            print(f"   📉 New mastery: {new_mastery:.3f}")
            print(f"   💬 Adaptation: {response['orchestrated_feedback']['difficulty_adaptation']}")
        
        # Check updated knowledge state
        updated_state = orchestration.get_comprehensive_knowledge_state(student_name, subject)
        if updated_state.get('success'):
            combined = updated_state['combined_confidence']
            print(f"   🎯 Combined confidence: {combined:.3f}")
            
            # Test difficulty mapping
            if combined < 0.3:
                suggested_difficulty = "easy"
            elif combined < 0.45:
                suggested_difficulty = "medium"
            else:
                suggested_difficulty = "hard"
                
            print(f"   ⚡ Suggested difficulty: {suggested_difficulty}")
    
    print("\n🎉 DIRECT ORCHESTRATION TEST COMPLETE")
    print("✅ If you see mastery levels changing, orchestration is working!")

if __name__ == "__main__":
    test_orchestration_directly()