#!/usr/bin/env python3
"""
Debug BKT Update Issue
Direct test to isolate the problem
"""
import os
import sys
import django

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from student_model.bkt import BKTService, initialize_bkt_skill, update_bkt
from orchestration.orchestration_service import OrchestrationService

def test_direct_bkt_math():
    """Test the BKT math directly"""
    print("🧪 DIRECT BKT MATHEMATICAL TEST")
    print("="*50)
    
    # Test the raw math
    skill_params = initialize_bkt_skill("test_skill")
    print(f"Initial BKT params: P_L={skill_params.P_L:.6f}")
    
    # Test wrong answer
    after_wrong = update_bkt(skill_params, is_correct=False)
    print(f"After wrong answer: P_L={after_wrong.P_L:.6f}")
    print(f"Change: {after_wrong.P_L - skill_params.P_L:+.6f}")
    
    # Test correct answer from initial
    after_correct = update_bkt(skill_params, is_correct=True)
    print(f"After correct answer: P_L={after_correct.P_L:.6f}")
    print(f"Change: {after_correct.P_L - skill_params.P_L:+.6f}")

def test_bkt_service():
    """Test BKT service with actual user"""
    print("\n🏗️ BKT SERVICE TEST")
    print("="*50)
    
    # Create test user
    username = "bkt_test_user"
    user, created = User.objects.get_or_create(username=username)
    if created:
        print(f"✅ Created test user: {username}")
    else:
        print(f"📋 Using existing user: {username}")
    
    skill_id = "test_skill"
    
    # Get initial BKT params
    initial_params = BKTService.get_skill_bkt_params(user, skill_id)
    print(f"Initial mastery: {initial_params.P_L:.6f}")
    
    # Update with wrong answer
    print("\n❌ Testing wrong answer update:")
    updated_params = BKTService.update_skill_bkt(
        user=user,
        skill_id=skill_id,
        is_correct=False,
        interaction_data={'timestamp': 'test', 'question_id': 'test_q1'}
    )
    print(f"After wrong answer: {updated_params.P_L:.6f}")
    print(f"Change: {updated_params.P_L - initial_params.P_L:+.6f}")
    
    # Update with correct answer
    print("\n✅ Testing correct answer update:")
    updated_params2 = BKTService.update_skill_bkt(
        user=user,
        skill_id=skill_id,
        is_correct=True,
        interaction_data={'timestamp': 'test', 'question_id': 'test_q2'}
    )
    print(f"After correct answer: {updated_params2.P_L:.6f}")
    print(f"Change: {updated_params2.P_L - updated_params.P_L:+.6f}")

def test_orchestration_service():
    """Test orchestration service"""
    print("\n🎼 ORCHESTRATION SERVICE TEST")
    print("="*50)
    
    service = OrchestrationService()
    
    # Initialize session
    username = "orchestration_test"
    subject = "quantitative_aptitude"
    
    print(f"🎬 Initializing session for {username}...")
    init_result = service.initialize_student_session(username, subject)
    print(f"Init result: {init_result}")
    
    if init_result.get('success'):
        print(f"Initial mastery: {init_result.get('initial_mastery', 'N/A')}")
        
        # Test wrong answer
        print(f"\n❌ Testing wrong answer through orchestration:")
        wrong_result = service.process_interaction(
            student_username=username,
            subject=subject,
            question_id="test_q1",
            is_correct=False,
            time_spent=10,
            difficulty_level="moderate"
        )
        
        print(f"Wrong answer result success: {wrong_result.get('success')}")
        if 'bkt_mastery' in wrong_result:
            print(f"New mastery: {wrong_result['bkt_mastery']:.6f}")
        else:
            print(f"No bkt_mastery in result: {list(wrong_result.keys())}")
        
        # Test correct answer
        print(f"\n✅ Testing correct answer through orchestration:")
        correct_result = service.process_interaction(
            student_username=username,
            subject=subject,
            question_id="test_q2",
            is_correct=True,
            time_spent=8,
            difficulty_level="moderate"
        )
        
        print(f"Correct answer result success: {correct_result.get('success')}")
        if 'bkt_mastery' in correct_result:
            print(f"New mastery: {correct_result['bkt_mastery']:.6f}")
        else:
            print(f"No bkt_mastery in result: {list(correct_result.keys())}")

def main():
    try:
        test_direct_bkt_math()
        test_bkt_service()
        test_orchestration_service()
        
        print("\n🎯 DEBUG SUMMARY:")
        print("   If the direct math works but service doesn't,")
        print("   there's an issue in the service implementation.")
        print("   If orchestration doesn't work, there's an issue")
        print("   in the orchestration service.")
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()