from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg, Q
from .models import AdaptiveQuestion, Interaction
from .serializers import (
    ChapterQuestionSerializer, 
    QuestionListSerializer,
    SubjectStatsSerializer,
    ChapterStatsSerializer
)
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def list_subjects_with_chapters(request):
    """List all subjects with their chapters and question counts"""
    try:
        subjects_data = []
        
        # Define chapter mappings based on CSV structure
        chapter_mappings = {
            'quantitative_aptitude': {
                'name': 'Quantitative Aptitude',
                'chapters': [
                    {'id': 1, 'name': 'Percentages', 'csv_tag': 'percentages'},
                    {'id': 2, 'name': 'Ratios and Proportions', 'csv_tag': 'ratios_and_proportions'},
                    {'id': 3, 'name': 'Profit and Loss', 'csv_tag': 'profit_and_loss'}
                ]
            },
            'logical_reasoning': {
                'name': 'Logical Reasoning', 
                'chapters': [
                    {'id': 1, 'name': 'Pattern Recognition', 'csv_tag': 'pattern_recognition'},
                    {'id': 2, 'name': 'Syllogisms', 'csv_tag': 'syllogisms'},
                    {'id': 3, 'name': 'Data Interpretation General', 'csv_tag': 'data_interpretation_general'}
                ]
            },
            'verbal_ability': {
                'name': 'Verbal Ability & Reading Comprehension',
                'chapters': [
                    {'id': 1, 'name': 'Vocabulary', 'csv_tag': 'vocabulary'},
                    {'id': 2, 'name': 'Grammar', 'csv_tag': 'grammar'},
                    {'id': 3, 'name': 'Reading Comprehension', 'csv_tag': 'reading_comprehension'}
                ]
            },
            'data_interpretation': {
                'name': 'Data Interpretation',
                'chapters': [
                    {'id': 1, 'name': 'Bar Charts', 'csv_tag': 'bar_charts'},
                    {'id': 2, 'name': 'Line Graphs', 'csv_tag': 'line_graphs'},
                    {'id': 3, 'name': 'Pie Charts', 'csv_tag': 'pie_charts'}
                ]
            }
        }
        
        for subject_code, subject_info in chapter_mappings.items():
            # Get total questions for subject
            total_questions = AdaptiveQuestion.objects.filter(
                subject=subject_code, is_active=True
            ).count()
            
            # Get chapter-wise question counts
            chapters_with_counts = []
            for chapter in subject_info['chapters']:
                # Count questions that have this chapter's CSV tag in their tags
                question_count = AdaptiveQuestion.objects.filter(
                    subject=subject_code,
                    is_active=True,
                    tags__icontains=chapter['csv_tag']
                ).count()
                
                chapters_with_counts.append({
                    'id': chapter['id'],
                    'name': chapter['name'],
                    'question_count': question_count,
                    'csv_tag': chapter['csv_tag']
                })
            
            # Get difficulty breakdown
            difficulty_breakdown = {}
            difficulty_counts = AdaptiveQuestion.objects.filter(
                subject=subject_code, is_active=True
            ).values('difficulty_level').annotate(count=Count('id'))
            
            for item in difficulty_counts:
                difficulty_breakdown[item['difficulty_level']] = item['count']
            
            subjects_data.append({
                'subject_code': subject_code,
                'subject_name': subject_info['name'],
                'total_questions': total_questions,
                'chapters': chapters_with_counts,
                'difficulty_breakdown': difficulty_breakdown
            })
        
        return Response({
            'success': True,
            'total_subjects': len(subjects_data),
            'subjects': subjects_data
        })
        
    except Exception as e:
        logger.error(f"Error listing subjects with chapters: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def get_chapter_questions(request):
    """Get questions for a specific chapter within a subject"""
    try:
        data = request.data
        subject = data.get('subject')
        chapter_id = data.get('chapter_id')
        difficulty_level = data.get('difficulty_level')
        count = int(data.get('count', 10))
        
        if not subject or not chapter_id:
            return Response({
                'success': False,
                'error': 'Subject and chapter_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Chapter mapping to CSV tags
        chapter_mappings = {
            'quantitative_aptitude': {
                1: 'percentages',
                2: 'ratios_and_proportions', 
                3: 'profit_and_loss'
            },
            'logical_reasoning': {
                1: 'pattern_recognition',
                2: 'syllogisms',
                3: 'data_interpretation_general'
            },
            'verbal_ability': {
                1: 'vocabulary',
                2: 'grammar',
                3: 'reading_comprehension'
            },
            'data_interpretation': {
                1: 'bar_charts',
                2: 'line_graphs', 
                3: 'pie_charts'
            }
        }
        
        csv_tag = chapter_mappings.get(subject, {}).get(int(chapter_id))
        if not csv_tag:
            return Response({
                'success': False,
                'error': f'Invalid chapter_id {chapter_id} for subject {subject}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build query filters
        filters = Q(subject=subject, is_active=True, tags__icontains=csv_tag)
        
        if difficulty_level:
            filters &= Q(difficulty_level=difficulty_level)
        
        # Get questions
        questions = AdaptiveQuestion.objects.filter(filters).order_by('?')[:count]
        
        # Serialize questions (without exposing correct answers)
        serializer = ChapterQuestionSerializer(questions, many=True)
        
        return Response({
            'success': True,
            'subject': subject,
            'chapter_id': chapter_id,
            'chapter_tag': csv_tag,
            'difficulty_level': difficulty_level,
            'requested_count': count,
            'returned_count': len(serializer.data),
            'questions': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error getting chapter questions: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_chapter_stats(request, subject, chapter_id):
    """Get statistics for a specific chapter"""
    try:
        # Chapter mapping to CSV tags
        chapter_mappings = {
            'quantitative_aptitude': {
                1: 'percentages',
                2: 'ratios_and_proportions',
                3: 'profit_and_loss'
            },
            'logical_reasoning': {
                1: 'pattern_recognition', 
                2: 'syllogisms',
                3: 'data_interpretation_general'
            },
            'verbal_ability': {
                1: 'vocabulary',
                2: 'grammar',
                3: 'reading_comprehension'
            },
            'data_interpretation': {
                1: 'bar_charts',
                2: 'line_graphs',
                3: 'pie_charts'
            }
        }
        
        csv_tag = chapter_mappings.get(subject, {}).get(int(chapter_id))
        if not csv_tag:
            return Response({
                'success': False,
                'error': f'Invalid chapter_id {chapter_id} for subject {subject}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get chapter questions
        chapter_questions = AdaptiveQuestion.objects.filter(
            subject=subject,
            is_active=True,
            tags__icontains=csv_tag
        )
        
        # Calculate statistics
        total_questions = chapter_questions.count()
        
        # Difficulty breakdown
        difficulty_counts = chapter_questions.values('difficulty_level').annotate(
            count=Count('id')
        )
        difficulty_breakdown = {item['difficulty_level']: item['count'] for item in difficulty_counts}
        
        # Success rate
        avg_success_rate = chapter_questions.aggregate(
            avg_rate=Avg('times_correct') / Avg('times_attempted') if chapter_questions.filter(times_attempted__gt=0).exists() else 0
        )['avg_rate'] or 0
        
        return Response({
            'success': True,
            'subject': subject,
            'chapter_id': chapter_id,
            'chapter_tag': csv_tag,
            'total_questions': total_questions,
            'difficulty_breakdown': difficulty_breakdown,
            'avg_success_rate': round(avg_success_rate, 2)
        })
        
    except Exception as e:
        logger.error(f"Error getting chapter stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_chapter_answer(request):
    """Submit answer for a chapter question with proper tracking"""
    try:
        data = request.data
        question_id = data.get('question_id')
        student_answer = data.get('answer')
        response_time = float(data.get('response_time', 0))
        subject = data.get('subject')
        chapter_id = data.get('chapter_id')
        
        if not all([question_id, student_answer, subject, chapter_id]):
            return Response({
                'success': False,
                'error': 'question_id, answer, subject, and chapter_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get question
        try:
            question = AdaptiveQuestion.objects.get(id=question_id, is_active=True)
        except AdaptiveQuestion.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Question not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if answer is correct
        is_correct = student_answer.lower() == question.answer.lower()
        
        # Update question statistics
        question.times_attempted += 1
        if is_correct:
            question.times_correct += 1
        question.save()
        
        # Create interaction record (you might need to create a user first)
        # For now, we'll just return the result
        
        return Response({
            'success': True,
            'question_id': question_id,
            'is_correct': is_correct,
            'correct_answer': question.answer,
            'correct_option_text': question.correct_option_text,
            'explanation': f"The correct answer is {question.answer.upper()}: {question.correct_option_text}",
            'response_time': response_time,
            'subject': subject,
            'chapter_id': chapter_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting chapter answer: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)