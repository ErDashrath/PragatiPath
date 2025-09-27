"""
LangGraph Orchestration Diagnostic and Fix

This script tests and fixes the LangGraph orchestration with BKT/DKT integration
to ensure everything works properly.

Author: AI Assistant
Date: 2024-12-26
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import StudentProfile
from student_model.bkt import BKTService
from student_model.dkt import DKTService
from orchestration.adaptive_orchestrator import adaptive_orchestrator, AdaptiveLearningState

def test_bkt_service():
    """Test BKT service functionality"""
    print("🧪 Testing BKT Service...")
    
    try:
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        bkt_service = BKTService()
        
        # Test getting BKT parameters
        skill_id = "math_basic"
        bkt_params = bkt_service.get_skill_bkt_params(user, skill_id)
        
        print(f"   ✅ BKT params retrieved for {user.username}:")
        print(f"      Skill: {skill_id}")
        print(f"      P_L (mastery): {bkt_params.P_L:.3f}")
        print(f"      P_T (learning): {bkt_params.P_T:.3f}")
        print(f"      P_G (guess): {bkt_params.P_G:.3f}")
        print(f"      P_S (slip): {bkt_params.P_S:.3f}")
        
        # Test updating BKT
        updated_params, progression_info = bkt_service.update_skill_bkt_with_progression(
            user=user,
            skill_id=skill_id, 
            is_correct=True,
            interaction_data={
                'timestamp': datetime.now().isoformat(),
                'question_id': 'test_question_1'
            }
        )
        
        print(f"   ✅ BKT updated after correct answer:")
        print(f"      New P_L (mastery): {updated_params.P_L:.3f}")
        print(f"      Progression: {progression_info}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ BKT Service failed: {e}")
        return False

def test_dkt_service():
    """Test DKT service functionality"""
    print("\n🧪 Testing DKT Service...")
    
    try:
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        dkt_service = DKTService()
        
        # Test getting DKT state
        dkt_state = dkt_service.get_dkt_state(user)
        
        print(f"   ✅ DKT state retrieved for {user.username}:")
        print(f"      Hidden State Size: {len(dkt_state.hidden_state)}")
        print(f"      Skill Predictions: {len(dkt_state.skill_predictions)}")
        print(f"      Confidence: {dkt_state.confidence:.3f}")
        
        # Test updating DKT
        result = dkt_service.update_dkt_knowledge(
            user=user,
            skill_id="quantitative_aptitude_arithmetic",
            is_correct=True,
            interaction_data={
                'question_id': 'test_question_1',
                'response_time': 15.5
            }
        )
        
        print(f"   ✅ DKT updated after interaction:")
        print(f"      Success: {result.get('success', False)}")
        print(f"      New Prediction: {result.get('prediction', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ DKT Service failed: {e}")
        return False

def test_langgraph_orchestration():
    """Test LangGraph orchestration"""
    print("\n🧪 Testing LangGraph Orchestration...")
    
    try:
        # Get a test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        # Test running adaptive session
        result = adaptive_orchestrator.run_adaptive_session(
            student_id=str(user.id),
            subject="mathematics",
            max_iterations=3  # Small number for testing
        )
        
        print(f"   ✅ LangGraph orchestration completed:")
        print(f"      Success: {result.get('success', False)}")
        print(f"      Student ID: {result.get('student_id')}")
        print(f"      Questions Attempted: {result.get('questions_attempted', 0)}")
        print(f"      Final Skill: {result.get('final_skill')}")
        print(f"      BKT Mastery: {result.get('bkt_mastery', 0):.3f}")
        print(f"      DKT Prediction: {result.get('dkt_prediction', 0):.3f}")
        print(f"      Recommendation: {result.get('recommendation')}")
        
        if result.get('error_message'):
            print(f"      Error: {result.get('error_message')}")
            return False
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"   ❌ LangGraph orchestration failed: {e}")
        return False

def test_state_management():
    """Test AdaptiveLearningState functionality"""
    print("\n🧪 Testing Adaptive Learning State...")
    
    try:
        # Get test user
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        # Create test state
        state = AdaptiveLearningState(
            student_id=str(user.id),
            subject="mathematics",
            skill_id="math_basic",
            max_iterations=5
        )
        
        print(f"   ✅ State created:")
        print(f"      Student ID: {state.student_id}")
        print(f"      Subject: {state.subject}")
        print(f"      Skill ID: {state.skill_id}")
        print(f"      Max Iterations: {state.max_iterations}")
        
        # Test initialization
        orchestrator = adaptive_orchestrator
        state = orchestrator.initialize_session(state)
        
        if hasattr(state, 'error_message') and state.error_message:
            print(f"   ❌ State initialization failed: {state.error_message}")
            return False
            
        print(f"   ✅ State initialized successfully")
        print(f"      User Object: {state.user}")
        print(f"      Session Complete: {getattr(state, 'session_complete', 'Not set')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ State management failed: {e}")
        return False

def diagnose_issues():
    """Diagnose common issues and provide fixes"""
    print("\n🔧 Diagnosing Common Issues...")
    
    issues_found = []
    fixes_applied = []
    
    try:
        # Check if required packages are installed
        try:
            from langgraph.graph import StateGraph, END
            print("   ✅ LangGraph installed and importable")
        except ImportError:
            issues_found.append("LangGraph not installed")
            print("   ❌ LangGraph not installed or not importable")
            
        # Check if core models exist
        try:
            from core.models import StudentProfile
            profile_count = StudentProfile.objects.count()
            print(f"   ✅ StudentProfile model exists ({profile_count} profiles)")
        except Exception as e:
            issues_found.append(f"StudentProfile model issue: {e}")
            
        # Check if BKT/DKT services work
        try:
            bkt_service = BKTService()
            dkt_service = DKTService()
            print("   ✅ BKT and DKT services instantiate correctly")
        except Exception as e:
            issues_found.append(f"BKT/DKT service issue: {e}")
            
        # Check database connectivity
        try:
            user_count = User.objects.count()
            print(f"   ✅ Database connectivity working ({user_count} users)")
        except Exception as e:
            issues_found.append(f"Database connectivity issue: {e}")
            
    except Exception as e:
        issues_found.append(f"General diagnostic error: {e}")
    
    return issues_found, fixes_applied

def fix_common_issues():
    """Apply fixes for common issues"""
    print("\n🔧 Applying Fixes for Common Issues...")
    
    fixes_applied = []
    
    try:
        # Ensure users have StudentProfile
        users_without_profile = User.objects.filter(studentprofile__isnull=True)
        
        if users_without_profile.exists():
            print(f"   🔧 Creating StudentProfile for {users_without_profile.count()} users...")
            
            for user in users_without_profile:
                StudentProfile.objects.get_or_create(
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
            
            fixes_applied.append(f"Created StudentProfile for {users_without_profile.count()} users")
            print(f"   ✅ StudentProfile created for all users")
        else:
            print("   ✅ All users already have StudentProfile")
            
        # Initialize BKT parameters for test
        test_user = User.objects.first()
        if test_user:
            bkt_service = BKTService()
            bkt_params = bkt_service.get_skill_bkt_params(test_user, "test_skill")
            fixes_applied.append("Initialized BKT parameters for test user")
            print("   ✅ BKT parameters initialized for test user")
            
        # Initialize DKT state for test
        if test_user:
            dkt_service = DKTService()
            dkt_state = dkt_service.get_dkt_state(test_user)
            fixes_applied.append("Initialized DKT state for test user")
            print("   ✅ DKT state initialized for test user")
            
    except Exception as e:
        print(f"   ❌ Fix application failed: {e}")
        
    return fixes_applied

def run_comprehensive_test():
    """Run comprehensive test of the entire system"""
    print("🚀 LangGraph Orchestration with BKT/DKT - Comprehensive Test")
    print("=" * 65)
    
    # Diagnose and fix issues
    issues, fixes = diagnose_issues()
    
    if issues:
        print(f"\n⚠️  Issues found: {len(issues)}")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("\n✅ No issues found in initial diagnosis")
    
    # Apply fixes
    fixes = fix_common_issues()
    if fixes:
        print(f"\n🔧 Fixes applied: {len(fixes)}")
        for fix in fixes:
            print(f"   • {fix}")
    
    # Run tests
    print(f"\n" + "=" * 65)
    print("🧪 RUNNING FUNCTIONALITY TESTS")
    print("=" * 65)
    
    test_results = []
    
    # Test 1: BKT Service
    bkt_success = test_bkt_service()
    test_results.append(("BKT Service", bkt_success))
    
    # Test 2: DKT Service
    dkt_success = test_dkt_service()
    test_results.append(("DKT Service", dkt_success))
    
    # Test 3: State Management
    state_success = test_state_management()
    test_results.append(("State Management", state_success))
    
    # Test 4: LangGraph Orchestration
    langgraph_success = test_langgraph_orchestration()
    test_results.append(("LangGraph Orchestration", langgraph_success))
    
    # Print results
    print(f"\n" + "=" * 65)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 65)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your LangGraph orchestration with BKT/DKT is working!")
        print("\n📋 Next Steps:")
        print("   1. Test with real student sessions")
        print("   2. Monitor performance in production")
        print("   3. Adjust BKT/DKT parameters as needed")
    elif passed_tests >= total_tests - 1:
        print("\n⚠️  MOSTLY WORKING: Minor issues to address")
        print("   Most functionality is working, check failed tests above")
    else:
        print("\n❌ MAJOR ISSUES: Multiple components failing")
        print("   Review error messages and fix core issues")
    
    print("=" * 65)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    run_comprehensive_test()