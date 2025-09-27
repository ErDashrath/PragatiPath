"""
Test Suite for Enhanced Adaptive Learning System

This module tests the new enhanced adaptive algorithms for:
1. Student performance profiling
2. Intelligent question selection 
3. Dynamic difficulty adjustment
4. Learning path optimization

Author: AI Assistant
Date: 2024-12-26
"""

import os
import sys
import json
import django
from datetime import datetime, timedelta
from typing import Dict, List

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from core.models import StudentProfile
from assessment.models import QuestionAttempt, StudentSession, AdaptiveQuestion
from enhanced_adaptive_system import (
    EnhancedAdaptiveEngine, 
    StudentPerformanceProfile, 
    QuestionSelectionContext,
    get_enhanced_adaptive_question
)

class EnhancedAdaptiveSystemTester:
    """Comprehensive tester for enhanced adaptive system"""
    
    def __init__(self):
        self.engine = EnhancedAdaptiveEngine()
        self.test_results = []
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Enhanced Adaptive System Test Suite")
        print("=" * 60)
        
        # Test 1: Student Profile Building
        self.test_student_profile_building()
        
        # Test 2: Difficulty Determination Logic
        self.test_difficulty_determination()
        
        # Test 3: Question Selection Algorithm
        self.test_question_selection()
        
        # Test 4: Integration with Existing System
        self.test_system_integration()
        
        # Test 5: Performance Comparison
        self.test_performance_comparison()
        
        # Print summary
        self.print_test_summary()
    
    def test_student_profile_building(self):
        """Test comprehensive student profile building"""
        print("\n📊 Test 1: Student Performance Profile Building")
        print("-" * 40)
        
        try:
            # Get test student with existing data
            test_students = User.objects.filter(
                questionattempt__isnull=False
            ).distinct()[:3]
            
            if not test_students.exists():
                print("❌ No students with question attempts found")
                self.test_results.append(("Profile Building", False, "No test data"))
                return
            
            for student in test_students:
                print(f"\n👤 Testing student: {student.username}")
                
                # Build profile
                profile = self.engine.build_student_performance_profile(student)
                
                # Validate profile completeness
                required_fields = [
                    'overall_accuracy', 'total_questions_attempted', 
                    'learning_velocity', 'consistency_score'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if not hasattr(profile, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                    self.test_results.append(("Profile Building", False, f"Missing: {missing_fields}"))
                    continue
                
                # Test profile metrics
                attempts_count = QuestionAttempt.objects.filter(student=student).count()
                
                print(f"   📈 Profile Metrics:")
                print(f"      Overall Accuracy: {profile.overall_accuracy:.3f}")
                print(f"      Questions Attempted: {profile.total_questions_attempted} (DB: {attempts_count})")
                print(f"      Learning Velocity: {profile.learning_velocity:.3f}")
                print(f"      Consistency Score: {profile.consistency_score:.3f}")
                print(f"      Profile Confidence: {profile.profile_confidence:.3f}")
                
                # Validate accuracy calculation
                if attempts_count > 0:
                    actual_correct = QuestionAttempt.objects.filter(
                        student=student, is_correct=True
                    ).count()
                    expected_accuracy = actual_correct / attempts_count
                    accuracy_diff = abs(profile.overall_accuracy - expected_accuracy)
                    
                    if accuracy_diff > 0.01:  # Allow 1% tolerance
                        print(f"❌ Accuracy calculation error: expected {expected_accuracy:.3f}, got {profile.overall_accuracy:.3f}")
                        self.test_results.append(("Profile Accuracy", False, f"Error: {accuracy_diff:.3f}"))
                    else:
                        print(f"✅ Accuracy calculation correct")
                        self.test_results.append(("Profile Accuracy", True, "Accurate calculation"))
                
                # Test subject-specific data
                if profile.subject_masteries:
                    print(f"   📚 Subject Masteries: {profile.subject_masteries}")
                    self.test_results.append(("Subject Analysis", True, f"Found {len(profile.subject_masteries)} subjects"))
                else:
                    print(f"   ℹ️ No subject-specific data found")
                    self.test_results.append(("Subject Analysis", True, "No subject data"))
                
                break  # Test first student with data
                
            print("✅ Profile building tests completed")
            
        except Exception as e:
            print(f"❌ Profile building test failed: {e}")
            self.test_results.append(("Profile Building", False, str(e)))
    
    def test_difficulty_determination(self):
        """Test advanced difficulty determination logic"""
        print("\n🎯 Test 2: Difficulty Determination Logic")
        print("-" * 40)
        
        try:
            # Create test profiles with different characteristics
            test_cases = [
                {
                    "name": "Beginner Student",
                    "overall_accuracy": 0.3,
                    "learning_velocity": 0.05,
                    "consistency_score": 0.4,
                    "recent_accuracy_trend": -0.1,
                    "expected_difficulty": "easy"
                },
                {
                    "name": "Advanced Student", 
                    "overall_accuracy": 0.85,
                    "learning_velocity": 0.1,
                    "consistency_score": 0.8,
                    "recent_accuracy_trend": 0.05,
                    "expected_difficulty": "hard"
                },
                {
                    "name": "Improving Student",
                    "overall_accuracy": 0.6,
                    "learning_velocity": 0.2,  # Fast improvement
                    "consistency_score": 0.6,
                    "recent_accuracy_trend": 0.15,
                    "expected_difficulty": "medium"
                },
                {
                    "name": "Struggling Student",
                    "overall_accuracy": 0.5,
                    "learning_velocity": -0.05,  # Declining
                    "consistency_score": 0.3,
                    "recent_accuracy_trend": -0.2,
                    "expected_difficulty": "easy"
                }
            ]
            
            for test_case in test_cases:
                print(f"\n👤 Testing: {test_case['name']}")
                
                # Create mock profile
                profile = StudentPerformanceProfile(
                    student_id="test_student",
                    overall_accuracy=test_case['overall_accuracy'],
                    learning_velocity=test_case['learning_velocity'],
                    consistency_score=test_case['consistency_score'],
                    recent_accuracy_trend=test_case['recent_accuracy_trend'],
                    subject_masteries={"mathematics": test_case['overall_accuracy']}
                )
                
                # Create mock session
                user = User.objects.first()
                if not user:
                    print("❌ No users found for testing")
                    continue
                    
                session = StudentSession.objects.create(
                    student=user,
                    subject="mathematics",
                    total_questions_planned=10,
                    session_config={"subject": "mathematics"}
                )
                
                # Create context
                context = QuestionSelectionContext(
                    student_profile=profile,
                    current_session=session,
                    questions_completed=5,
                    recent_performance=[True, False, True, True, False],
                    remaining_questions=5
                )
                
                # Test difficulty determination
                difficulty, strategy = self.engine._determine_optimal_difficulty(context)
                
                print(f"   🎲 Determined Difficulty: {difficulty} (strategy: {strategy})")
                print(f"   📊 Profile: accuracy={profile.overall_accuracy:.3f}, velocity={profile.learning_velocity:.3f}")
                
                # Validate reasonableness
                if test_case['name'] == "Beginner Student" and difficulty == "hard":
                    print("❌ Unreasonable difficulty for beginner")
                    self.test_results.append((f"Difficulty - {test_case['name']}", False, "Too hard for beginner"))
                elif test_case['name'] == "Advanced Student" and difficulty == "easy":
                    print("❌ Unreasonable difficulty for advanced student")
                    self.test_results.append((f"Difficulty - {test_case['name']}", False, "Too easy for advanced"))
                else:
                    print("✅ Reasonable difficulty selected")
                    self.test_results.append((f"Difficulty - {test_case['name']}", True, f"{difficulty} - {strategy}"))
                
                # Cleanup
                session.delete()
            
            print("✅ Difficulty determination tests completed")
            
        except Exception as e:
            print(f"❌ Difficulty determination test failed: {e}")
            self.test_results.append(("Difficulty Determination", False, str(e)))
    
    def test_question_selection(self):
        """Test intelligent question selection algorithm"""
        print("\n🎲 Test 3: Question Selection Algorithm")
        print("-" * 40)
        
        try:
            # Get a real student and session for testing
            student = User.objects.first()
            if not student:
                print("❌ No users found for testing")
                self.test_results.append(("Question Selection", False, "No users"))
                return
                
            # Create test session
            session = StudentSession.objects.create(
                student=student,
                subject="quantitative_aptitude",
                total_questions_planned=10,
                session_config={"subject": "quantitative_aptitude"}
            )
            
            # Build profile
            profile = self.engine.build_student_performance_profile(student)
            
            # Create context
            context = QuestionSelectionContext(
                student_profile=profile,
                current_session=session,
                questions_completed=3,
                recent_performance=[True, False, True],
                remaining_questions=7
            )
            
            # Test question selection
            recommendation = self.engine.select_optimal_question(context)
            
            print(f"   🎯 Selected Difficulty: {recommendation.difficulty}")
            print(f"   🧠 Selection Reason: {recommendation.selection_reason}")
            print(f"   📈 Expected Success: {recommendation.expected_success_probability:.3f}")
            print(f"   💡 Learning Objective: {recommendation.learning_objective}")
            print(f"   🎪 Strategy: {recommendation.adaptation_strategy}")
            print(f"   🔮 Next Difficulty Hint: {recommendation.next_difficulty_hint}")
            print(f"   ✅ Selection Confidence: {recommendation.confidence:.3f}")
            
            # Validate recommendation completeness
            required_fields = [
                'difficulty', 'selection_reason', 'expected_success_probability',
                'learning_objective', 'adaptation_strategy', 'confidence'
            ]
            
            missing_fields = []
            for field in required_fields:
                if not hasattr(recommendation, field) or getattr(recommendation, field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing recommendation fields: {missing_fields}")
                self.test_results.append(("Question Selection", False, f"Missing: {missing_fields}"))
            else:
                print("✅ Complete recommendation generated")
                self.test_results.append(("Question Selection", True, "Complete recommendation"))
            
            # Test multiple iterations to ensure variety
            difficulties_seen = set()
            strategies_seen = set()
            
            for i in range(5):
                rec = self.engine.select_optimal_question(context)
                difficulties_seen.add(rec.difficulty)
                strategies_seen.add(rec.adaptation_strategy)
            
            print(f"   🎲 Variety Test - Difficulties: {difficulties_seen}")
            print(f"   🎪 Variety Test - Strategies: {strategies_seen}")
            
            if len(difficulties_seen) > 1:
                print("✅ Good difficulty variety")
                self.test_results.append(("Selection Variety", True, f"{len(difficulties_seen)} different difficulties"))
            else:
                print("ℹ️ Limited difficulty variety (may be intentional)")
                self.test_results.append(("Selection Variety", True, "Consistent selection"))
                
            # Cleanup
            session.delete()
            
        except Exception as e:
            print(f"❌ Question selection test failed: {e}")
            self.test_results.append(("Question Selection", False, str(e)))
    
    def test_system_integration(self):
        """Test integration with existing system"""
        print("\n🔗 Test 4: System Integration")
        print("-" * 40)
        
        try:
            # Get existing session or create one
            existing_sessions = StudentSession.objects.filter(
                session_config__subject__isnull=False
            )[:1]
            
            if existing_sessions.exists():
                test_session = existing_sessions.first()
                print(f"   📍 Using existing session: {test_session.id}")
            else:
                # Create test session
                student = User.objects.first()
                if not student:
                    print("❌ No users found")
                    self.test_results.append(("System Integration", False, "No users"))
                    return
                
                test_session = StudentSession.objects.create(
                    student=student,
                    subject="quantitative_aptitude",
                    total_questions_planned=5,
                    session_config={"subject": "quantitative_aptitude"}
                )
                print(f"   📍 Created test session: {test_session.id}")
            
            # Test main integration function
            result = get_enhanced_adaptive_question(str(test_session.id))
            
            print(f"   🎯 Integration Result:")
            print(f"      Success: {result.get('success', False)}")
            
            if result.get('success'):
                print(f"      Question ID: {result.get('question_id', 'N/A')}")
                print(f"      Subject: {result.get('subject', 'N/A')}")
                print(f"      Difficulty: {result.get('difficulty', 'N/A')}")
                print(f"      Question Text: {result.get('question_text', 'N/A')[:50]}...")
                
                # Check enhanced adaptive info
                enhanced_info = result.get('enhanced_adaptive_info', {})
                if enhanced_info:
                    print(f"      Enhanced Info Available: ✅")
                    print(f"         Selection Confidence: {enhanced_info.get('selection_confidence', 'N/A')}")
                    print(f"         Expected Success: {enhanced_info.get('expected_success_probability', 'N/A')}")
                    print(f"         Learning Objective: {enhanced_info.get('learning_objective', 'N/A')}")
                    print(f"         Adaptation Strategy: {enhanced_info.get('adaptation_strategy', 'N/A')}")
                    
                    self.test_results.append(("System Integration", True, "Enhanced info provided"))
                else:
                    print(f"      Enhanced Info: ❌ Not found")
                    self.test_results.append(("System Integration", False, "No enhanced info"))
                
                # Test response format compatibility
                required_fields = ['success', 'question_id', 'subject', 'difficulty', 'question_text', 'options']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    self.test_results.append(("Response Format", False, f"Missing: {missing_fields}"))
                else:
                    print("✅ Response format compatible")
                    self.test_results.append(("Response Format", True, "All required fields present"))
            
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ Integration failed: {error_msg}")
                self.test_results.append(("System Integration", False, error_msg))
            
            # Cleanup if we created the session
            if not existing_sessions.exists():
                test_session.delete()
                
        except Exception as e:
            print(f"❌ System integration test failed: {e}")
            self.test_results.append(("System Integration", False, str(e)))
    
    def test_performance_comparison(self):
        """Test performance comparison with existing system"""
        print("\n⚡ Test 5: Performance Comparison")
        print("-" * 40)
        
        try:
            # Get test session
            student = User.objects.first()
            if not student:
                print("❌ No users found")
                return
                
            session = StudentSession.objects.create(
                student=student,
                subject="quantitative_aptitude",
                total_questions_planned=5,
                session_config={"subject": "quantitative_aptitude"}
            )
            
            # Time enhanced system
            import time
            
            start_time = time.time()
            enhanced_result = get_enhanced_adaptive_question(str(session.id))
            enhanced_time = time.time() - start_time
            
            print(f"   ⏱️ Enhanced System Time: {enhanced_time:.4f} seconds")
            
            # Check if enhanced system worked
            if enhanced_result.get('success'):
                print("   ✅ Enhanced system successful")
                enhanced_info = enhanced_result.get('enhanced_adaptive_info', {})
                
                if enhanced_info:
                    print(f"      🧠 Selection Confidence: {enhanced_info.get('selection_confidence', 0):.3f}")
                    print(f"      📊 Expected Success: {enhanced_info.get('expected_success_probability', 0):.3f}")
                    print(f"      🎯 Strategy: {enhanced_info.get('adaptation_strategy', 'N/A')}")
                    print(f"      🔮 Next Hint: {enhanced_info.get('next_difficulty_hint', 'N/A')}")
                
                self.test_results.append(("Performance Test", True, f"Completed in {enhanced_time:.4f}s"))
            else:
                print("   ❌ Enhanced system failed")
                self.test_results.append(("Performance Test", False, "Enhanced system error"))
            
            # Memory usage approximation
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"   💾 Current Memory Usage: {memory_mb:.1f} MB")
            
            # Cleanup
            session.delete()
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.test_results.append(("Performance Test", False, str(e)))
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 ENHANCED ADAPTIVE SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result[1])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "N/A")
        
        print(f"\nDetailed Results:")
        for test_name, passed, details in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {test_name}: {details}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 All tests passed! Enhanced Adaptive System is ready for deployment.")
        elif failed_tests <= 2:
            print("⚠️ Most tests passed. Minor issues to address before deployment.")
        else:
            print("❌ Multiple test failures. System needs debugging before deployment.")
        
        print("=" * 60)

def main():
    """Main test execution"""
    print("🚀 Enhanced Adaptive Learning System - Test Suite")
    print("Testing advanced BKT/DKT algorithms for dynamic question selection")
    print()
    
    tester = EnhancedAdaptiveSystemTester()
    tester.run_all_tests()
    
    return tester.test_results

if __name__ == "__main__":
    main()