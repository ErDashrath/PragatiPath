"""
Database Migration Strategy for Improved Multi-Student Schema
Carefully migrates existing data to new improved schema with proper foreign keys
"""

from django.db import migrations, models
import uuid
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    """
    Custom migration to implement improved multi-student database schema
    """
    
    dependencies = [
        ('assessment', '0005_usersession_userquestionhistory_usersubjectprogress_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    
    operations = [
        # Step 1: Create new master tables
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True, choices=[
                    ('quantitative_aptitude', 'Quantitative Aptitude'),
                    ('logical_reasoning', 'Logical Reasoning'),
                    ('data_interpretation', 'Data Interpretation'),
                    ('verbal_ability', 'Verbal Ability'),
                ])),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'subjects',
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
        ),
        
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('chapter_number', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                            related_name='chapters', to='assessment.subject')),
            ],
            options={
                'db_table': 'chapters',
                'verbose_name': 'Chapter',
                'verbose_name_plural': 'Chapters',
            },
        ),
        
        # Step 2: Create improved session table
        migrations.CreateModel(
            name='StudentSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_type', models.CharField(choices=[
                    ('PRACTICE', 'Practice Session'),
                    ('CHAPTER_TEST', 'Chapter Test'),
                    ('MOCK_TEST', 'Mock Test'),
                    ('FULL_TEST', 'Full Subject Test'),
                    ('ASSESSMENT', 'Assessment Test'),
                ], default='PRACTICE', max_length=20)),
                ('session_name', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[
                    ('ACTIVE', 'Active Session'),
                    ('PAUSED', 'Paused Session'),
                    ('COMPLETED', 'Completed Session'),
                    ('ABANDONED', 'Abandoned Session'),
                ], default='ACTIVE', max_length=15)),
                ('current_question_number', models.IntegerField(default=0)),
                ('total_questions_planned', models.IntegerField(default=10)),
                ('session_start_time', models.DateTimeField(auto_now_add=True)),
                ('session_end_time', models.DateTimeField(blank=True, null=True)),
                ('session_duration_seconds', models.IntegerField(default=0)),
                ('time_limit_minutes', models.IntegerField(blank=True, null=True)),
                ('questions_attempted', models.IntegerField(default=0)),
                ('questions_correct', models.IntegerField(default=0)),
                ('questions_incorrect', models.IntegerField(default=0)),
                ('questions_skipped', models.IntegerField(default=0)),
                ('questions_timeout', models.IntegerField(default=0)),
                ('total_score', models.FloatField(default=0.0)),
                ('max_possible_score', models.FloatField(default=0.0)),
                ('percentage_score', models.FloatField(default=0.0)),
                ('current_difficulty_level', models.CharField(choices=[
                    ('very_easy', 'Very Easy'),
                    ('easy', 'Easy'),
                    ('moderate', 'Moderate'),
                    ('difficult', 'Difficult'),
                ], default='easy', max_length=15)),
                ('difficulty_adjustments', models.JSONField(default=list)),
                ('session_config', models.JSONField(default=dict)),
                ('question_sequence', models.JSONField(default=list)),
                ('device_info', models.JSONField(blank=True, default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                           related_name='study_sessions', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                           related_name='sessions', to='assessment.subject')),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            related_name='sessions', to='assessment.chapter')),
            ],
            options={
                'db_table': 'student_sessions',
                'verbose_name': 'Student Session',
                'verbose_name_plural': 'Student Sessions',
                'ordering': ['-session_start_time'],
            },
        ),
        
        # Step 3: Create improved question attempt table
        migrations.CreateModel(
            name='QuestionAttempt',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('question_number_in_session', models.IntegerField()),
                ('attempt_number', models.IntegerField(default=1)),
                ('student_answer', models.CharField(blank=True, max_length=10)),
                ('correct_answer', models.CharField(max_length=10)),
                ('answer_status', models.CharField(choices=[
                    ('CORRECT', 'Correct Answer'),
                    ('INCORRECT', 'Incorrect Answer'),
                    ('SKIPPED', 'Question Skipped'),
                    ('TIMEOUT', 'Timed Out'),
                    ('NOT_ATTEMPTED', 'Not Attempted'),
                ], default='NOT_ATTEMPTED', max_length=15)),
                ('is_correct', models.BooleanField(default=False)),
                ('question_displayed_at', models.DateTimeField(auto_now_add=True)),
                ('answer_submitted_at', models.DateTimeField(blank=True, null=True)),
                ('time_spent_seconds', models.FloatField(default=0.0)),
                ('time_limit_seconds', models.IntegerField(blank=True, null=True)),
                ('difficulty_when_presented', models.CharField(choices=[
                    ('very_easy', 'Very Easy'),
                    ('easy', 'Easy'),
                    ('moderate', 'Moderate'),
                    ('difficult', 'Difficult'),
                ], max_length=15)),
                ('question_points', models.FloatField(default=1.0)),
                ('points_earned', models.FloatField(default=0.0)),
                ('hints_requested', models.IntegerField(default=0)),
                ('hints_used', models.JSONField(default=list)),
                ('explanation_viewed', models.BooleanField(default=False)),
                ('bookmarked', models.BooleanField(default=False)),
                ('confidence_level', models.IntegerField(blank=True, choices=[
                    (1, 'Very Low'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Very High')
                ], null=True)),
                ('student_feedback', models.TextField(blank=True)),
                ('interaction_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='question_attempts', to='assessment.studentsession')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='attempts', to='assessment.adaptivequestion')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='question_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'question_attempts',
                'verbose_name': 'Question Attempt',
                'verbose_name_plural': 'Question Attempts',
                'ordering': ['-created_at'],
            },
        ),
        
        # Step 4: Create improved progress tracking
        migrations.CreateModel(
            name='StudentProgress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('total_sessions', models.IntegerField(default=0)),
                ('total_questions_attempted', models.IntegerField(default=0)),
                ('total_questions_correct', models.IntegerField(default=0)),
                ('total_study_time_seconds', models.BigIntegerField(default=0)),
                ('current_accuracy_percentage', models.FloatField(default=0.0)),
                ('best_accuracy_percentage', models.FloatField(default=0.0)),
                ('current_mastery_level', models.CharField(choices=[
                    ('very_easy', 'Very Easy'),
                    ('easy', 'Easy'),
                    ('moderate', 'Moderate'),
                    ('difficult', 'Difficult'),
                ], default='easy', max_length=15)),
                ('mastery_score', models.FloatField(default=0.0)),
                ('chapter_progress', models.JSONField(default=dict)),
                ('chapter_mastery_scores', models.JSONField(default=dict)),
                ('unlocked_chapters', models.JSONField(default=list)),
                ('current_correct_streak', models.IntegerField(default=0)),
                ('longest_correct_streak', models.IntegerField(default=0)),
                ('current_study_streak_days', models.IntegerField(default=0)),
                ('longest_study_streak_days', models.IntegerField(default=0)),
                ('learning_velocity', models.FloatField(default=0.0)),
                ('difficulty_progression', models.JSONField(default=list)),
                ('performance_trend', models.JSONField(default=list)),
                ('last_session_date', models.DateTimeField(blank=True, null=True)),
                ('last_question_answered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='progress_records', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='student_progress', to='assessment.subject')),
                ('last_active_chapter', models.ForeignKey(blank=True, null=True, 
                                                        on_delete=django.db.models.deletion.SET_NULL,
                                                        to='assessment.chapter')),
            ],
            options={
                'db_table': 'student_progress',
                'verbose_name': 'Student Progress',
                'verbose_name_plural': 'Student Progress Records',
            },
        ),
        
        # Step 5: Create daily stats table
        migrations.CreateModel(
            name='DailyStudyStats',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('study_date', models.DateField()),
                ('total_sessions', models.IntegerField(default=0)),
                ('total_study_time_seconds', models.IntegerField(default=0)),
                ('questions_attempted', models.IntegerField(default=0)),
                ('questions_correct', models.IntegerField(default=0)),
                ('sessions_completed', models.IntegerField(default=0)),
                ('subject_time_distribution', models.JSONField(default=dict)),
                ('subject_question_counts', models.JSONField(default=dict)),
                ('subject_accuracy_rates', models.JSONField(default=dict)),
                ('new_chapters_unlocked', models.IntegerField(default=0)),
                ('difficulty_levels_progressed', models.JSONField(default=list)),
                ('personal_bests', models.JSONField(default=list)),
                ('streaks_maintained', models.JSONField(default=dict)),
                ('daily_accuracy_percentage', models.FloatField(default=0.0)),
                ('peak_performance_time', models.TimeField(blank=True, null=True)),
                ('focus_duration_minutes', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='daily_stats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'daily_study_stats',
                'verbose_name': 'Daily Study Stats',
                'verbose_name_plural': 'Daily Study Stats',
                'ordering': ['-study_date'],
            },
        ),
        
        # Step 6: Add unique constraints
        migrations.AddConstraint(
            model_name='chapter',
            constraint=models.UniqueConstraint(fields=['subject', 'chapter_number'], name='unique_chapter_per_subject'),
        ),
        
        migrations.AddConstraint(
            model_name='questionattempt',
            constraint=models.UniqueConstraint(fields=['session', 'question', 'attempt_number'], 
                                             name='unique_question_attempt'),
        ),
        
        migrations.AddConstraint(
            model_name='studentprogress',
            constraint=models.UniqueConstraint(fields=['student', 'subject'], name='unique_student_subject_progress'),
        ),
        
        migrations.AddConstraint(
            model_name='dailystudystats',
            constraint=models.UniqueConstraint(fields=['student', 'study_date'], name='unique_daily_stats'),
        ),
        
        # Step 7: Add database indexes for performance
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['student', 'status'], name='idx_student_status'),
        ),
        
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['subject', 'session_type'], name='idx_subject_type'),
        ),
        
        migrations.AddIndex(
            model_name='studentsession',
            index=models.Index(fields=['student', 'subject', 'status'], name='idx_student_subject_status'),
        ),
        
        migrations.AddIndex(
            model_name='questionattempt',
            index=models.Index(fields=['session', 'question_number_in_session'], name='idx_session_question_num'),
        ),
        
        migrations.AddIndex(
            model_name='questionattempt',
            index=models.Index(fields=['student', 'is_correct'], name='idx_student_correct'),
        ),
        
        migrations.AddIndex(
            model_name='studentprogress',
            index=models.Index(fields=['student', 'subject'], name='idx_progress_lookup'),
        ),
        
        migrations.AddIndex(
            model_name='dailystudystats',
            index=models.Index(fields=['student', 'study_date'], name='idx_daily_lookup'),
        ),
    ]