"""
Direct Test of Orchestration Components (Without LangGraph)

This script tests the individual orchestration methods directly to isolate issues.
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
from orchestration.adaptive_orchestrator import AdaptiveLearningOrchestrator, AdaptiveLearningState

def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print("🧪 TESTING ORCHESTRATOR INITIALIZATION")
    print("=" * 50)
    
    try:
        orchestrator = AdaptiveLearningOrchestrator()
        print("✅ Orchestrator initialized successfully")
        print(f"   BKT Service: {orchestrator.bkt_service}")
        print(f"   DKT Service: {orchestrator.dkt_service}")
        print(f"   Workflow: {orchestrator.workflow}")
        return True, orchestrator
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False, None

def test_individual_methods(orchestrator):
    """Test individual orchestrator methods"""
    print("\n🧪 TESTING INDIVIDUAL METHODS")
    print("=" * 50)
    
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found")
            return False
            
        # Create test state
        state = AdaptiveLearningState(
            student_id=str(user.id),
            subject_code='quantitative_aptitude',
            max_iterations=5
        )
        
        print(f"📋 Initial state: {state.student_id}, {state.subject_code}")
        
        # Test initialize_session
        print("\n1️⃣ Testing initialize_session...")
        state = orchestrator.initialize_session(state)
        
        if state.error_message:
            print(f"❌ Initialize session failed: {state.error_message}")
            return False
        else:
            print(f"✅ Session initialized:")
            print(f"   User: {state.user.username if state.user else 'None'}")
            print(f"   Subject: {state.subject_obj.name if state.subject_obj else 'None'}")
            print(f"   Chapter: {state.chapter_obj.name if state.chapter_obj else 'None'}")
            print(f"   Skill ID: {state.skill_id}")
        
        # Test analyze_knowledge_state
        print("\n2️⃣ Testing analyze_knowledge_state...")
        state = orchestrator.analyze_knowledge_state(state)
        
        if state.error_message:
            print(f"❌ Analyze knowledge failed: {state.error_message}")
            return False
        else:
            print(f"✅ Knowledge analyzed:")
            print(f"   BKT State: {state.bkt_state}")
            print(f"   DKT State: {state.dkt_state}")
        
        # Test select_question
        print("\n3️⃣ Testing select_question...")
        state = orchestrator.select_question(state)
        
        if state.error_message:
            print(f"❌ Question selection failed: {state.error_message}")
            return False
        else:
            print(f"✅ Question selected:")
            if state.current_question:
                print(f"   ID: {state.current_question['id']}")
                print(f"   Subject: {state.current_question.get('subject_name', 'Unknown')}")
                print(f"   Chapter: {state.current_question.get('chapter_name', 'Unknown')}")
                print(f"   Difficulty: {state.current_question.get('difficulty', 'Unknown')}")
                print(f"   Text: {state.current_question.get('text', '')[:100]}...")
            else:
                print("   No question selected")
        
        print("\n✅ All individual methods working!")
        return True
        
    except Exception as e:
        print(f"❌ Individual methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_queries():
    """Test direct database queries"""
    print("\n🧪 TESTING DATABASE QUERIES")
    print("=" * 50)
    
    try:
        # Test subject query
        subject = Subject.objects.filter(code='quantitative_aptitude', is_active=True).first()
        if subject:
            print(f"✅ Subject found: {subject.name}")
        else:
            print("❌ Subject not found")
            return False
        
        # Test questions query
        questions = AdaptiveQuestion.objects.filter(
            subject='quantitative_aptitude',
            difficulty_level='moderate',
            is_active=True
        )
        
        print(f"✅ Found {questions.count()} moderate questions in quantitative_aptitude")
        
        if questions.exists():
            q = questions.first()
            print(f"   Sample question: {q.question_text[:100]}...")
            print(f"   Difficulty: {q.difficulty_level}")
            print(f"   Answer: {q.answer}")
            print(f"   Chapter: {q.chapter.name if q.chapter else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database queries failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_direct_test():
    """Run direct component test"""
    print("🚀 DIRECT ORCHESTRATION COMPONENT TEST")
    print("🔧 Testing without LangGraph to isolate issues")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Orchestrator initialization
    success, orchestrator = test_orchestrator_initialization()
    if success:
        tests_passed += 1
    
    # Test 2: Database queries
    if test_database_queries():
        tests_passed += 1
    
    # Test 3: Individual methods (only if orchestrator initialized)
    if orchestrator and test_individual_methods(orchestrator):
        tests_passed += 1
    
    # Test 4: Try a complete workflow manually
    print("\n🧪 TESTING MANUAL WORKFLOW")
    print("=" * 50)
    
    if orchestrator:
        try:
            user = User.objects.first()
            
            # Ensure user has profile
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bkt_parameters': {},
                    'dkt_hidden_state': [],
                    'fundamentals': {'listening': 0.5, 'grasping': 0.5, 'retention': 0.5, 'application': 0.5},
                    'interaction_history': []
                }
            )
            
            state = AdaptiveLearningState(
                student_id=str(user.id),
                subject_code='quantitative_aptitude',
                max_iterations=2
            )
            
            # Manual workflow
            state = orchestrator.initialize_session(state)
            if not state.error_message:
                state = orchestrator.analyze_knowledge_state(state)
                if not state.error_message:
                    state = orchestrator.select_question(state)
                    if not state.error_message and state.current_question:
                        print("✅ Manual workflow completed successfully!")
                        print(f"   Selected question from: {state.current_question.get('chapter_name', 'Unknown chapter')}")
                        tests_passed += 1
                    else:
                        print(f"❌ Question selection failed: {state.error_message}")
                else:
                    print(f"❌ Knowledge analysis failed: {state.error_message}")
            else:
                print(f"❌ Session initialization failed: {state.error_message}")
        
        except Exception as e:
            print(f"❌ Manual workflow failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎉 ALL CORE COMPONENTS WORKING!")
        print("💡 The issue is likely with LangGraph integration, not the core logic")
    elif tests_passed >= total_tests - 1:
        print("⚠️ MOSTLY WORKING: Minor issues")
    else:
        print("❌ MAJOR ISSUES: Core components failing")
    
    print("=" * 60)

if __name__ == "__main__":
    run_direct_test()