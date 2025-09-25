"""
Data Migration Script for Improved Multi-Student Schema
Populates subjects and chapters, creates test data for demonstration
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from assessment.improved_models import Subject, Chapter, StudentSession, QuestionAttempt, StudentProgress, DailyStudyStats
from assessment.models import AdaptiveQuestion
from django.utils import timezone
import uuid


class Command(BaseCommand):
    help = 'Populate initial data for improved multi-student schema'

    def handle(self, *args, **options):
        """Main execution method"""
        self.stdout.write(self.style.SUCCESS('Starting data migration for improved multi-student schema...'))
        
        try:
            with transaction.atomic():
                # Step 1: Create subjects
                self.create_subjects()
                
                # Step 2: Create chapters
                self.create_chapters()
                
                # Step 3: Create sample students if none exist
                self.create_sample_students()
                
                # Step 4: Initialize progress records for existing students
                self.initialize_student_progress()
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully completed data migration for improved multi-student schema!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during data migration: {str(e)}')
            )
            raise
    
    def create_subjects(self):
        """Create the four main subjects"""
        subjects_data = [
            {
                'code': 'quantitative_aptitude',
                'name': 'Quantitative Aptitude',
                'description': 'Mathematics, Arithmetic, Algebra, Geometry, and Data Analysis'
            },
            {
                'code': 'logical_reasoning',
                'name': 'Logical Reasoning',
                'description': 'Logical puzzles, patterns, analytical reasoning, and critical thinking'
            },
            {
                'code': 'data_interpretation',
                'name': 'Data Interpretation',
                'description': 'Charts, graphs, tables, and data analysis questions'
            },
            {
                'code': 'verbal_ability',
                'name': 'Verbal Ability',
                'description': 'Reading comprehension, grammar, vocabulary, and language skills'
            }
        ]
        
        created_subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'description': subject_data['description'],
                    'is_active': True
                }
            )
            created_subjects.append(subject)
            
            if created:
                self.stdout.write(f'✓ Created subject: {subject.name}')
            else:
                self.stdout.write(f'- Subject already exists: {subject.name}')
        
        return created_subjects
    
    def create_chapters(self):
        """Create chapters for each subject"""
        chapters_data = {
            'quantitative_aptitude': [
                'Number Systems and Basic Arithmetic',
                'Percentages and Profit & Loss',
                'Simple and Compound Interest',
                'Ratio and Proportion',
                'Algebra and Linear Equations',
                'Geometry and Mensuration',
                'Statistics and Probability',
                'Time and Work',
                'Speed, Time and Distance',
                'Mixtures and Allegations'
            ],
            'logical_reasoning': [
                'Logical Sequences and Series',
                'Analogies and Classifications',
                'Coding and Decoding',
                'Blood Relations',
                'Direction and Distance',
                'Puzzles and Arrangements',
                'Syllogisms',
                'Statement and Assumptions',
                'Cause and Effect',
                'Logical Games'
            ],
            'data_interpretation': [
                'Tables and Basic Calculations',
                'Bar Charts and Column Charts',
                'Line Graphs and Trends',
                'Pie Charts and Percentages',
                'Mixed Charts and Comparisons',
                'Data Sufficiency',
                'Caselets and Business Data',
                'Network Diagrams',
                'Venn Diagrams',
                'Advanced Data Analysis'
            ],
            'verbal_ability': [
                'Reading Comprehension - Basic',
                'Reading Comprehension - Advanced',
                'Grammar and Sentence Correction',
                'Vocabulary and Word Usage',
                'Para Jumbles',
                'Critical Reasoning',
                'Fill in the Blanks',
                'Synonyms and Antonyms',
                'Idioms and Phrases',
                'Error Detection'
            ]
        }
        
        created_chapters = []
        for subject_code, chapter_names in chapters_data.items():
            try:
                subject = Subject.objects.get(code=subject_code)
                for i, chapter_name in enumerate(chapter_names, 1):
                    chapter, created = Chapter.objects.get_or_create(
                        subject=subject,
                        chapter_number=i,
                        defaults={
                            'name': chapter_name,
                            'description': f'Chapter {i} of {subject.name}: {chapter_name}',
                            'is_active': True
                        }
                    )
                    created_chapters.append(chapter)
                    
                    if created:
                        self.stdout.write(f'✓ Created chapter: {subject.name} - {chapter.name}')
                    else:
                        self.stdout.write(f'- Chapter already exists: {subject.name} - {chapter.name}')
            except Subject.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Subject not found: {subject_code}'))
        
        return created_chapters
    
    def create_sample_students(self):
        """Create sample student accounts for testing"""
        sample_students = [
            {'username': 'student1', 'email': 'student1@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'student2', 'email': 'student2@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'student3', 'email': 'student3@example.com', 'first_name': 'Carol', 'last_name': 'Davis'},
        ]
        
        created_students = []
        for student_data in sample_students:
            user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('testpass123')  # Set a default password
                user.save()
                created_students.append(user)
                self.stdout.write(f'✓ Created sample student: {user.username}')
            else:
                self.stdout.write(f'- Student already exists: {user.username}')
        
        return created_students
    
    def initialize_student_progress(self):
        """Initialize progress records for all students and subjects"""
        students = User.objects.filter(is_active=True, is_staff=False)
        subjects = Subject.objects.filter(is_active=True)
        
        progress_created = 0
        for student in students:
            for subject in subjects:
                progress, created = StudentProgress.objects.get_or_create(
                    student=student,
                    subject=subject,
                    defaults={
                        'total_sessions': 0,
                        'total_questions_attempted': 0,
                        'total_questions_correct': 0,
                        'current_accuracy_percentage': 0.0,
                        'best_accuracy_percentage': 0.0,
                        'current_mastery_level': 'easy',
                        'mastery_score': 0.0,
                        'current_correct_streak': 0,
                        'longest_correct_streak': 0,
                        'current_study_streak_days': 0,
                        'longest_study_streak_days': 0,
                        'learning_velocity': 0.0,
                        'difficulty_progression': [],
                        'performance_trend': [],
                        'chapter_progress': {},
                        'chapter_mastery_scores': {},
                        'unlocked_chapters': []
                    }
                )
                
                if created:
                    progress_created += 1
        
        self.stdout.write(f'✓ Initialized {progress_created} student progress records')
    
    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new records',
        )