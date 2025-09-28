"""
Setup test data for enhanced adaptive learning system
Run: python setup_test_data.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.improved_models import Subject, Chapter, StudentMastery, StudentSession
from assessment.models import AdaptiveQuestion

def setup_test_data():
    """Create test data for adaptive learning system"""
    
    print("🔧 Setting up test data for Enhanced Adaptive Learning System")
    print("=" * 60)
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.username} (ID: {user.id})")
    else:
        print(f"✅ Using existing user: {user.username} (ID: {user.id})")
    
    # Create test subjects
    subjects_data = [
        {'name': 'Mathematics', 'code': 'MATH', 'description': 'Mathematical concepts and problem solving'},
        {'name': 'Science', 'code': 'SCI', 'description': 'Scientific principles and applications'},
        {'name': 'English', 'code': 'ENG', 'description': 'English language and literature'},
    ]
    
    subjects_created = []
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults=subject_data
        )
        subjects_created.append(subject)
        if created:
            print(f"✅ Created subject: {subject.name} (ID: {subject.id})")
        else:
            print(f"✅ Using existing subject: {subject.name} (ID: {subject.id})")
    
    # Create test chapters
    chapters_data = [
        {'subject': subjects_created[0], 'name': 'Algebra', 'chapter_number': 1},
        {'subject': subjects_created[0], 'name': 'Geometry', 'chapter_number': 2},
        {'subject': subjects_created[1], 'name': 'Physics', 'chapter_number': 1},
        {'subject': subjects_created[1], 'name': 'Chemistry', 'chapter_number': 2},
        {'subject': subjects_created[2], 'name': 'Grammar', 'chapter_number': 1},
        {'subject': subjects_created[2], 'name': 'Literature', 'chapter_number': 2},
    ]
    
    chapters_created = []
    for chapter_data in chapters_data:
        chapter, created = Chapter.objects.get_or_create(
            subject=chapter_data['subject'],
            chapter_number=chapter_data['chapter_number'],
            defaults={'name': chapter_data['name']}
        )
        chapters_created.append(chapter)
        if created:
            print(f"✅ Created chapter: {chapter.name} (ID: {chapter.id})")
        else:
            print(f"✅ Using existing chapter: {chapter.name} (ID: {chapter.id})")
    
    # Create test questions
    questions_data = [
        {
            'question_text': 'What is 2 + 2?',
            'option_a': '3',
            'option_b': '4', 
            'option_c': '5',
            'option_d': '6',
            'answer': 'b',
            'difficulty_level': 'easy',
            'subject': 'quantitative_aptitude',
            'subject_fk': subjects_created[0],
            'chapter': chapters_created[0]
        },
        {
            'question_text': 'What is 5 × 7?',
            'option_a': '32',
            'option_b': '35',
            'option_c': '38', 
            'option_d': '40',
            'answer': 'b',
            'difficulty_level': 'moderate',
            'subject': 'quantitative_aptitude',
            'subject_fk': subjects_created[0],
            'chapter': chapters_created[0]
        },
        {
            'question_text': 'What is the area of a circle with radius 5?',
            'option_a': '25π',
            'option_b': '50π',
            'option_c': '10π',
            'option_d': '15π',
            'answer': 'a',
            'difficulty_level': 'moderate',
            'subject': 'quantitative_aptitude',
            'subject_fk': subjects_created[0],
            'chapter': chapters_created[1]
        },
        {
            'question_text': 'What is the capital of France?',
            'option_a': 'London',
            'option_b': 'Berlin',
            'option_c': 'Paris',
            'option_d': 'Madrid',
            'answer': 'c',
            'difficulty_level': 'easy',
            'subject': 'verbal_ability',
            'subject_fk': subjects_created[2],
            'chapter': chapters_created[4]
        },
        {
            'question_text': 'Which element has the chemical symbol "H"?',
            'option_a': 'Helium',
            'option_b': 'Hydrogen',
            'option_c': 'Hafnium',
            'option_d': 'Hassium',
            'answer': 'b',
            'difficulty_level': 'easy',
            'subject': 'logical_reasoning',
            'subject_fk': subjects_created[1],
            'chapter': chapters_created[3]
        }
    ]
    
    questions_created = 0
    for question_data in questions_data:
        question, created = AdaptiveQuestion.objects.get_or_create(
            question_text=question_data['question_text'],
            defaults=question_data
        )
        if created:
            questions_created += 1
            print(f"✅ Created question: {question.question_text[:50]}...")
        else:
            print(f"✅ Using existing question: {question.question_text[:50]}...")
    
    print(f"\n📊 Summary:")
    print(f"Users: {User.objects.count()}")
    print(f"Subjects: {Subject.objects.count()}")
    print(f"Chapters: {Chapter.objects.count()}")
    print(f"Questions: {AdaptiveQuestion.objects.count()}")
    print(f"New questions created: {questions_created}")
    
    # Display test IDs for API testing
    print(f"\n🧪 Test Data for API:")
    print(f"User ID: {user.id}")
    print(f"Subject IDs: {[s.id for s in subjects_created[:3]]}")
    print(f"Chapter IDs: {[c.id for c in chapters_created[:3]]}")
    
    return {
        'user_id': user.id,
        'subject_ids': [s.id for s in subjects_created],
        'chapter_ids': [c.id for c in chapters_created]
    }

if __name__ == "__main__":
    try:
        test_data = setup_test_data()
        print(f"\n🎉 Test data setup complete!")
        print(f"Ready to test adaptive learning API with:")
        print(f"- User ID: {test_data['user_id']}")
        print(f"- Subject ID: {test_data['subject_ids'][0]} (Mathematics)")
        print(f"- Chapter ID: {test_data['chapter_ids'][0]} (Algebra)")
        
    except Exception as e:
        print(f"❌ Error setting up test data: {str(e)}")
        import traceback
        traceback.print_exc()