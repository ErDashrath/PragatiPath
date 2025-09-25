"""
Quick test student creation management command
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import StudentProfile
import uuid

class Command(BaseCommand):
    help = 'Create test students for AI system testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=2, help='Number of test students to create')

    def handle(self, *args, **options):
        count = options['count']
        created = []
        
        for i in range(count):
            username = f"test_ai_student_{i+1}"
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"User {username} already exists")
                user = User.objects.get(username=username)
                student_profile = user.student_profile
                created.append({
                    'username': username,
                    'student_id': str(student_profile.id),
                    'email': user.email,
                    'status': 'existing'
                })
                continue
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=f"{username}@test.com",
                password="testpass123"
            )
            
            # Create student profile
            student_profile = StudentProfile.objects.create(user=user)
            
            created.append({
                'username': username,
                'student_id': str(student_profile.id),
                'email': user.email,
                'status': 'created'
            })
            
            self.stdout.write(
                self.style.SUCCESS(f'Created test student: {username} (ID: {student_profile.id})')
            )
        
        if created:
            self.stdout.write(f"\nTest students available:")
            for student in created:
                status = "✅ Created" if student['status'] == 'created' else "📋 Existing"
                self.stdout.write(f"  {status} {student['username']}: {student['student_id']}")
        else:
            self.stdout.write("No test students available")