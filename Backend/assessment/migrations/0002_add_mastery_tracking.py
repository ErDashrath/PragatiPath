"""
Database migration for enhanced adaptive learning with mastery tracking
Run: python manage.py makemigrations assessment
Then: python manage.py migrate
"""
from django.db import migrations, models
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),  # Adjust based on your last migration
    ]

    operations = [
        # Add StudentMastery model
        migrations.CreateModel(
            name='StudentMastery',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('mastery_score', models.FloatField(
                    default=0.0,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='Current mastery score (0.0 to 1.0)'
                )),
                ('mastery_level', models.CharField(
                    max_length=20,
                    choices=[
                        ('novice', 'Novice (0-30%)'),
                        ('developing', 'Developing (30-50%)'),
                        ('proficient', 'Proficient (50-70%)'),
                        ('advanced', 'Advanced (70-85%)'),
                        ('expert', 'Expert (85-100%)'),
                    ],
                    default='novice',
                    help_text='Categorized mastery level'
                )),
                ('confidence_score', models.FloatField(
                    default=0.0,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='Confidence in mastery assessment'
                )),
                ('bkt_knowledge_probability', models.FloatField(
                    default=0.0,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='BKT knowledge probability'
                )),
                ('bkt_learning_rate', models.FloatField(
                    default=0.1,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='BKT learning rate parameter'
                )),
                ('bkt_guess_rate', models.FloatField(
                    default=0.2,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='BKT guess rate parameter'
                )),
                ('bkt_slip_rate', models.FloatField(
                    default=0.1,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='BKT slip rate parameter'
                )),
                ('dkt_knowledge_state', models.JSONField(
                    default=dict,
                    help_text='DKT knowledge state vector'
                )),
                ('dkt_prediction_confidence', models.FloatField(
                    default=0.0,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0)
                    ],
                    help_text='DKT prediction confidence'
                )),
                ('questions_attempted', models.PositiveIntegerField(
                    default=0,
                    help_text='Total questions attempted in this context'
                )),
                ('questions_correct', models.PositiveIntegerField(
                    default=0,
                    help_text='Total questions answered correctly'
                )),
                ('average_response_time', models.FloatField(
                    default=0.0,
                    help_text='Average response time in seconds'
                )),
                ('difficulty_progression', models.JSONField(
                    default=list,
                    help_text='Track of difficulty levels attempted'
                )),
                ('first_assessment', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Student Mastery',
                'verbose_name_plural': 'Student Masteries',
            },
        ),
        
        # Add foreign key relationships to StudentMastery
        migrations.AddField(
            model_name='studentmastery',
            name='student_session',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='mastery_records',
                to='assessment.StudentSession',
                help_text='Session associated with this mastery record'
            ),
        ),
        migrations.AddField(
            model_name='studentmastery',
            name='subject',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='student_masteries',
                to='assessment.Subject',
                help_text='Subject for mastery tracking'
            ),
        ),
        migrations.AddField(
            model_name='studentmastery',
            name='chapter',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='student_masteries',
                to='assessment.Chapter',
                help_text='Chapter for mastery tracking'
            ),
        ),
        
        # Add enhanced mastery fields to StudentSession
        migrations.AddField(
            model_name='studentsession',
            name='current_mastery_score',
            field=models.FloatField(
                default=0.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0)
                ],
                help_text='Overall session mastery score'
            ),
        ),
        migrations.AddField(
            model_name='studentsession',
            name='mastery_threshold',
            field=models.FloatField(
                default=0.8,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0)
                ],
                help_text='Threshold for mastery achievement'
            ),
        ),
        migrations.AddField(
            model_name='studentsession',
            name='mastery_achieved',
            field=models.BooleanField(
                default=False,
                help_text='Whether mastery has been achieved in this session'
            ),
        ),
        migrations.AddField(
            model_name='studentsession',
            name='mastery_achieved_at',
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text='Timestamp when mastery was achieved'
            ),
        ),
        migrations.AddField(
            model_name='studentsession',
            name='session_analytics',
            field=models.JSONField(
                default=dict,
                help_text='Comprehensive session analytics for reporting'
            ),
        ),
        
        # Add indexes for performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_student_mastery_session_subject ON assessment_studentmastery (student_session_id, subject_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_mastery_session_subject;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_student_mastery_score ON assessment_studentmastery (mastery_score);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_mastery_score;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_student_mastery_level ON assessment_studentmastery (subject_id, mastery_level);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_mastery_level;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_student_mastery_updated ON assessment_studentmastery (last_updated);",
            reverse_sql="DROP INDEX IF EXISTS idx_student_mastery_updated;"
        ),
        
        # Add unique constraint
        migrations.AddConstraint(
            model_name='studentmastery',
            constraint=models.UniqueConstraint(
                fields=['student_session', 'subject', 'chapter'],
                name='unique_session_subject_chapter_mastery'
            ),
        ),
    ]