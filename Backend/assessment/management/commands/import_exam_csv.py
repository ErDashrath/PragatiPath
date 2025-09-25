"""
Django management command to import competitive exam questions from CSV files.
Supports subject-wise import with automatic difficulty mapping.

Usage:
python manage.py import_exam_csv data/quantitative_aptitude.csv --subject quantitative_aptitude
python manage.py import_exam_csv data/logical_reasoning.csv --subject logical_reasoning
python manage.py import_exam_csv data/data_interpretation.csv --subject data_interpretation
python manage.py import_exam_csv data/verbal_ability.csv --subject verbal_ability
"""

import csv
import re
import uuid
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from assessment.models import AdaptiveQuestion


class Command(BaseCommand):
    help = 'Import competitive exam questions from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--subject',
            type=str,
            choices=['quantitative_aptitude', 'logical_reasoning', 'data_interpretation', 'verbal_ability'],
            required=True,
            help='Subject area for the questions'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing questions for this subject before importing'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of questions to import in each batch (default: 100)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        subject = options['subject']
        clear_existing = options['clear_existing']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        self.stdout.write(
            self.style.SUCCESS(f'Starting import for subject: {subject}')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be imported'))

        # Clear existing questions if requested
        if clear_existing and not dry_run:
            with transaction.atomic():
                deleted_count = AdaptiveQuestion.objects.filter(subject=subject).count()
                AdaptiveQuestion.objects.filter(subject=subject).delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing questions for {subject}')
                )

        # Import CSV data
        try:
            imported_count = self._import_csv_data(csv_file, subject, dry_run, batch_size)
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {imported_count} questions for {subject}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Would import {imported_count} questions for {subject}')
                )
                
        except Exception as e:
            raise CommandError(f'Error importing CSV data: {str(e)}')

    def _import_csv_data(self, csv_file, subject, dry_run, batch_size):
        """Import questions from CSV file in batches"""
        imported_count = 0
        batch_questions = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Detect CSV format by examining headers
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                self.stdout.write(f'CSV Headers: {headers}')
                
                # Validate required headers (flexible header names)
                required_headers = ['id', 'answer', 'difficulty']
                option_headers = ['option_a', 'option_b', 'option_c', 'option_d'] or ['a', 'b', 'c', 'd']
                question_headers = ['question_text'] or ['question']
                
                missing_headers = [h for h in required_headers if h not in headers]
                
                # Check for question text field
                question_field = None
                for q_header in ['question_text', 'question']:
                    if q_header in headers:
                        question_field = q_header
                        break
                
                if not question_field:
                    raise CommandError('Missing question text field. Expected "question_text" or "question"')
                
                # Check for option fields (either option_a/b/c/d or a/b/c/d)
                option_fields = {}
                if all(f'option_{opt}' in headers for opt in ['a', 'b', 'c', 'd']):
                    option_fields = {'a': 'option_a', 'b': 'option_b', 'c': 'option_c', 'd': 'option_d'}
                elif all(opt in headers for opt in ['a', 'b', 'c', 'd']):
                    option_fields = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'}
                else:
                    raise CommandError('Missing option fields. Expected either "option_a/b/c/d" or "a/b/c/d"')
                
                if missing_headers:
                    raise CommandError(f'Missing required CSV headers: {missing_headers}')

                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                    try:
                        question = self._create_question_from_row(row, subject, row_num, question_field, option_fields)
                        if question:
                            batch_questions.append(question)
                            imported_count += 1
                            
                            # Process batch when full
                            if len(batch_questions) >= batch_size:
                                if not dry_run:
                                    self._save_batch(batch_questions)
                                self.stdout.write(f'Processed {imported_count} questions...')
                                batch_questions = []
                                
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing row {row_num}: {str(e)}')
                        )
                        continue

                # Save remaining questions in final batch
                if batch_questions and not dry_run:
                    self._save_batch(batch_questions)
                    
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')
            
        return imported_count

    def _create_question_from_row(self, row, subject, row_num, question_field, option_fields):
        """Create AdaptiveQuestion object from CSV row with flexible field mapping"""
        try:
            # Extract and clean data using flexible field names
            question_text = self._clean_text(row.get(question_field, ''))
            if not question_text:
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Empty question text, skipping')
                )
                return None

            option_a = self._clean_text(row.get(option_fields['a'], ''))
            option_b = self._clean_text(row.get(option_fields['b'], ''))
            option_c = self._clean_text(row.get(option_fields['c'], ''))
            option_d = self._clean_text(row.get(option_fields['d'], ''))
            
            # Validate options
            if not all([option_a, option_b, option_c, option_d]):
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Missing options, skipping')
                )
                return None

            # Map answer
            answer = row.get('answer', '').strip().lower()
            if answer not in ['a', 'b', 'c', 'd']:
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Invalid answer "{answer}", skipping')
                )
                return None

            # Map difficulty
            difficulty_level = self._map_difficulty(row.get('difficulty', ''))
            if not difficulty_level:
                self.stdout.write(
                    self.style.WARNING(f'Row {row_num}: Invalid difficulty, using "moderate"')
                )
                difficulty_level = 'moderate'

            # Generate IRT parameters based on difficulty
            irt_params = self._get_irt_parameters(difficulty_level)
            
            # Create question object
            question = AdaptiveQuestion(
                id=uuid.uuid4(),
                question_text=question_text,
                question_type='multiple_choice',
                
                # Multiple choice options
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                
                # Answer and difficulty
                answer=answer,
                difficulty_level=difficulty_level,
                subject=subject,
                
                # Legacy compatibility
                correct_answer=f"Option {answer.upper()}: {locals()[f'option_{answer}']}",
                options=[option_a, option_b, option_c, option_d],
                
                # IRT parameters
                difficulty=irt_params['difficulty'],
                discrimination=irt_params['discrimination'],
                guessing=irt_params['guessing'],
                
                # Level mapping (1=very_easy, 2=easy, 3=moderate, 4=difficult)
                level=self._get_level_from_difficulty(difficulty_level),
                
                # Additional fields
                skill_id=f"{subject}_{difficulty_level}",
                fundamental_type='problem_solving',
                topic=subject.replace('_', ' ').title(),
                estimated_time_seconds=self._get_estimated_time(subject, difficulty_level),
                
                # CSV metadata
                tags=f"csv_import,{subject},{difficulty_level}",
                
                # Initialize statistics
                times_attempted=0,
                times_correct=0,
                average_response_time=0.0,
                is_active=True
            )
            
            return question

        except Exception as e:
            raise Exception(f'Error creating question from row {row_num}: {str(e)}')

    def _save_batch(self, questions):
        """Save a batch of questions using bulk_create"""
        with transaction.atomic():
            AdaptiveQuestion.objects.bulk_create(questions, ignore_conflicts=True)

    def _clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', str(text).strip())
        
        # Remove common CSV artifacts
        text = text.replace('""', '"')
        text = text.replace('\\n', '\n')
        
        return text

    def _map_difficulty(self, difficulty_str):
        """Map difficulty string to standard choices"""
        if not difficulty_str:
            return 'moderate'
            
        difficulty_str = difficulty_str.lower().strip()
        
        # Mapping dictionary
        difficulty_map = {
            'very easy': 'very_easy',
            'very_easy': 'very_easy',
            'veryeasy': 'very_easy',
            'easy': 'easy',
            'moderate': 'moderate',
            'medium': 'moderate',
            'difficult': 'difficult',
            'hard': 'difficult',
            'very difficult': 'difficult',
            'very_difficult': 'difficult',
        }
        
        return difficulty_map.get(difficulty_str, 'moderate')

    def _get_irt_parameters(self, difficulty_level):
        """Get IRT parameters based on difficulty level"""
        irt_params = {
            'very_easy': {'difficulty': -1.5, 'discrimination': 0.8, 'guessing': 0.3},
            'easy': {'difficulty': -0.5, 'discrimination': 1.0, 'guessing': 0.25},
            'moderate': {'difficulty': 0.0, 'discrimination': 1.2, 'guessing': 0.2},
            'difficult': {'difficulty': 1.0, 'discrimination': 1.5, 'guessing': 0.1},
        }
        return irt_params.get(difficulty_level, irt_params['moderate'])

    def _get_level_from_difficulty(self, difficulty_level):
        """Map difficulty to numeric level"""
        level_map = {
            'very_easy': 1,
            'easy': 2,
            'moderate': 3,
            'difficult': 4
        }
        return level_map.get(difficulty_level, 3)

    def _get_estimated_time(self, subject, difficulty_level):
        """Get estimated time based on subject and difficulty"""
        base_times = {
            'quantitative_aptitude': 120,  # 2 minutes
            'logical_reasoning': 90,       # 1.5 minutes
            'data_interpretation': 180,    # 3 minutes
            'verbal_ability': 60          # 1 minute
        }
        
        difficulty_multipliers = {
            'very_easy': 0.7,
            'easy': 0.85,
            'moderate': 1.0,
            'difficult': 1.3
        }
        
        base_time = base_times.get(subject, 90)
        multiplier = difficulty_multipliers.get(difficulty_level, 1.0)
        
        return int(base_time * multiplier)

    def _display_summary(self, imported_count, subject):
        """Display import summary"""
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Import Summary ===\n'
                f'Subject: {subject}\n'
                f'Questions imported: {imported_count}\n'
                f'Status: Complete\n'
            )
        )