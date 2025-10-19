"""
Enhanced Exam Session API with Adaptive Learning Integration
Handles student exam taking with BKT-based adaptive question delivery
"""

import json
import uuid
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from assessment.models import (
    EnhancedExam, 
    StudentExamAttempt, 
    ExamQuestionAttempt, 
    AdaptiveQuestion
)
from assessment.improved_models import Subject, Chapter, StudentSession
from assessment.adaptive_session_manager import AdaptiveSessionManager
from core.models import StudentProfile
from student_model.bkt import BKTService

import logging
logger = logging.getLogger(__name__)

# Initialize services
adaptive_manager = AdaptiveSessionManager()
bkt_service = BKTService()

@csrf_exempt
@require_http_methods(["POST"])
def join_enhanced_exam(request, exam_id):
    """
    Student joins an enhanced exam and creates adaptive session
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        student_id = data.get('student_id')
        
        if not username and not student_id:
            return JsonResponse({
                'success': False,
                'error': 'Username or student_id is required'
            }, status=400)

        # Get user and student profile
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(id=student_id)
                username = user.username  # Set username for logging
            student_profile = user.student_profile
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Student not found'
            }, status=404)
        except StudentProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Student profile not found'
            }, status=404)

        # Get exam
        try:
            exam = EnhancedExam.objects.get(id=exam_id)
        except EnhancedExam.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Exam not found'
            }, status=404)

        # Check if exam is available
        if not exam.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Exam is not currently available'
            }, status=400)

        # Check if student has already attempted this exam
        existing_attempt = StudentExamAttempt.objects.filter(
            exam=exam,
            student=user
        ).first()

        if existing_attempt and existing_attempt.status in ['COMPLETED', 'SUBMITTED']:
            return JsonResponse({
                'success': False,
                'error': 'You have already completed this exam'
            }, status=400)

        # Check if student has an active attempt
        if existing_attempt and existing_attempt.status == 'IN_PROGRESS':
            # Resume existing session
            session_id = existing_attempt.id
            logger.info(f"🔄 Resuming exam session {session_id} for {username}")
        else:
            # Create new exam attempt with transaction
            with transaction.atomic():
                session_id = str(uuid.uuid4())
                
                exam_attempt = StudentExamAttempt.objects.create(
                    id=session_id,
                    exam=exam,
                    student=user,
                    student_profile=student_profile,
                    status='IN_PROGRESS',
                    started_at=timezone.now(),
                    attempt_number=1,
                    total_questions=exam.total_questions,
                    questions_attempted=0,
                    questions_answered=0,
                    correct_answers=0,
                    total_time_spent_seconds=0,
                    final_score_percentage=0.0
                )
                
                logger.info(f"✅ Created new exam session {session_id} for {username}")

        # Create adaptive learning session for question delivery
        adaptive_session = adaptive_manager.start_adaptive_session(
            student_id=user.id,  # Use integer user ID, not UUID
            subject_code=exam.subject.name.lower().replace(' ', '_'),  # Convert subject name to code
            chapter_id=exam.chapters.first().id if exam.chapters.exists() else None,
            max_questions=exam.total_questions
        )
        
        if not adaptive_session['success']:
            return JsonResponse({
                'success': False,
                'error': f'Failed to create adaptive session: {adaptive_session.get("error_message", "Unknown error")}'
            }, status=500)

        # Store adaptive session ID in exam attempt session_data
        exam_attempt_obj = StudentExamAttempt.objects.get(id=session_id)
        exam_attempt_obj.session_data = exam_attempt_obj.session_data or {}
        exam_attempt_obj.session_data['adaptive_session_id'] = adaptive_session['session_id']
        exam_attempt_obj.save()

        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'adaptive_session_id': adaptive_session['session_id'],
            'exam_name': exam.exam_name,
            'total_questions': exam.total_questions,
            'duration_minutes': exam.duration_minutes,
            'message': 'Successfully joined exam session'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Error joining exam: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to join exam: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_exam_question(request, session_id):
    """
    Get next adaptive question for the exam session
    """
    try:
        # Get exam attempt
        try:
            exam_attempt = StudentExamAttempt.objects.get(id=session_id)
        except StudentExamAttempt.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Exam session not found'
            }, status=404)

        # Check if session is still active
        if exam_attempt.status != 'IN_PROGRESS':
            return JsonResponse({
                'success': False,
                'error': 'Exam session is not active',
                'session_status': exam_attempt.status
            }, status=400)

        # Check time limit
        if exam_attempt.started_at:
            elapsed_minutes = (timezone.now() - exam_attempt.started_at).total_seconds() / 60
            if elapsed_minutes > exam_attempt.exam.duration_minutes:
                # Auto-submit due to time limit
                exam_attempt.status = 'TIMEOUT'
                exam_attempt.submitted_at = timezone.now()
                exam_attempt.save()
                
                return JsonResponse({
                    'success': False,
                    'error': 'Exam time limit exceeded',
                    'session_status': 'TIMEOUT'
                }, status=400)

        # Get adaptive session ID
        adaptive_session_id = exam_attempt.session_data.get('adaptive_session_id') if exam_attempt.session_data else None
        
        if not adaptive_session_id:
            return JsonResponse({
                'success': False,
                'error': 'Adaptive session not found'
            }, status=500)

        # Get next question using adaptive system
        question_result = adaptive_manager.get_next_question(adaptive_session_id)
        
        if not question_result['success']:
            # End exam if no more questions
            exam_attempt.status = 'COMPLETED'
            exam_attempt.submitted_at = timezone.now()
            exam_attempt.save()
            
            return JsonResponse({
                'success': True,
                'exam_completed': True,
                'message': 'Exam completed - no more questions available',
                'final_score': exam_attempt.final_score_percentage
            })

        question = question_result['question']
        
        # Format question for frontend
        formatted_question = {
            'question_id': str(question['id']),
            'question_number': exam_attempt.questions_attempted + 1,
            'total_questions': exam_attempt.exam.total_questions,
            'question_text': question['text'],  # Note: adaptive manager returns 'text' not 'question_text'
            'options': [
                {'id': 'a', 'text': question['options'][0]},  # Note: adaptive manager returns options as array
                {'id': 'b', 'text': question['options'][1]},
                {'id': 'c', 'text': question['options'][2]},
                {'id': 'd', 'text': question['options'][3]}
            ],
            'difficulty': question_result.get('current_difficulty', 'moderate'),
            'subject': exam_attempt.exam.subject.name,
            'time_remaining_minutes': max(0, exam_attempt.exam.duration_minutes - 
                                        ((timezone.now() - exam_attempt.started_at).total_seconds() / 60)),
            'current_mastery': question_result.get('current_mastery', 0.5)
        }

        return JsonResponse({
            'success': True,
            'question': formatted_question
        })

    except Exception as e:
        logger.error(f"❌ Error getting exam question: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to get question: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_exam_answer(request, session_id):
    """
    Submit answer for current question and update BKT state
    """
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_taken = data.get('time_taken', 0)
        
        if not question_id or not selected_answer:
            return JsonResponse({
                'success': False,
                'error': 'Question ID and selected answer are required'
            }, status=400)

        # Get exam attempt
        exam_attempt = StudentExamAttempt.objects.get(id=session_id)
        
        # Get question
        question = AdaptiveQuestion.objects.get(id=question_id)
        
        # Check correct answer
        is_correct = selected_answer.lower() == question.answer.lower()
        
        # Submit to adaptive system
        adaptive_session_id = exam_attempt.session_data.get('adaptive_session_id')
        submit_result = adaptive_manager.submit_answer(
            adaptive_session_id,
            str(question_id),
            selected_answer,
            float(time_taken)
        )
        
        if not submit_result['success']:
            return JsonResponse({
                'success': False,
                'error': f'Failed to submit to adaptive system: {submit_result.get("error_message", "Unknown error")}'
            }, status=500)

        # Create or update exam question attempt record
        with transaction.atomic():
            question_attempt, created = ExamQuestionAttempt.objects.get_or_create(
                exam_attempt=exam_attempt,
                question=question,
                defaults={
                    'student': exam_attempt.student,
                    'question_number': exam_attempt.questions_attempted + 1,
                    'presented_order': exam_attempt.questions_attempted + 1,
                    'student_answer': selected_answer,
                    'correct_answer': question.answer,
                    'is_correct': is_correct,
                    'answer_status': 'ANSWERED',
                    'total_time_spent_seconds': int(time_taken),
                    'thinking_time_seconds': int(time_taken),
                    'difficulty_when_presented': question.difficulty_level,
                    'first_viewed_at': timezone.now(),
                    'first_answered_at': timezone.now(),
                    'final_answered_at': timezone.now(),
                    'points_earned': 1.0 if is_correct else 0.0
                }
            )
            
            # If record already existed, update it
            if not created:
                question_attempt.student_answer = selected_answer
                question_attempt.is_correct = is_correct
                question_attempt.answer_status = 'ANSWERED'
                question_attempt.total_time_spent_seconds = int(time_taken)
                question_attempt.final_answered_at = timezone.now()
                question_attempt.points_earned = 1.0 if is_correct else 0.0
                question_attempt.save()
            
            # Recalculate exam attempt statistics from actual records
            total_questions = ExamQuestionAttempt.objects.filter(exam_attempt=exam_attempt).count()
            correct_count = ExamQuestionAttempt.objects.filter(exam_attempt=exam_attempt, is_correct=True).count()
            
            exam_attempt.questions_attempted = total_questions
            exam_attempt.questions_answered = total_questions
            exam_attempt.correct_answers = correct_count
            exam_attempt.incorrect_answers = total_questions - correct_count
            
            # Calculate current score
            exam_attempt.final_score_percentage = (
                (exam_attempt.correct_answers / exam_attempt.questions_answered) * 100
                if exam_attempt.questions_answered > 0 else 0
            )
            
            exam_attempt.save()

        logger.info(f"📝 Answer submitted - Question: {question_id}, Correct: {is_correct}, Score: {exam_attempt.final_score_percentage:.1f}%")

        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'current_score': exam_attempt.final_score_percentage,
            'questions_answered': exam_attempt.questions_answered,
            'correct_answers': exam_attempt.correct_answers,
            'mastery_update': submit_result.get('mastery_update', {}),
            'message': 'Answer submitted successfully'
        })

    except StudentExamAttempt.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Exam session not found'
        }, status=404)
    except AdaptiveQuestion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Question not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error submitting answer: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to submit answer: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_exam(request, session_id):
    """
    Submit/End exam session with confirmation
    """
    try:
        data = json.loads(request.body)
        force_submit = data.get('force_submit', False)
        
        # Get exam attempt
        exam_attempt = StudentExamAttempt.objects.get(id=session_id)
        
        if exam_attempt.status != 'IN_PROGRESS':
            return JsonResponse({
                'success': False,
                'error': 'Exam session is not active'
            }, status=400)

        # If not force submit, return confirmation prompt
        if not force_submit:
            return JsonResponse({
                'success': True,
                'requires_confirmation': True,
                'message': 'Are you sure you want to end the exam? This action cannot be undone.',
                'current_progress': {
                    'questions_answered': exam_attempt.questions_answered,
                    'total_questions': exam_attempt.exam.total_questions,
                    'current_score': exam_attempt.final_score_percentage,
                    'time_elapsed_minutes': (timezone.now() - exam_attempt.started_at).total_seconds() / 60
                }
            })

        # Process final submission
        with transaction.atomic():
            exam_attempt.status = 'SUBMITTED'
            exam_attempt.submitted_at = timezone.now()
            exam_attempt.total_time_spent_seconds = (timezone.now() - exam_attempt.started_at).total_seconds()
            
            # Determine if passed
            passing_score = exam_attempt.exam.passing_score_percentage
            exam_attempt.passed = exam_attempt.final_score_percentage >= passing_score
            
            # Calculate grade
            exam_attempt.grade = exam_attempt.calculate_grade()
            
            exam_attempt.save()
            
            # Note: Adaptive session will be automatically finalized when max questions reached
            # or when session is marked as complete

        logger.info(f"✅ Exam submitted - Session: {session_id}, Score: {exam_attempt.final_score_percentage:.1f}%, Grade: {exam_attempt.grade}")

        return JsonResponse({
            'success': True,
            'exam_completed': True,
            'results': {
                'final_score_percentage': float(exam_attempt.final_score_percentage),
                'grade': exam_attempt.grade,
                'passed': exam_attempt.passed,
                'questions_answered': exam_attempt.questions_answered,
                'correct_answers': exam_attempt.correct_answers,
                'total_time_minutes': round(exam_attempt.total_time_spent_seconds / 60, 2),
                'submitted_at': exam_attempt.submitted_at.isoformat()
            }
        })

    except StudentExamAttempt.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Exam session not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error submitting exam: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to submit exam: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_exam_results(request, session_id):
    """
    Get detailed exam results and analytics
    """
    try:
        # Get exam attempt
        exam_attempt = StudentExamAttempt.objects.get(id=session_id)
        
        if exam_attempt.status not in ['SUBMITTED', 'COMPLETED', 'TIMEOUT']:
            return JsonResponse({
                'success': False,
                'error': 'Exam results not available yet'
            }, status=400)

        # Get question attempts
        question_attempts = ExamQuestionAttempt.objects.filter(
            session=exam_attempt
        ).select_related('question').order_by('answered_at')

        # Calculate detailed analytics
        question_results = []
        subject_performance = {}
        difficulty_performance = {}
        
        for attempt in question_attempts:
            question_data = {
                'question_id': str(attempt.question.id),
                'question_text': attempt.question.question_text,
                'student_answer': attempt.student_answer,
                'correct_answer': attempt.correct_answer,
                'is_correct': attempt.is_correct,
                'time_taken': attempt.time_spent_seconds,
                'difficulty': attempt.question.difficulty_level,
                'subject': attempt.question.subject
            }
            question_results.append(question_data)
            
            # Subject performance tracking
            subject = attempt.question.subject
            if subject not in subject_performance:
                subject_performance[subject] = {'total': 0, 'correct': 0}
            subject_performance[subject]['total'] += 1
            if attempt.is_correct:
                subject_performance[subject]['correct'] += 1
                
            # Difficulty performance tracking
            difficulty = attempt.question.difficulty_level
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {'total': 0, 'correct': 0}
            difficulty_performance[difficulty]['total'] += 1
            if attempt.is_correct:
                difficulty_performance[difficulty]['correct'] += 1

        # Calculate percentages
        for subject_data in subject_performance.values():
            subject_data['percentage'] = (subject_data['correct'] / subject_data['total']) * 100
            
        for difficulty_data in difficulty_performance.values():
            difficulty_data['percentage'] = (difficulty_data['correct'] / difficulty_data['total']) * 100

        return JsonResponse({
            'success': True,
            'exam_results': {
                'exam_name': exam_attempt.exam.exam_name,
                'student_name': exam_attempt.student.get_full_name() or exam_attempt.student.username,
                'final_score_percentage': float(exam_attempt.final_score_percentage),
                'grade': exam_attempt.grade,
                'passed': exam_attempt.passed,
                'questions_answered': exam_attempt.questions_answered,
                'correct_answers': exam_attempt.correct_answers,
                'total_time_minutes': round(exam_attempt.total_time_spent_seconds / 60, 2),
                'started_at': exam_attempt.started_at.isoformat(),
                'submitted_at': exam_attempt.submitted_at.isoformat() if exam_attempt.submitted_at else None,
                'status': exam_attempt.status
            },
            'question_breakdown': question_results,
            'analytics': {
                'subject_performance': subject_performance,
                'difficulty_performance': difficulty_performance,
                'average_time_per_question': exam_attempt.total_time_spent_seconds / exam_attempt.questions_answered if exam_attempt.questions_answered > 0 else 0
            }
        })

    except StudentExamAttempt.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Exam session not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting exam results: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to get exam results: {str(e)}'
        }, status=500)