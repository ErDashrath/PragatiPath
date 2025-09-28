"""
Test LangGraph Orchestration with Real Database Subjects and Chapters

This script demonstrates how the orchestration now works with:
- Real subjects from SUBJECT_CHOICES 
- Actual chapters with difficulty distributions
- Chapter-specific question selection
- Comprehensive analytics and statistics

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
from django.db.models import Count
from core.models import StudentProfile
from assessment.improved_models import Subject, Chapter, SUBJECT_CHOICES
from assessment.models import AdaptiveQuestion
from orchestration.adaptive_orchestrator import adaptive_orchestrator, AdaptiveLearningState

def show_database_structure():
    """Display the current database structure"""
    print("📊 DATABASE STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Show available subjects
    subjects = Subject.objects.filter(is_active=True)
    print(f"\n🎯 AVAILABLE SUBJECTS ({subjects.count()})")
    for subject in subjects:
        chapters = subject.chapters.filter(is_active=True)
        questions = AdaptiveQuestion.objects.filter(subject=subject.code, is_active=True)  # Fix field name
        
        print(f"   📚 {subject.name} ({subject.code})")
        print(f"      Chapters: {chapters.count()}")
        print(f"      Questions: {questions.count()}")
        
        # Show difficulty distribution for this subject
        if questions.exists():
            difficulty_counts = questions.values('difficulty_level').annotate(count=Count('id'))
            difficulty_dist = {item['difficulty_level']: item['count'] for item in difficulty_counts}
            print(f"      Difficulty Distribution: {difficulty_dist}")
        
        # Show first 3 chapters
        for chapter in chapters[:3]:
            chapter_questions = questions.filter(chapter=chapter)
            print(f"         📖 Chapter {chapter.chapter_number}: {chapter.name} ({chapter_questions.count()} questions)")
        
        if chapters.count() > 3:
            print(f"         ... and {chapters.count() - 3} more chapters")
        print()

def test_subject_specific_session():
    """Test orchestration with specific subject"""
    print("\n🧪 TESTING SUBJECT-SPECIFIC SESSION")
    print("=" * 60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    # Test with Quantitative Aptitude
    subject_code = 'quantitative_aptitude'
    
    result = adaptive_orchestrator.run_adaptive_session(
        student_id=str(user.id),
        subject_code=subject_code,
        max_iterations=3
    )
    
    print(f"📋 SESSION RESULTS:")
    print(f"   Success: {result['success']}")
    print(f"   Subject: {result['subject']['name']} ({result['subject']['code']})")
    print(f"   Questions Attempted: {result['questions_attempted']}")
    print(f"   BKT Mastery: {result['bkt_mastery']:.3f}")
    print(f"   DKT Prediction: {result['dkt_prediction']:.3f}")
    print(f"   Final Difficulty: {result.get('final_difficulty', 'Unknown')}")
    
    if result.get('error_message'):
        print(f"   Error: {result['error_message']}")

def test_chapter_specific_session():
    """Test orchestration with specific chapter"""
    print("\n🧪 TESTING CHAPTER-SPECIFIC SESSION") 
    print("=" * 60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    # Get first chapter of quantitative aptitude
    subject = Subject.objects.filter(code='quantitative_aptitude', is_active=True).first()
    if not subject:
        print("❌ No quantitative_aptitude subject found")
        return
        
    chapter = subject.chapters.filter(is_active=True).first()
    if not chapter:
        print("❌ No chapters found for quantitative_aptitude")
        return
    
    print(f"🎯 Testing with: {subject.name} - {chapter.name}")
    
    # Show chapter question distribution
    chapter_questions = AdaptiveQuestion.objects.filter(
        subject=subject.code,  # Fix field name
        chapter=chapter,
        is_active=True
    )
    
    if chapter_questions.exists():
        difficulty_counts = chapter_questions.values('difficulty_level').annotate(count=Count('id'))
        difficulty_dist = {item['difficulty_level']: item['count'] for item in difficulty_counts}
        print(f"📊 Chapter Question Distribution: {difficulty_dist}")
    
    result = adaptive_orchestrator.run_adaptive_session(
        student_id=str(user.id),
        subject_code=subject.code,
        chapter_id=chapter.id,
        max_iterations=5
    )
    
    print(f"\n📋 CHAPTER SESSION RESULTS:")
    print(f"   Success: {result['success']}")
    print(f"   Subject: {result['subject']['name']}")
    
    if result.get('chapter'):
        chapter_info = result['chapter']
        print(f"   Chapter: {chapter_info['name']} (#{chapter_info['number']})")
        if chapter_info.get('stats'):
            stats = chapter_info['stats']
            print(f"   Chapter Stats:")
            print(f"      Total Questions: {stats['total_questions']}")
            print(f"      Difficulty Breakdown: {stats['difficulty_breakdown']}")
    
    print(f"   Questions Attempted: {result['questions_attempted']}")
    print(f"   BKT Mastery: {result['bkt_mastery']:.3f}")
    print(f"   DKT Prediction: {result['dkt_prediction']:.3f}")
    
    if result.get('error_message'):
        print(f"   Error: {result['error_message']}")

def test_all_subjects():
    """Test orchestration with all available subjects"""
    print("\n🧪 TESTING ALL SUBJECTS")
    print("=" * 60)
    
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    subjects = Subject.objects.filter(is_active=True)
    
    for subject in subjects:
        print(f"\n🎯 Testing {subject.name} ({subject.code})")
        
        result = adaptive_orchestrator.run_adaptive_session(
            student_id=str(user.id),
            subject_code=subject.code,
            max_iterations=2
        )
        
        if result['success']:
            print(f"   ✅ Success - BKT: {result['bkt_mastery']:.3f}, DKT: {result['dkt_prediction']:.3f}")
        else:
            print(f"   ❌ Failed - {result.get('error_message', 'Unknown error')}")

def show_orchestration_features():
    """Show the enhanced features of the updated orchestration"""
    print("\n🌟 ENHANCED ORCHESTRATION FEATURES")
    print("=" * 60)
    
    print("✅ Real Database Integration:")
    print("   • Uses actual Subject and Chapter models")
    print("   • Validates subject_code against SUBJECT_CHOICES") 
    print("   • Validates chapter_id against Chapter table")
    print("   • Provides comprehensive error messages")
    
    print("\n✅ Intelligent Question Selection:")
    print("   • Filters questions by real subject_code")
    print("   • Chapter-specific filtering when chapter_id provided") 
    print("   • Fallback to subject-wide questions if chapter empty")
    print("   • Uses real difficulty levels: easy, moderate, difficult")
    
    print("\n✅ Enhanced Analytics:")
    print("   • Subject information with ID and name")
    print("   • Chapter information with number and name")
    print("   • Difficulty distribution statistics")
    print("   • Question count per chapter")
    print("   • Comprehensive session metadata")
    
    print("\n✅ Adaptive Algorithm Integration:")
    print("   • BKT with skill_id based on subject_code + chapter")
    print("   • DKT predictions for real skills")
    print("   • Combined mastery assessment")
    print("   • Dynamic difficulty adjustment")
    
    print("\n✅ Error Handling & Validation:")
    print("   • Subject existence validation") 
    print("   • Chapter-subject relationship validation")
    print("   • Graceful fallbacks when no questions found")
    print("   • Detailed error messages for debugging")

def run_comprehensive_demo():
    """Run comprehensive demonstration"""
    print("🚀 LANGGRAPH ORCHESTRATION WITH REAL DATABASE")
    print("🔗 Integration with Subjects, Chapters & Question Analytics")
    print("=" * 80)
    
    # Show database structure
    show_database_structure()
    
    # Show enhanced features
    show_orchestration_features()
    
    # Test subject-specific session
    test_subject_specific_session()
    
    # Test chapter-specific session  
    test_chapter_specific_session()
    
    # Test all subjects
    test_all_subjects()
    
    print("\n" + "=" * 80)
    print("🎉 DEMO COMPLETE!")
    print("📋 Your LangGraph orchestration now works with:")
    print("   • Real database subjects and chapters")
    print("   • Actual question difficulty distributions") 
    print("   • Chapter-specific analytics")
    print("   • Enhanced BKT/DKT integration")
    print("   • Comprehensive error handling")
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_demo()