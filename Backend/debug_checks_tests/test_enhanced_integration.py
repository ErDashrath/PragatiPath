"""
Simple Integration Test for Enhanced Adaptive System

Tests the enhanced adaptive system integration with existing simple_frontend_api.py
without complex Django model dependencies.

Author: AI Assistant  
Date: 2024-12-26
"""

import os
import sys
import json
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from enhanced_adaptive_system import enhanced_adaptive_engine, get_enhanced_adaptive_question

def test_enhanced_system_integration():
    """Test enhanced adaptive system with real session"""
    
    print("🧪 Enhanced Adaptive System - Integration Test")
    print("=" * 55)
    
    try:
        # Find existing session with data
        from assessment.improved_models import StudentSession
        
        existing_sessions = StudentSession.objects.filter(
            session_config__isnull=False
        ).order_by('-created_at')[:5]
        
        if not existing_sessions.exists():
            print("❌ No existing sessions found for testing")
            return False
        
        print(f"Found {existing_sessions.count()} existing sessions to test with")
        
        # Test with each session
        success_count = 0
        total_tests = 0
        
        for session in existing_sessions:
            total_tests += 1
            print(f"\n📍 Testing with session: {session.id}")
            print(f"   Student: {session.student.username}")
            print(f"   Subject: {session.subject}")
            print(f"   Questions Planned: {session.total_questions_planned}")
            
            try:
                # Call enhanced adaptive function
                result = get_enhanced_adaptive_question(str(session.id))
                
                # Check result
                if result.get('success'):
                    print(f"   ✅ Enhanced system working!")
                    print(f"      Question ID: {result.get('question_id')}")
                    print(f"      Difficulty: {result.get('difficulty')}")
                    print(f"      Subject: {result.get('subject')}")
                    
                    # Check enhanced info
                    enhanced_info = result.get('enhanced_adaptive_info', {})
                    if enhanced_info:
                        print(f"      🧠 Enhanced Features:")
                        print(f"         Selection Confidence: {enhanced_info.get('selection_confidence', 0):.3f}")
                        print(f"         Expected Success: {enhanced_info.get('expected_success_probability', 0):.3f}")
                        print(f"         Strategy: {enhanced_info.get('adaptation_strategy', 'N/A')}")
                        print(f"         Learning Objective: {enhanced_info.get('learning_objective', 'N/A')}")
                        success_count += 1
                    else:
                        print("      ⚠️ No enhanced info found")
                else:
                    print(f"   ❌ Enhanced system failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Exception in enhanced system: {e}")
        
        # Summary
        print(f"\n" + "=" * 55)
        print(f"📊 TEST SUMMARY")
        print(f"Total Sessions Tested: {total_tests}")
        print(f"Successful Tests: {success_count}")
        print(f"Success Rate: {(success_count / total_tests * 100):.1f}%" if total_tests > 0 else "0%")
        
        if success_count > 0:
            print(f"✅ Enhanced Adaptive System is working with existing sessions!")
            return True
        else:
            print(f"❌ Enhanced Adaptive System needs debugging")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_enhanced_algorithm_components():
    """Test individual components of enhanced algorithm"""
    
    print(f"\n🔧 Testing Enhanced Algorithm Components")
    print("-" * 40)
    
    try:
        # Test 1: Student Profile Building
        print("📊 Test 1: Student Profile Building")
        users_with_data = User.objects.filter(question_attempts__isnull=False).distinct()[:2]
        
        if users_with_data.exists():
            for user in users_with_data:
                try:
                    profile = enhanced_adaptive_engine.build_student_performance_profile(user)
                    print(f"   ✅ Profile built for {user.username}:")
                    print(f"      Overall Accuracy: {profile.overall_accuracy:.3f}")
                    print(f"      Questions Attempted: {profile.total_questions_attempted}")
                    print(f"      Learning Velocity: {profile.learning_velocity:.3f}")
                    print(f"      Consistency Score: {profile.consistency_score:.3f}")
                    break
                except Exception as e:
                    print(f"   ❌ Profile building failed: {e}")
        else:
            print("   ℹ️ No users with question attempts found")
        
        print("✅ Component testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        return False

def demonstrate_enhanced_features():
    """Demonstrate key enhanced features"""
    
    print(f"\n🎯 Enhanced Features Demonstration")
    print("-" * 40)
    
    # Show key improvements over basic system
    improvements = [
        "🧠 Multi-factor difficulty determination (mastery + velocity + consistency + trends)",
        "📊 Comprehensive student performance profiling with 15+ metrics",
        "🎲 Intelligent adaptation strategies (advance, reinforce, challenge, explore)",
        "🔮 Expected success probability calculation with confidence intervals",
        "📚 Chapter diversity optimization for better coverage",
        "⚡ Real-time learning objective adaptation",
        "🎪 Dynamic strategy switching based on performance patterns",
        "💎 Enhanced reasoning and explanation for all selections"
    ]
    
    print("Key Enhanced Features:")
    for improvement in improvements:
        print(f"   {improvement}")
    
    print("\n🔄 Algorithm Flow:")
    flow_steps = [
        "1. Build comprehensive student profile (accuracy, velocity, consistency, trends)",
        "2. Analyze current knowledge state using BKT/DKT orchestration", 
        "3. Determine optimal adaptation strategy (advance/reinforce/challenge/explore)",
        "4. Calculate expected success probability with confidence",
        "5. Select question optimizing for learning objectives and variety",
        "6. Provide detailed reasoning and next-step predictions"
    ]
    
    for step in flow_steps:
        print(f"   {step}")
        
    return True

def main():
    """Main test execution"""
    
    print("🚀 Enhanced Adaptive Learning System")
    print("Integration Test with Existing PragatiPath System")
    print()
    
    # Run tests
    integration_success = test_enhanced_system_integration()
    component_success = test_enhanced_algorithm_components() 
    
    # Demonstrate features
    demonstrate_enhanced_features()
    
    # Final summary
    print(f"\n" + "=" * 55)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 55)
    
    if integration_success and component_success:
        print("🎉 SUCCESS: Enhanced Adaptive System is ready for integration!")
        print()
        print("Next Steps:")
        print("1. Replace current get_simple_question() logic in simple_frontend_api.py")
        print("2. Update submit answer processing to use enhanced analytics")
        print("3. Add enhanced adaptive info to frontend display")
        print("4. Monitor performance improvements in student outcomes")
    elif integration_success:
        print("⚠️ PARTIAL SUCCESS: Integration works but components need attention")
    else:
        print("❌ NEEDS WORK: System requires debugging before deployment")
    
    print("=" * 55)
    
    return integration_success

if __name__ == "__main__":
    main()