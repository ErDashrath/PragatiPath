"""
Simple Test for LangGraph Orchestration Components

This script tests individual components first, then the full orchestration.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import StudentProfile
from assessment.improved_models import Subject, Chapter
from assessment.models import AdaptiveQuestion
from orchestration.adaptive_orchestrator import AdaptiveLearningState

def test_basic_components():
    """Test basic components work"""
    print("🧪 TESTING BASIC COMPONENTS")
    print("=" * 50)
    
    # Test database access
    subjects = Subject.objects.filter(is_active=True)
    print(f"✅ Found {subjects.count()} active subjects")
    
    questions = AdaptiveQuestion.objects.filter(is_active=True)
    print(f"✅ Found {questions.count()} active questions")
    
    users = User.objects.all()
    print(f"✅ Found {users.count()} users")
    
    if subjects.exists() and questions.exists() and users.exists():
        print("✅ All basic components working!")
        return True
    else:
        print("❌ Missing basic components")
        return False

def test_state_creation():
    """Test AdaptiveLearningState creation"""
    print("\n🧪 TESTING STATE CREATION")
    print("=" * 50)
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return False
            
        state = AdaptiveLearningState(
            student_id=str(user.id),
            subject_code='quantitative_aptitude',
            max_iterations=5
        )
        
        print(f"✅ State created successfully:")
        print(f"   Student ID: {state.student_id}")
        print(f"   Subject Code: {state.subject_code}")
        print(f"   Max Iterations: {state.max_iterations}")
        
        return True
        
    except Exception as e:
        print(f"❌ State creation failed: {e}")
        return False

def test_simple_orchestration():
    """Test simple orchestration workflow"""
    print("\n🧪 TESTING SIMPLE ORCHESTRATION") 
    print("=" * 50)
    
    try:
        from orchestration.adaptive_orchestrator import adaptive_orchestrator
        
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return False
            
        # Ensure user has StudentProfile
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'bkt_parameters': {},
                'dkt_hidden_state': [],
                'fundamentals': {
                    'listening': 0.5,
                    'grasping': 0.5, 
                    'retention': 0.5,
                    'application': 0.5
                },
                'interaction_history': []
            }
        )
        
        if created:
            print(f"✅ Created StudentProfile for {user.username}")
        
        print(f"🎯 Running orchestration for user: {user.username}")
        
        result = adaptive_orchestrator.run_adaptive_session(
            student_id=str(user.id),
            subject_code='quantitative_aptitude',
            max_iterations=2
        )
        
        print(f"📋 ORCHESTRATION RESULT:")
        print(f"   Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"   Subject: {result.get('subject', {}).get('name', 'Unknown')}")
            print(f"   Questions Attempted: {result.get('questions_attempted', 0)}")
            print(f"   BKT Mastery: {result.get('bkt_mastery', 0):.3f}")
            print(f"   DKT Prediction: {result.get('dkt_prediction', 0):.3f}")
            print("✅ Orchestration working!")
            return True
        else:
            print(f"   Error: {result.get('error_message', 'Unknown error')}")
            print("❌ Orchestration failed")
            return False
            
    except Exception as e:
        print(f"❌ Orchestration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_simple_test():
    """Run simple test suite"""
    print("🚀 SIMPLE LANGGRAPH ORCHESTRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Basic Components", test_basic_components),
        ("State Creation", test_state_creation), 
        ("Simple Orchestration", test_simple_orchestration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        success = test_func()
        if success:
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your LangGraph orchestration is working!")
    elif passed >= total - 1:
        print("⚠️ MOSTLY WORKING: Minor issues to address")
    else:
        print("❌ MAJOR ISSUES: Multiple components failing")
    
    print("=" * 60)

if __name__ == "__main__":
    run_simple_test()