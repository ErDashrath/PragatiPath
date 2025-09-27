"""
Initialize adaptive learning data with proper subjects and test questions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User
from assessment.improved_models import Subject, Chapter
from assessment.models import AdaptiveQuestion

def create_subjects_and_chapters():
    """Create subjects and chapters based on your system"""
    
    # Your actual subjects
    subjects_data = [
        {
            'code': 'quantitative_aptitude',
            'name': 'Quantitative Aptitude',
            'description': 'Mathematical and numerical reasoning questions'
        },
        {
            'code': 'logical_reasoning', 
            'name': 'Logical Reasoning',
            'description': 'Logic-based problem solving questions'
        },
        {
            'code': 'data_interpretation',
            'name': 'Data Interpretation', 
            'description': 'Data analysis and interpretation questions'
        },
        {
            'code': 'verbal_ability',
            'name': 'Verbal Ability',
            'description': 'Language and communication skills questions'
        }
    ]
    
    # Create subjects
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={
                'name': subject_data['name'],
                'description': subject_data['description']
            }
        )
        print(f"{'Created' if created else 'Found'} subject: {subject.name}")
        
        # Create sample chapters for each subject
        chapters_data = get_chapters_for_subject(subject_data['code'])
        
        for chapter_data in chapters_data:
            chapter, created = Chapter.objects.get_or_create(
                subject=subject,
                chapter_number=chapter_data['number'],
                defaults={
                    'name': chapter_data['name'],
                    'description': chapter_data['description']
                }
            )
            print(f"  {'Created' if created else 'Found'} chapter: {chapter.name}")


def get_chapters_for_subject(subject_code):
    """Get chapter data for each subject"""
    
    chapters = {
        'quantitative_aptitude': [
            {'number': 1, 'name': 'Number System', 'description': 'Basic number theory and operations'},
            {'number': 2, 'name': 'Algebra', 'description': 'Linear and quadratic equations'},
            {'number': 3, 'name': 'Geometry', 'description': 'Basic geometric concepts and formulas'},
            {'number': 4, 'name': 'Arithmetic', 'description': 'Percentages, profit/loss, ratios'},
        ],
        'logical_reasoning': [
            {'number': 1, 'name': 'Syllogisms', 'description': 'Logical deduction from premises'},
            {'number': 2, 'name': 'Puzzles', 'description': 'Arrangement and seating puzzles'},
            {'number': 3, 'name': 'Coding-Decoding', 'description': 'Pattern recognition in codes'},
            {'number': 4, 'name': 'Blood Relations', 'description': 'Family relationship problems'},
        ],
        'data_interpretation': [
            {'number': 1, 'name': 'Tables', 'description': 'Data analysis from tabular format'},
            {'number': 2, 'name': 'Graphs', 'description': 'Bar charts, line graphs analysis'},
            {'number': 3, 'name': 'Pie Charts', 'description': 'Circular data representation'},
            {'number': 4, 'name': 'Case Studies', 'description': 'Complex data scenario analysis'},
        ],
        'verbal_ability': [
            {'number': 1, 'name': 'Reading Comprehension', 'description': 'Passage-based questions'},
            {'number': 2, 'name': 'Grammar', 'description': 'English grammar and usage'},
            {'number': 3, 'name': 'Vocabulary', 'description': 'Word meanings and usage'},
            {'number': 4, 'name': 'Sentence Correction', 'description': 'Error identification and correction'},
        ]
    }
    
    return chapters.get(subject_code, [])


def create_sample_questions():
    """Create sample questions for testing"""
    
    sample_questions = [
        {
            'subject': 'quantitative_aptitude',
            'question_text': 'If 20% of a number is 40, what is 50% of that number?',
            'option_a': '80',
            'option_b': '100',
            'option_c': '120',
            'option_d': '150',
            'answer': 'b',
            'difficulty_level': 'easy'
        },
        {
            'subject': 'quantitative_aptitude', 
            'question_text': 'A train 300m long is running at 54 km/hr. In what time will it cross a platform 200m long?',
            'option_a': '30 seconds',
            'option_b': '33.33 seconds', 
            'option_c': '35 seconds',
            'option_d': '40 seconds',
            'answer': 'b',
            'difficulty_level': 'moderate'
        },
        {
            'subject': 'logical_reasoning',
            'question_text': 'All cats are animals. Some animals are dogs. Which conclusion follows?',
            'option_a': 'All cats are dogs',
            'option_b': 'Some cats are dogs',
            'option_c': 'No cats are dogs',
            'option_d': 'Cannot be determined',
            'answer': 'd',
            'difficulty_level': 'moderate'
        },
        {
            'subject': 'data_interpretation',
            'question_text': 'In a pie chart, if one sector represents 72°, what percentage of the total does it represent?',
            'option_a': '15%',
            'option_b': '20%',
            'option_c': '25%',
            'option_d': '30%',
            'answer': 'b',
            'difficulty_level': 'easy'
        },
        {
            'subject': 'verbal_ability',
            'question_text': 'Choose the word most similar to "Ephemeral":',
            'option_a': 'Permanent',
            'option_b': 'Temporary',
            'option_c': 'Solid',
            'option_d': 'Heavy',
            'answer': 'b',
            'difficulty_level': 'moderate'
        }
    ]
    
    # Get subjects and chapters
    subjects = {s.code: s for s in Subject.objects.all()}
    chapters = {s.code: list(Chapter.objects.filter(subject=s)) for s in Subject.objects.all()}
    
    for q_data in sample_questions:
        subject_obj = subjects.get(q_data['subject'])
        chapter_obj = chapters.get(q_data['subject'], [None])[0] if chapters.get(q_data['subject']) else None
        
        if subject_obj:
            question, created = AdaptiveQuestion.objects.get_or_create(
                question_text=q_data['question_text'],
                defaults={
                    'subject': q_data['subject'],
                    'subject_fk': subject_obj,
                    'chapter': chapter_obj,
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'], 
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'answer': q_data['answer'],
                    'difficulty_level': q_data['difficulty_level'],
                    'question_type': 'multiple_choice',
                    'is_active': True
                }
            )
            print(f"{'Created' if created else 'Found'} question: {q_data['question_text'][:50]}...")


def create_test_user():
    """Create a test user for API testing"""
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
    
    print(f"{'Created' if created else 'Found'} test user: {user.username}")
    return user


def main():
    """Initialize all test data"""
    print("🚀 Initializing Adaptive Learning System Data")
    print("=" * 50)
    
    # Create subjects and chapters
    create_subjects_and_chapters()
    print()
    
    # Create sample questions
    print("Creating sample questions...")
    create_sample_questions()
    print()
    
    # Create test user
    print("Creating test user...")
    test_user = create_test_user()
    print()
    
    # Show summary
    print("📊 Data Summary:")
    print(f"Subjects: {Subject.objects.count()}")
    print(f"Chapters: {Chapter.objects.count()}")
    print(f"Questions: {AdaptiveQuestion.objects.count()}")
    print(f"Users: {User.objects.count()}")
    print()
    
    # Show test API parameters
    subjects = Subject.objects.all()
    print("🔗 Test API Parameters:")
    print(f"Test User ID: {test_user.id}")
    for subject in subjects:
        print(f"Subject '{subject.name}' - ID: {subject.id}, Code: {subject.code}")
    print()
    
    print("✅ Data initialization complete!")
    print("You can now test the adaptive API with these parameters.")


if __name__ == "__main__":
    main()