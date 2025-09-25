"""
SM-2 Spaced Repetition System - Quick Demo Script
Creates sample data and demonstrates the SM-2 algorithm functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from assessment.models import AdaptiveQuestion
from practice.models import SRSCard
from practice.sm2 import SM2Scheduler
import json

def create_sample_data():
    """Create sample data for SM-2 demo"""
    print("🚀 Creating sample data for SM-2 demonstration...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='sm2_demo_student',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'Student'
        }
    )
    if created:
        print(f"✅ Created demo student: {user.username}")
    else:
        print(f"📝 Using existing demo student: {user.username}")
    
    # Create sample questions if they don't exist
    sample_questions = [
        {
            'question_text': 'What is the quadratic formula?',
            'question_type': 'multiple_choice',
            'correct_answer': 'x = (-b ± √(b²-4ac)) / 2a',
            'difficulty': 0.7
        },
        {
            'question_text': 'Solve: 2x + 5 = 15',
            'question_type': 'short_answer', 
            'correct_answer': 'x = 5',
            'difficulty': 0.4
        },
        {
            'question_text': 'What is the derivative of x²?',
            'question_type': 'short_answer',
            'correct_answer': '2x',
            'difficulty': 0.6
        },
        {
            'question_text': 'Factor: x² - 9',
            'question_type': 'short_answer',
            'correct_answer': '(x+3)(x-3)',
            'difficulty': 0.5
        },
        {
            'question_text': 'What is the limit of (1/x) as x approaches infinity?',
            'question_type': 'multiple_choice',
            'correct_answer': '0',
            'difficulty': 0.8
        }
    ]
    
    questions = []
    for q_data in sample_questions:
        question, created = AdaptiveQuestion.objects.get_or_create(
            question_text=q_data['question_text'],
            defaults={
                'question_type': q_data['question_type'],
                'correct_answer': q_data['correct_answer'],
                'difficulty': q_data['difficulty'],
                'skill_id': 'mathematics',
                'is_active': True
            }
        )
        questions.append(question)
        if created:
            print(f"✅ Created question: {question.question_text[:40]}...")
    
    # Create SRS cards with different stages for demonstration
    card_configs = [
        {'question_idx': 0, 'stage': 'apprentice_1', 'ease_factor': 2.5, 'interval': 1, 'due_offset_hours': -2},
        {'question_idx': 1, 'stage': 'apprentice_2', 'ease_factor': 2.6, 'interval': 2, 'due_offset_hours': 0}, 
        {'question_idx': 2, 'stage': 'guru_1', 'ease_factor': 2.4, 'interval': 16, 'due_offset_hours': -5},
        {'question_idx': 3, 'stage': 'apprentice_3', 'ease_factor': 2.7, 'interval': 4, 'due_offset_hours': 1},
        {'question_idx': 4, 'stage': 'master', 'ease_factor': 2.2, 'interval': 64, 'due_offset_hours': -24}
    ]
    
    cards = []
    for config in card_configs:
        question = questions[config['question_idx']]
        
        # Delete existing card if it exists
        SRSCard.objects.filter(student=user, question=question).delete()
        
        # Calculate due date
        due_date = timezone.now() + timedelta(hours=config['due_offset_hours'])
        
        card = SRSCard.objects.create(
            student=user,
            question=question,
            stage=config['stage'],
            ease_factor=config['ease_factor'],
            interval=config['interval'],
            repetition=1 if config['stage'] != 'apprentice_1' else 0,
            due_date=due_date,
            last_reviewed=timezone.now() - timedelta(days=config['interval']),
            correct_streak=2 if 'guru' in config['stage'] else 1,
            total_reviews=3,
            incorrect_count=1,
            average_response_time=5.0 + config['question_idx'] * 2
        )
        cards.append(card)
        print(f"📚 Created SRS card: Stage={config['stage']}, Due={'NOW' if due_date <= timezone.now() else 'FUTURE'}")
    
    return user.id, [str(card.id) for card in cards]

def demo_sm2_algorithm():
    """Demonstrate SM-2 algorithm functionality"""
    print("\n🧠 Demonstrating SM-2 Algorithm...")
    
    user_id, card_ids = create_sample_data()
    scheduler = SM2Scheduler()
    
    print(f"\n📊 Student ID for testing: {user_id}")
    print("🔗 API Endpoints to test:")
    print(f"   GET  /api/v1/practice/{user_id}/due-cards")
    print(f"   GET  /api/v1/practice/{user_id}/stats")
    print(f"   POST /api/v1/practice/review")
    print(f"   GET  /api/v1/practice/{user_id}/optimal-study-set")
    
    # Get due cards
    print("\n📚 Getting due cards...")
    due_cards = scheduler.get_due_cards(str(user_id), limit=10)
    
    print(f"📈 Found {len(due_cards)} due cards:")
    for i, card in enumerate(due_cards[:3], 1):
        print(f"   {i}. Stage: {card['stage']:<15} Priority: {card['priority_score']:.1f} - {card['question_text'][:50]}...")
    
    # Demonstrate review processing
    if due_cards:
        print(f"\n🎯 Demonstrating review processing with card: {card_ids[0]}")
        
        # Simulate correct answer (quality 4)
        result = scheduler.process_review(
            card_id=card_ids[0],
            quality=4,  # Good answer
            response_time=6.5
        )
        
        if result.get('success'):
            print("✅ Review processed successfully!")
            print(f"   Previous stage: {result['previous_state']['stage']}")
            print(f"   New stage: {result['new_state']['stage']}")
            print(f"   Ease factor: {result['previous_state']['ease_factor']:.2f} → {result['new_state']['ease_factor']:.2f}")
            print(f"   Next interval: {result['new_state']['interval']} days")
        else:
            print(f"❌ Review failed: {result.get('error')}")
    
    # Get statistics
    print(f"\n📈 Getting statistics for student {user_id}...")
    stats = scheduler.get_review_statistics(str(user_id), days=30)
    
    if 'error' not in stats:
        print(f"📊 Statistics Summary:")
        print(f"   Total cards: {stats['total_cards']}")
        print(f"   Due now: {stats['due_analysis']['due_now']}")
        print(f"   Success rate: {stats['performance_metrics']['overall_success_rate']:.1%}")
        print(f"   Avg ease factor: {stats['performance_metrics']['average_ease_factor']:.2f}")
        print(f"   Stage distribution: {dict(list(stats['stage_distribution'].items())[:3])}")
    
    print(f"\n🎉 SM-2 Demo Complete! Use student_id={user_id} to test the API endpoints.")
    
    # Generate sample API calls
    print("\n📋 Sample API calls to try:")
    print(f"Invoke-RestMethod -Uri \"http://127.0.0.1:8000/api/v1/practice/{user_id}/due-cards\" -Method GET")
    print(f"Invoke-RestMethod -Uri \"http://127.0.0.1:8000/api/v1/practice/{user_id}/stats\" -Method GET")

if __name__ == "__main__":
    try:
        demo_sm2_algorithm()
        print("\n✨ Demo completed successfully!")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()