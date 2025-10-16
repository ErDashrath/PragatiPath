#!/usr/bin/env python3
"""
Unified Practice History API

This creates a bridge between SM-2 practice system and adaptive learning system
to show unified practice history in the frontend adaptive learning section.

Fixes: "showing the same details as practice history to adaptive learning some fetching problem"
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
import json
import logging

# Import models from both systems
from practice.models import SRSCard
from assessment.models import StudentSession
from core.models import StudentProfile

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def get_unified_practice_history(request, student_id):
    """
    Get unified practice history combining SM-2 spaced repetition and adaptive learning data
    
    This endpoint bridges the gap between:
    1. Practice system (SM-2 spaced repetition) 
    2. Adaptive learning system (BKT/DKT)
    
    Frontend usage: GET /simple/practice-history/<student_id>/
    """
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Get SM-2 practice cards with recent activity
        sm2_cards = SRSCard.objects.filter(
            student=student
        ).select_related('question').order_by('-last_reviewed')[:50]
        
        # Get adaptive learning sessions
        adaptive_sessions = StudentSession.objects.filter(
            student=student,
            status='COMPLETED'
        ).order_by('-session_end_time')[:50]
        
        # Initialize unified history structure
        unified_history = {
            'success': True,
            'student_id': str(student_id),
            'student_name': student.get_full_name() or student.username,
            'total_sessions': 0,
            'practice_sessions': [],
            'adaptive_sessions': [],
            'combined_sessions': [],
            'summary_stats': {
                'total_practice_cards': len(sm2_cards),
                'total_adaptive_sessions': len(adaptive_sessions),
                'practice_mastery_avg': 0.0,
                'adaptive_mastery_avg': 0.0,
            }
        }
        
        # Process SM-2 practice sessions
        practice_mastery_sum = 0.0
        practice_count = 0
        
        for card in sm2_cards:
            if card.last_reviewed:  # Only include reviewed cards
                mastery_level, mastery_score = get_practice_mastery_level(card)
                practice_mastery_sum += mastery_score
                practice_count += 1
                
                practice_data = {
                    'session_id': f'practice_{card.id}',
                    'type': 'practice',
                    'subject': getattr(card.question, 'subject', 'Mixed Practice'),
                    'session_date': card.last_reviewed.strftime('%Y-%m-%d %H:%M'),
                    'stage': card.stage,
                    'ease_factor': round(card.ease_factor, 2),
                    'interval_days': card.interval,
                    'repetitions': card.repetition,
                    'success_rate': round(card.success_rate * 100, 1),
                    'total_reviews': card.total_reviews,
                    'mastery_level': mastery_level,
                    'mastery_score': mastery_score,
                    'question_text': getattr(card.question, 'question_text', 'Practice Question')[:100] + '...',
                    'next_review': card.due_date.strftime('%Y-%m-%d') if card.due_date else None,
                    'is_due': card.due_date <= timezone.now().date() if card.due_date else False,
                    'priority_score': calculate_practice_priority(card)
                }
                unified_history['practice_sessions'].append(practice_data)
                unified_history['combined_sessions'].append(practice_data)
        
        # Process adaptive learning sessions
        adaptive_mastery_sum = 0.0
        adaptive_count = 0
        
        for session in adaptive_sessions:
            session_config = session.session_config or {}
            
            # Extract mastery data
            final_bkt = session_config.get('final_bkt_mastery', 0.0)
            final_dkt = session_config.get('final_dkt_prediction', 0.0)
            
            if final_bkt > 0:  # Only count sessions with mastery data
                adaptive_mastery_sum += final_bkt
                adaptive_count += 1
            
            mastery_level = get_adaptive_mastery_level(final_bkt)
            
            adaptive_data = {
                'session_id': str(session.id),
                'type': 'adaptive',
                'subject': session_config.get('subject', getattr(session.subject, 'name', 'Mixed')),
                'session_date': session.session_end_time.strftime('%Y-%m-%d %H:%M') if session.session_end_time else 'Unknown',
                'duration_minutes': round(session.session_duration_seconds / 60, 1) if session.session_duration_seconds else 0,
                'questions_attempted': session.questions_attempted,
                'questions_correct': session_config.get('correct_answers', 0),
                'accuracy': f"{session.percentage_score:.1f}%" if session.percentage_score else "0%",
                'mastery_scores': {
                    'bkt_mastery': f"{final_bkt:.1%}",
                    'bkt_mastery_raw': final_bkt,
                    'dkt_prediction': f"{final_dkt:.1%}",
                    'dkt_prediction_raw': final_dkt,
                    'mastery_level': mastery_level
                },
                'session_summary': session_config.get('completion_reason', 'Completed'),
                'adaptive_info': {
                    'difficulty_progression': session_config.get('difficulty_progression', []),
                    'mastery_progression': session_config.get('mastery_progression', []),
                    'final_difficulty': session_config.get('final_difficulty', 'medium')
                }
            }
            unified_history['adaptive_sessions'].append(adaptive_data)
            unified_history['combined_sessions'].append(adaptive_data)
        
        # Calculate summary statistics
        unified_history['summary_stats']['practice_mastery_avg'] = round(
            practice_mastery_sum / practice_count if practice_count > 0 else 0.0, 3
        )
        unified_history['summary_stats']['adaptive_mastery_avg'] = round(
            adaptive_mastery_sum / adaptive_count if adaptive_count > 0 else 0.0, 3
        )
        unified_history['total_sessions'] = len(unified_history['combined_sessions'])
        
        # Sort combined sessions by date (most recent first)
        unified_history['combined_sessions'].sort(
            key=lambda x: x['session_date'], 
            reverse=True
        )
        
        # Limit to most recent 30 combined sessions for performance
        unified_history['combined_sessions'] = unified_history['combined_sessions'][:30]
        
        # Add learning insights
        unified_history['learning_insights'] = generate_learning_insights(
            unified_history['practice_sessions'], 
            unified_history['adaptive_sessions']
        )
        
        logger.info(f"Unified practice history generated for student {student_id}: "
                   f"{len(unified_history['practice_sessions'])} practice, "
                   f"{len(unified_history['adaptive_sessions'])} adaptive sessions")
        
        return JsonResponse(unified_history)
        
    except Exception as e:
        logger.error(f"Error generating unified practice history for student {student_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to load unified practice history: {str(e)}',
            'student_id': str(student_id)
        }, status=500)

def get_practice_mastery_level(card):
    """
    Calculate mastery level for SM-2 practice card
    Returns (level_name, numeric_score)
    """
    success_rate = card.success_rate
    stage = card.stage
    
    # Calculate numeric mastery score (0.0 to 1.0)
    base_score = success_rate
    
    # Bonus for advanced stages
    stage_bonus = {
        'graduated': 0.2,
        'review': 0.15,
        'learning': 0.05,
        'new': 0.0
    }.get(stage, 0.0)
    
    # Bonus for high ease factor
    ease_bonus = max(0, (card.ease_factor - 2.5) * 0.1)
    
    mastery_score = min(1.0, base_score + stage_bonus + ease_bonus)
    
    # Determine level name
    if mastery_score >= 0.9 and stage in ['graduated', 'review']:
        level_name = 'expert'
    elif mastery_score >= 0.8:
        level_name = 'advanced'  
    elif mastery_score >= 0.6:
        level_name = 'proficient'
    elif mastery_score >= 0.4:
        level_name = 'developing'
    else:
        level_name = 'novice'
    
    return level_name, mastery_score

def get_adaptive_mastery_level(bkt_mastery):
    """Calculate mastery level name from BKT score"""
    if bkt_mastery >= 0.85:
        return 'expert'
    elif bkt_mastery >= 0.70:
        return 'advanced'
    elif bkt_mastery >= 0.50:
        return 'proficient'
    elif bkt_mastery >= 0.30:
        return 'developing'
    else:
        return 'novice'

def calculate_practice_priority(card):
    """Calculate priority score for practice card (higher = more urgent)"""
    priority = 0.0
    
    # Overdue cards get high priority
    if card.due_date and card.due_date <= timezone.now().date():
        days_overdue = (timezone.now().date() - card.due_date).days
        priority += min(10.0, days_overdue * 2.0)  # Up to 10 points for overdue
    
    # Low success rate increases priority
    if card.success_rate < 0.7:
        priority += (0.7 - card.success_rate) * 5.0  # Up to 3.5 points
    
    # New or struggling cards get priority
    if card.stage in ['new', 'learning']:
        priority += 2.0
    
    # Cards with low ease factor need attention
    if card.ease_factor < 2.0:
        priority += (2.0 - card.ease_factor) * 2.0
    
    return round(priority, 2)

def generate_learning_insights(practice_sessions, adaptive_sessions):
    """Generate insights about learning patterns"""
    insights = []
    
    # Practice insights
    if practice_sessions:
        # Find most practiced subjects
        subject_counts = {}
        total_reviews = 0
        
        for session in practice_sessions:
            subject = session['subject']
            subject_counts[subject] = subject_counts.get(subject, 0) + session['total_reviews']
            total_reviews += session['total_reviews']
        
        if subject_counts:
            top_subject = max(subject_counts, key=subject_counts.get)
            insights.append(f"Most practiced: {top_subject} ({subject_counts[top_subject]} reviews)")
        
        # Check for due cards
        due_count = sum(1 for session in practice_sessions if session.get('is_due', False))
        if due_count > 0:
            insights.append(f"{due_count} practice cards are due for review")
    
    # Adaptive learning insights
    if adaptive_sessions:
        # Recent performance trend
        recent_accuracies = []
        for session in adaptive_sessions[:5]:  # Last 5 sessions
            try:
                accuracy = float(session['accuracy'].replace('%', ''))
                recent_accuracies.append(accuracy)
            except:
                continue
        
        if len(recent_accuracies) >= 3:
            avg_accuracy = sum(recent_accuracies) / len(recent_accuracies)
            insights.append(f"Recent adaptive accuracy: {avg_accuracy:.1f}%")
            
            if len(recent_accuracies) >= 5:
                trend = recent_accuracies[0] - recent_accuracies[-1]  # Most recent vs oldest
                if trend > 10:
                    insights.append("📈 Your accuracy is improving!")
                elif trend < -10:
                    insights.append("📉 Consider reviewing fundamentals")
    
    # Combined insights
    if practice_sessions and adaptive_sessions:
        insights.append("🎯 You're using both practice methods - great strategy!")
    elif practice_sessions:
        insights.append("💡 Try adaptive learning for personalized difficulty")
    elif adaptive_sessions:
        insights.append("💡 Try spaced repetition practice for better retention")
    
    return insights[:5]  # Limit to 5 insights

# URL pattern for integration
def get_url_pattern():
    """Return URL pattern for Django urls.py integration"""
    from django.urls import path
    return path('simple/practice-history/<str:student_id>/', get_unified_practice_history, name='get_unified_practice_history')

if __name__ == "__main__":
    print("🔧 Unified Practice History API")
    print("This bridges SM-2 practice and adaptive learning systems")
    print("Add to urls.py:")
    print("  path('simple/practice-history/<str:student_id>/', unified_practice_history_api.get_unified_practice_history)")