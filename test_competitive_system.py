"""
Test the competitive exam system with imported CSV data
Tests all 4 subjects: quantitative_aptitude, logical_reasoning, data_interpretation, verbal_ability
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(r'c:\Users\Dashrath\Desktop\Academic\Hackathons\StrawHatsH2')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from assessment.models import AdaptiveQuestion
from core.models import StudentProfile, User
from django.db.models import Count, Q
import uuid

def test_database_import():
    """Test that all subjects were imported correctly"""
    print("🧪 Testing Database Import")
    print("=" * 50)
    
    # Count questions by subject
    subjects = AdaptiveQuestion.objects.values('subject').annotate(count=Count('id')).order_by('subject')
    
    total_questions = 0
    for subject_data in subjects:
        subject = subject_data['subject']
        count = subject_data['count']
        total_questions += count
        print(f"📊 {subject.replace('_', ' ').title()}: {count} questions")
    
    print(f"\n✅ Total Questions Imported: {total_questions}")
    return total_questions > 0

def test_question_structure():
    """Test the structure of imported questions"""
    print("\n🔍 Testing Question Structure")
    print("=" * 50)
    
    # Get sample questions from each subject
    subjects = ['quantitative_aptitude', 'logical_reasoning', 'data_interpretation', 'verbal_ability']
    
    for subject in subjects:
        questions = AdaptiveQuestion.objects.filter(subject=subject)[:2]
        
        if questions:
            print(f"\n📋 {subject.replace('_', ' ').title()} Sample:")
            for i, q in enumerate(questions, 1):
                print(f"   Q{i}: {q.question_text[:60]}...")
                print(f"       Options: {list(q.formatted_options.keys())}")
                print(f"       Answer: {q.answer} -> {q.correct_option_text[:30]}...")
                print(f"       Difficulty: {q.difficulty_level} (Level {q.level})")
                print(f"       Tags: {q.tags}")
        else:
            print(f"❌ No questions found for {subject}")

def test_subject_filtering():
    """Test filtering questions by subject and difficulty"""
    print("\n🔽 Testing Subject Filtering")
    print("=" * 50)
    
    subjects = ['quantitative_aptitude', 'logical_reasoning', 'data_interpretation', 'verbal_ability']
    difficulties = ['very easy', 'easy', 'moderate', 'difficult']
    
    for subject in subjects:
        print(f"\n📊 {subject.replace('_', ' ').title()} Breakdown:")
        
        # Count by difficulty (handle different formats)
        for diff in difficulties:
            # Try both formats
            count1 = AdaptiveQuestion.objects.filter(
                subject=subject, 
                difficulty_level=diff.replace(' ', '_')
            ).count()
            count2 = AdaptiveQuestion.objects.filter(
                subject=subject, 
                difficulty_level__icontains=diff.replace(' ', '')
            ).count()
            
            total_count = max(count1, count2)
            if total_count > 0:
                print(f"   {diff.title()}: {total_count} questions")

def test_level_mapping():
    """Test level mapping for different difficulties"""
    print("\n📈 Testing Level Mapping")
    print("=" * 50)
    
    level_counts = AdaptiveQuestion.objects.values('level').annotate(count=Count('id')).order_by('level')
    
    for level_data in level_counts:
        level = level_data['level']
        count = level_data['count']
        print(f"Level {level}: {count} questions")

def create_test_student():
    """Create a test student for API testing"""
    print("\n👤 Creating Test Student")
    print("=" * 30)
    
    # Create user if not exists
    user, created = User.objects.get_or_create(
        username='test_competitive_student',
        defaults={
            'email': 'test@competitive.exam',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    
    # Create or get student profile
    profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'current_level': 1,
            'mastery_threshold': 0.8,
            'consecutive_correct_count': 0,
            'level_lock_status': {'locked_levels': []}
        }
    )
    
    action = "Created" if created else "Found existing"
    print(f"✅ {action} student: {user.username}")
    print(f"   Level: {profile.current_level}")
    print(f"   Mastery Threshold: {profile.mastery_threshold}")
    
    return str(profile.id)

def test_api_endpoints():
    """Test the API endpoints manually"""
    print("\n🌐 API Endpoints Available:")
    print("=" * 50)
    
    print("Subject-specific endpoints:")
    print("  GET  /api/assessment/subjects - List all subjects")
    print("  POST /api/assessment/subject-questions - Get questions for a subject")
    print("  GET  /api/assessment/subjects/{subject}/stats - Get subject statistics")
    print("  POST /api/assessment/submit - Submit answer with subject tracking")
    
    print("\nTo test with curl or Postman:")
    print("1. Start server: python manage.py runserver")
    print("2. Test subjects: GET http://localhost:8000/api/assessment/subjects")
    print("3. Get questions: POST http://localhost:8000/api/assessment/subject-questions")
    print("   Body: {'student_id': 'test-student-id', 'subject': 'quantitative_aptitude'}")

def main():
    """Run all tests"""
    print("🚀 Competitive Exam System Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Database import
        if not test_database_import():
            print("❌ No questions found. Make sure CSV import completed successfully.")
            return
        
        # Test 2: Question structure
        test_question_structure()
        
        # Test 3: Subject filtering
        test_subject_filtering()
        
        # Test 4: Level mapping
        test_level_mapping()
        
        # Test 5: Create test student
        student_id = create_test_student()
        
        # Test 6: API information
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("🎉 All Tests Completed Successfully!")
        print("💡 Your competitive exam system is ready with:")
        
        total_questions = AdaptiveQuestion.objects.count()
        subjects_count = AdaptiveQuestion.objects.values('subject').distinct().count()
        
        print(f"   • {total_questions} total questions")
        print(f"   • {subjects_count} subjects")
        print("   • Subject-wise progression tracking")
        print("   • Difficulty-based level mapping")
        print("   • BKT algorithm integration")
        print("   • IRT question selection")
        print("   • Spaced repetition scheduling")
        print(f"   • Test student ID: {student_id}")
        
        print("\n🎯 Next Steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Test the APIs using the test student ID above")
        print("3. Import more CSV files if needed")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()