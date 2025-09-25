"""
Management command to load questions from CSV files into the database
with proper Subject → Chapter → Question relationships
"""
import os
import csv
import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from assessment.models import AdaptiveQuestion
from assessment.improved_models import Subject, Chapter


class Command(BaseCommand):
    help = 'Load questions from CSV files with proper foreign key relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing questions...')
            AdaptiveQuestion.objects.all().delete()

        # Define CSV structure and chapter mappings
        csv_structure = {
            'quantitative_aptitude': {
                'subject_name': 'Quantitative Aptitude',
                'chapters': {
                    'percentages.csv': 'Percentages',
                    'profit_and_loss.csv': 'Profit and Loss', 
                    'ratios_and_proportions.csv': 'Ratios and Proportions'
                }
            },
            'logical_reasoning': {
                'subject_name': 'Logical Reasoning',
                'chapters': {
                    'pattern_recognition.csv': 'Pattern Recognition',
                    'syllogisms.csv': 'Syllogisms'
                }
            },
            'data_interpretation': {
                'subject_name': 'Data Interpretation',
                'chapters': {
                    'bar_charts.csv': 'Bar Charts',
                    'line_graphs.csv': 'Line Graphs',
                    'pie_charts.csv': 'Pie Charts'
                }
            },
            'verbal_ability': {
                'subject_name': 'Verbal Ability',
                'chapters': {
                    'vocabulary.csv': 'Vocabulary',
                    'grammar.csv': 'Grammar',
                    'reading_comprehension.csv': 'Reading Comprehension'
                }
            }
        }

        # Get the Backend directory path and add sample_data  
        # __file__ is in assessment/management/commands/load_csv_questions.py
        # We need to go up 4 levels to get to Backend directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        sample_data_path = os.path.join(base_dir, 'sample_data')
        
        self.stdout.write(f'Looking for CSV files in: {sample_data_path}')
        
        total_questions_loaded = 0
        
        for subject_code, subject_info in csv_structure.items():
            try:
                # Get or create subject
                subject, created = Subject.objects.get_or_create(
                    code=subject_code,
                    defaults={
                        'name': subject_info['subject_name'],
                        'description': f'{subject_info["subject_name"]} questions for competitive exams',
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Created subject: {subject.name}')
                else:
                    self.stdout.write(f'Using existing subject: {subject.name}')
                
                # Process each chapter CSV
                chapter_num = 1
                for csv_file, chapter_name in subject_info['chapters'].items():
                    csv_path = os.path.join(sample_data_path, subject_code, csv_file)
                    
                    if not os.path.exists(csv_path):
                        self.stdout.write(f'CSV file not found: {csv_path}')
                        continue
                    
                    # Get or create chapter
                    chapter, created = Chapter.objects.get_or_create(
                        subject=subject,
                        chapter_number=chapter_num,
                        defaults={
                            'name': chapter_name,
                            'description': f'Chapter {chapter_num} of {subject.name}: {chapter_name}',
                            'is_active': True
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'Created chapter: {chapter.name}')
                    else:
                        self.stdout.write(f'Using existing chapter: {chapter.name}')
                    
                    # Load questions from CSV
                    questions_loaded = self.load_questions_from_csv(csv_path, subject, chapter)
                    self.stdout.write(f'Loaded {questions_loaded} questions for {chapter.name}')
                    total_questions_loaded += questions_loaded
                    
                    chapter_num += 1
                    
            except Exception as e:
                self.stdout.write(f'Error processing subject {subject_code}: {e}')
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {total_questions_loaded} questions with proper relationships!'))

    def load_questions_from_csv(self, csv_path, subject, chapter):
        """Load questions from a single CSV file"""
        questions_loaded = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Skip empty rows or rows with missing critical data
                        question_text = row.get('question_text', '') or ''
                        if not question_text.strip():
                            continue
                        
                        # Handle None values in tags field
                        tags_value = row.get('tags', '') or ''
                        if not tags_value.strip():
                            tags_value = chapter.name
                            
                        # Map CSV difficulty to our choices
                        difficulty_mapping = {
                            'Very easy': 'very_easy',
                            'Easy': 'easy', 
                            'Moderate': 'moderate',
                            'Difficult': 'difficult'
                        }
                        
                        difficulty_level = difficulty_mapping.get(row.get('difficulty', 'Easy'), 'easy')
                        
                        # Convert level based on difficulty
                        level_mapping = {
                            'very_easy': 1,
                            'easy': 2,
                            'moderate': 3,
                            'difficult': 4
                        }
                        level = level_mapping.get(difficulty_level, 2)
                        
                        # Determine IRT difficulty parameter
                        irt_difficulty_mapping = {
                            'very_easy': -1.5,
                            'easy': -0.5,
                            'moderate': 0.5,
                            'difficult': 1.5
                        }
                        irt_difficulty = irt_difficulty_mapping.get(difficulty_level, 0.0)
                        
                        # Create question with proper relationships
                        question = AdaptiveQuestion.objects.create(
                            # Proper foreign key relationships
                            subject_fk=subject,
                            chapter=chapter,
                            
                            # Question content
                            question_text=row['question_text'],
                            question_type='multiple_choice',
                            
                            # Options
                            option_a=row.get('option_a', ''),
                            option_b=row.get('option_b', ''),
                            option_c=row.get('option_c', ''),
                            option_d=row.get('option_d', ''),
                            
                            # Answer and metadata
                            answer=row.get('answer', 'a').lower(),
                            correct_answer=row.get('answer', 'a').lower(),
                            difficulty_level=difficulty_level,
                            level=level,
                            
                            # IRT parameters
                            difficulty=irt_difficulty,
                            discrimination=1.0,
                            guessing=0.25,  # 25% for 4-option MC
                            
                        # Categorization
                        tags=tags_value,
                        topic=chapter.name,
                        subtopic=tags_value,                            # Legacy compatibility
                            subject=subject.code,
                            skill_id=f"{subject.code}_{chapter.name.lower().replace(' ', '_')}",
                            
                            # Timing
                            estimated_time_seconds=60,  # Default 1 minute per question
                            
                            # Status
                            is_active=True
                        )
                        
                        questions_loaded += 1
                        
                    except Exception as e:
                        self.stdout.write(f'Error loading question: {e}')
                        continue
                        
        except FileNotFoundError:
            self.stdout.write(f'File not found: {csv_path}')
        except Exception as e:
            self.stdout.write(f'Error reading CSV file {csv_path}: {e}')
        
        return questions_loaded

    def format_options_dict(self, option_a, option_b, option_c, option_d):
        """Format options as dictionary for JSON field"""
        return {
            'a': option_a,
            'b': option_b, 
            'c': option_c,
            'd': option_d
        }