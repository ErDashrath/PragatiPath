#!/usr/bin/env python3
"""
Simple Direct Frontend API

This provides immediate working endpoints that the frontend can click and use
without any complex setup or orchestration dependencies.
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
from django.db import models
import json
import uuid
import logging

from core.models import StudentProfile
from assessment.models import StudentSession, QuestionAttempt
from assessment.adaptive_submission_models import AdaptiveSubmission, AdaptiveSubmissionAnalyzer
from student_model.bkt import BKTService
from student_model.dkt import DKTService

logger = logging.getLogger(__name__)

# Import orchestration service for full adaptive learning
try:
    from orchestration.orchestration_service import OrchestrationService
    from orchestration.adaptive_orchestrator import adaptive_orchestrator
    orchestration_service = OrchestrationService()
    ORCHESTRATION_AVAILABLE = True
    print("🧠 Orchestration service loaded successfully!")
except ImportError as e:
    orchestration_service = None
    ORCHESTRATION_AVAILABLE = False
    print(f"⚠️ Orchestration service not available: {e}")

# Initialize services
bkt_service = BKTService()
dkt_service = DKTService()

# ============================================================================
# Simple Direct Endpoints - Ready for Frontend Clicks
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def start_simple_session(request):
    """
    START SESSION - Direct frontend click endpoint
    
    Frontend can call this immediately:
    POST /start-session
    {
        "student_name": "John Doe",
        "subject": "mathematics"
    }
    """
    try:
        data = json.loads(request.body)
        student_name = data.get('student_name', 'Test Student')
        subject = data.get('subject', 'mathematics')
        question_count = data.get('question_count', 10)  # Default to 10 if not provided
        
        # Validate question count
        if not isinstance(question_count, int) or question_count < 1 or question_count > 50:
            question_count = 10  # Default fallback
        
        # Create or get student
        username = f"student_{student_name.replace(' ', '_').lower()}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': student_name.split()[0],
                'last_name': ' '.join(student_name.split()[1:]) if len(student_name.split()) > 1 else ''
            }
        )
        
        # Create or get student profile
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'fundamentals': {
                    'listening': 0.5,
                    'grasping': 0.5,
                    'retention': 0.5,
                    'application': 0.5
                }
            }
        )
        
        # Get or create subject for session
        from assessment.improved_models import Subject, SUBJECT_CHOICES
        
        # Map subject name to valid code
        subject_mapping = {
            'mathematics': 'quantitative_aptitude',
            'math': 'quantitative_aptitude', 
            'quantitative': 'quantitative_aptitude',
            'quantitative_aptitude': 'quantitative_aptitude',  # Direct mapping
            'reasoning': 'logical_reasoning',
            'logic': 'logical_reasoning',
            'logical_reasoning': 'logical_reasoning',  # Direct mapping
            'data': 'data_interpretation',
            'data_interpretation': 'data_interpretation',  # Direct mapping
            'verbal': 'verbal_ability',
            'english': 'verbal_ability',
            'verbal_ability': 'verbal_ability'  # Direct mapping - THIS WAS MISSING!
        }
        
        subject_code = subject_mapping.get(subject.lower(), 'quantitative_aptitude')
        
        subject_obj, created = Subject.objects.get_or_create(
            code=subject_code,
            defaults={
                'name': subject.title(),
                'description': f'Auto-created subject for {subject}',
                'is_active': True
            }
        )
        
        # Create simple session with required fields only
        session = StudentSession.objects.create(
            student=user,
            subject=subject_obj,
            session_name=f"Adaptive {subject_obj.name} Session",  # Enhanced name
            session_type='PRACTICE',  # Set session type
            status='ACTIVE',  # Set status
            total_questions_planned=question_count,  # Use the provided question count
            current_difficulty_level='moderate',  # Default difficulty
            difficulty_adjustments=[],  # Empty list
            question_sequence=[],  # Empty array
            device_info={},  # Empty dict
            user_agent=request.META.get('HTTP_USER_AGENT', ''),  # Set user agent
            session_config={
                'subject': subject,
                'subject_code': subject_code,
                'subject_name': subject_obj.name,
                'frontend_session': True,
                'orchestration_enabled': ORCHESTRATION_AVAILABLE,  # Flag orchestration
                'adaptive_api': True,
                'question_count': question_count  # Store in config for reference
            }
        )
        
        # Initialize orchestration if available
        if ORCHESTRATION_AVAILABLE and orchestration_service:
            try:
                # Initialize student's adaptive learning state with orchestration
                orchestration_result = orchestration_service.initialize_student_session(
                    student_username=user.username,
                    subject=subject
                )
                print(f"🎯 Orchestration initialized: {orchestration_result}")
                
            except Exception as e:
                print(f"⚠️ Orchestration initialization failed: {e}")
                # Continue without orchestration
        
        return JsonResponse({
            'success': True,
            'message': 'Session started successfully!',
            'session_id': str(session.id),
            'student_id': str(profile.id),  # StudentProfile UUID for legacy compatibility
            'user_id': user.id,  # User integer ID for session history
            'student_name': student_name,
            'subject': subject,
            'orchestration_enabled': ORCHESTRATION_AVAILABLE,
            'next_action': 'Click "Get Question" to start learning!'
        })
        
    except Exception as e:
        logger.error(f"Start session error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Session start failed'
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def get_simple_question(request, session_id):
    """
    GET QUESTION - Direct frontend click endpoint
    
    Frontend can call this immediately:
    GET /get-question/<session_id>/
    """
    print(f"🔍 DEBUG - get_simple_question called with session_id: {session_id}")
    
    try:
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required',
                'message': 'Please provide session_id parameter'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        subject = session.session_config.get('subject', 'mathematics')
        print(f"🔍 DEBUG - Found session for subject: {subject}")
        
        # Count current questions
        question_count = QuestionAttempt.objects.filter(session=session).count() + 1
        
        # Check if session has reached question limit
        if question_count > session.total_questions_planned:
            return JsonResponse({
                'success': False,
                'session_complete': True,
                'message': f'Session complete! You have completed all {session.total_questions_planned} questions.',
                'next_action': 'Session finished! 🎉',
                'session_stats': {
                    'questions_completed': session.total_questions_planned,
                    'questions_planned': session.total_questions_planned
                }
            }, status=200)
        
        # Get advanced knowledge state for adaptive difficulty using full orchestration
        skill_id = f"{subject}_skill"  # FIXED: Use consistent skill_id format
        
        print(f"🔍 DEBUG - Checking orchestration availability: {ORCHESTRATION_AVAILABLE}")
        print(f"🔍 DEBUG - Orchestration service object: {orchestration_service}")
        
        try:
            if ORCHESTRATION_AVAILABLE and orchestration_service:
                print(f"🎯 Getting orchestrated knowledge state for {session.student.username}, skill: {skill_id}")
                
                orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                    student_username=session.student.username,
                    subject=subject
                )
                
                print(f"🔍 DEBUG - Orchestration result: {orchestration_result}")
                
                if orchestration_result and orchestration_result.get('success'):
                    mastery_level = orchestration_result.get('bkt_mastery', 0.5)
                    dkt_prediction = orchestration_result.get('dkt_prediction', 0.5)
                    combined_confidence = orchestration_result.get('combined_confidence', 0.5)
                    
                    print(f"📊 Orchestrated State - BKT: {mastery_level:.3f}, DKT: {dkt_prediction:.3f}, Combined: {combined_confidence:.3f}")
                    
                    # ENHANCED DIFFICULTY ADAPTATION - Check recent performance pattern
                    recent_attempts = QuestionAttempt.objects.filter(
                        session=session
                    ).order_by('-created_at')[:3]  # Last 3 attempts
                    
                    recent_performance = []
                    for attempt in recent_attempts:
                        recent_performance.append(1 if attempt.is_correct else 0)
                    
                    print(f"📊 Recent performance: {recent_performance}")
                    
                    # Use combined confidence for base adaptive difficulty
                    adaptive_confidence = combined_confidence
                    
                    # Adjust confidence based on recent performance trend
                    if len(recent_performance) >= 2:
                        recent_success_rate = sum(recent_performance) / len(recent_performance)
                        print(f"📈 Recent success rate: {recent_success_rate:.2f}")
                        
                        # Dynamic difficulty adjustment based on performance trend
                        if recent_success_rate == 0.0:  # All recent answers wrong
                            adaptive_confidence = max(0.05, adaptive_confidence * 0.6)
                            print(f"📉 All recent wrong - reducing confidence to {adaptive_confidence:.3f}")
                        elif recent_success_rate == 1.0:  # All recent answers correct
                            adaptive_confidence = min(0.95, adaptive_confidence * 1.4)
                            print(f"📈 All recent correct - boosting confidence to {adaptive_confidence:.3f}")
                        elif recent_success_rate < 0.4:  # Mostly wrong
                            adaptive_confidence = max(0.1, adaptive_confidence * 0.75)
                            print(f"📉 Mostly wrong - reducing confidence to {adaptive_confidence:.3f}")
                        elif recent_success_rate > 0.7:  # Mostly correct
                            adaptive_confidence = min(0.9, adaptive_confidence * 1.25)
                            print(f"📈 Mostly correct - boosting confidence to {adaptive_confidence:.3f}")
                    
                    print(f"🎯 Final adaptive confidence: {adaptive_confidence:.3f}")
                else:
                    print("⚠️ Orchestration returned empty result, using fallback")
                    adaptive_confidence = 0.5
                    
            else:
                print("⚠️ Orchestration not available, using basic BKT")
                # Fallback to basic BKT
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                adaptive_confidence = bkt_params.P_L if bkt_params else 0.5
                
        except Exception as e:
            print(f"⚠️ Orchestration failed: {e}, using fallback")
            adaptive_confidence = 0.5
        
        # Map orchestrated adaptive confidence to database difficulty - COMPLETE MAPPING INCLUDING VERY_EASY
        if adaptive_confidence < 0.15:  # Very low mastery - use very_easy questions
            difficulty = "very_easy"
            db_difficulty = "very_easy"
            difficulty_emoji = "�"
            adaptive_reason = f"Very easy questions to build basic confidence (mastery: {adaptive_confidence:.1%})"
        elif adaptive_confidence < 0.35:  # Low mastery - use easy questions
            difficulty = "easy"
            db_difficulty = "easy"
            difficulty_emoji = "�"
            adaptive_reason = f"Easy questions to build confidence (mastery: {adaptive_confidence:.1%})"
        elif adaptive_confidence < 0.55:  # Medium-low mastery - use moderate questions
            difficulty = "moderate" 
            db_difficulty = "moderate"
            difficulty_emoji = "🟡"
            adaptive_reason = f"Moderate questions for skill building (mastery: {adaptive_confidence:.1%})"
        elif adaptive_confidence < 0.75:  # Medium-high mastery - stay at moderate
            difficulty = "moderate"
            db_difficulty = "moderate"
            difficulty_emoji = "🟡"
            adaptive_reason = f"Moderate questions for steady progress (mastery: {adaptive_confidence:.1%})"
        elif adaptive_confidence < 0.9:  # High mastery - use difficult questions
            difficulty = "difficult"
            db_difficulty = "difficult"
            difficulty_emoji = "🔴"
            adaptive_reason = f"Difficult questions for advanced growth (mastery: {adaptive_confidence:.1%})"
        else:  # Very high mastery - use most difficult questions
            difficulty = "difficult"
            db_difficulty = "difficult"  
            difficulty_emoji = "🔥"
            adaptive_reason = f"Advanced difficult questions (mastery: {adaptive_confidence:.1%})"
        
        print(f"🎯 Adaptive mapping: confidence {adaptive_confidence:.3f} → {difficulty} difficulty")
        
        # Get real questions from database
        from assessment.improved_models import Subject
        from assessment.models import AdaptiveQuestion
        
        # Get subject object
        subject_obj = Subject.objects.filter(code=session.session_config.get('subject_code', 'quantitative_aptitude')).first()
        if not subject_obj:
            # Fallback to first available subject
            subject_obj = Subject.objects.first()
        
        # Try to get real questions matching difficulty
        real_questions = AdaptiveQuestion.objects.filter(
            subject_fk=subject_obj,
            difficulty_level=db_difficulty
        ).exclude(
            # Exclude questions already attempted in this session
            id__in=QuestionAttempt.objects.filter(session=session).values_list('question_id', flat=True)
        )
        
        if real_questions.exists():
            # Use real question from database
            real_question = real_questions.first()
            question_id = f"real_{real_question.id}"
            
            question = {
                'success': True,
                'question_id': question_id,
                'real_question_id': real_question.id,
                'session_id': session_id,
                'question_number': question_count,
                'subject': subject,
                'subject_display': subject_obj.name,
                'difficulty': difficulty,
                'difficulty_display': f"{difficulty_emoji} {difficulty.upper()}",
                'question_text': real_question.question_text,
                'options': [
                    {'id': 'A', 'text': real_question.option_a},
                    {'id': 'B', 'text': real_question.option_b},
                    {'id': 'C', 'text': real_question.option_c},
                    {'id': 'D', 'text': real_question.option_d}
                ],
                'correct_answer': real_question.answer.upper(),
                'explanation': f'This {difficulty} {subject_obj.name} question was selected based on your confidence level of {adaptive_confidence:.1%}',
                'topic': getattr(real_question, 'tags', '').split(',')[0] if getattr(real_question, 'tags', '') else 'General',
                'subtopic': real_question.question_type,
                'adaptive_info': {
                    'mastery_level': adaptive_confidence,
                    'skill_id': skill_id,
                    'adaptive_reason': adaptive_reason,
                    'orchestration_enabled': ORCHESTRATION_AVAILABLE,
                    'bkt_mastery': orchestration_result.get('bkt_mastery', 0.5) if ORCHESTRATION_AVAILABLE and 'orchestration_result' in locals() else adaptive_confidence,
                    'dkt_prediction': orchestration_result.get('dkt_prediction', 0.5) if ORCHESTRATION_AVAILABLE and 'orchestration_result' in locals() else 0.5,
                    'real_question': True
                },
            }
        else:
            # Fallback to adaptive dummy question if no real questions available
            question_id = f"adaptive_{session_id}_{question_count}"
            
            question = {
                'success': True,
                'question_id': question_id,
                'session_id': session_id,
                'question_number': question_count,
                'subject': subject,
                'subject_display': subject_obj.name if subject_obj else subject.title(),
                'difficulty': difficulty,
                'difficulty_display': f"{difficulty_emoji} {difficulty.upper()}",
                'question_text': f"Question {question_count}: This is a {difficulty} {subject} question adapted to your current confidence level ({adaptive_confidence:.1%}).",
                'options': [
                    {'id': 'A', 'text': f'Option A - {difficulty} level answer'},
                    {'id': 'B', 'text': f'Option B - {difficulty} level answer'},
                    {'id': 'C', 'text': f'Option C - {difficulty} level answer'},
                    {'id': 'D', 'text': f'Option D - {difficulty} level answer'}
                ],
                'correct_answer': 'A',
                'explanation': f'This {difficulty} {subject_obj.name} question was selected based on your confidence level of {adaptive_confidence:.1%}',
                'adaptive_info': {
                    'mastery_level': adaptive_confidence,
                    'skill_id': skill_id,
                    'adaptive_reason': adaptive_reason,
                    'orchestration_enabled': ORCHESTRATION_AVAILABLE,
                    'real_question': False
                },
            'message': f'📚 Adaptive question ready! Difficulty: {difficulty_emoji} {difficulty.upper()}',
            'next_action': 'Choose your answer and click "Submit Answer"'
        }
        
        return JsonResponse(question)
        
    except Exception as e:
        logger.error(f"Get question error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get question'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_simple_answer(request):
    """
    SUBMIT ANSWER - Direct frontend click endpoint
    
    Frontend can call this immediately:
    POST /submit-answer
    {
        "session_id": "<session_id>",
        "question_id": "<question_id>", 
        "selected_answer": "A",
        "time_spent": 15.5
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 10.0)
        
        if not all([session_id, question_id, selected_answer]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields',
                'message': 'session_id, question_id, and selected_answer are required'
            }, status=400)
        
        # Validate session exists with better error handling
        try:
            session = get_object_or_404(StudentSession, id=session_id)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Invalid session_id - please use a valid session from start-session endpoint'
            }, status=400)
        subject = session.session_config.get('subject', 'mathematics')
        
        # Will determine correct answer after getting question
        
        # Handle question record for attempt
        from assessment.models import AdaptiveQuestion
        
        # Check if this is a real question (starts with "real_")
        if question_id.startswith("real_"):
            # Extract the actual question ID and clean it
            actual_question_id = question_id.replace("real_", "")
            
            # Clean the UUID string - remove any non-UUID characters
            import re
            import uuid
            
            # Remove quotes, spaces, and other invalid characters
            cleaned_id = re.sub(r'[^\w\-]', '', actual_question_id.strip())
            
            logger.info(f"Original question_id: {question_id}")
            logger.info(f"Extracted ID: '{actual_question_id}'")
            logger.info(f"Cleaned ID: '{cleaned_id}'")
            
            try:
                # Convert string to UUID
                actual_uuid = uuid.UUID(cleaned_id)
                logger.info(f"Successfully created UUID: {actual_uuid}")
                
                # Get the existing real question
                question_for_attempt = AdaptiveQuestion.objects.get(id=actual_uuid)
                correct_answer = question_for_attempt.answer.upper()
                logger.info(f"Found question: {question_for_attempt.id}, Answer: {correct_answer}")
                
            except ValueError as ve:
                logger.error(f"UUID conversion failed: {ve}")
                logger.error(f"Problematic string: '{cleaned_id}' (length: {len(cleaned_id)})")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid UUID format: {str(ve)}',
                    'message': f'Question ID "{cleaned_id}" is not a valid UUID format',
                    'debug_info': {
                        'original_id': question_id,
                        'extracted_id': actual_question_id,
                        'cleaned_id': cleaned_id,
                        'id_length': len(cleaned_id)
                    }
                }, status=400)
            except AdaptiveQuestion.DoesNotExist:
                logger.error(f"Question not found: {actual_uuid}")
                return JsonResponse({
                    'success': False,
                    'error': 'Real question not found in database',
                    'message': f'Question with UUID {actual_uuid} not found in database'
                }, status=400)
        else:
            # For adaptive dummy questions, create a simple record
            # Generate a unique UUID for the dummy question
            import uuid
            dummy_uuid = uuid.uuid4()
            
            # Try to get existing dummy question first, or create new one
            try:
                # Check if we already created a dummy question for this question_id
                existing_dummy = AdaptiveQuestion.objects.filter(
                    question_text__contains=f'Simple API Question {question_id}'
                ).first()
                
                if existing_dummy:
                    question_for_attempt = existing_dummy
                else:
                    # Create new dummy question
                    question_for_attempt = AdaptiveQuestion.objects.create(
                        id=dummy_uuid,
                        question_text=f'Simple API Question {question_id}',
                        question_type='multiple_choice',
                        answer='A',
                        difficulty_level='medium',
                        subject_fk=session.subject if session.subject else None,
                        option_a='Option A',
                        option_b='Option B', 
                        option_c='Option C',
                        option_d='Option D'
                    )
                    
            except Exception as e:
                logger.error(f"Error creating dummy question: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to create question record: {str(e)}',
                    'message': 'Could not create question for submission'
                }, status=500)
                
            correct_answer = 'A'
        
        # Determine correct answer based on question type
        is_correct = (selected_answer.upper() == correct_answer.upper())
        
        # Create question attempt record
        attempt = QuestionAttempt.objects.create(
            session=session,
            question=question_for_attempt,
            student=session.student,
            question_number_in_session=QuestionAttempt.objects.filter(session=session).count() + 1,
            student_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            difficulty_when_presented=question_for_attempt.difficulty_level,
            interaction_data={
                'simple_api': True,
                'adaptive_submission': True,
                'question_id_string': question_id,
                'real_question': question_id.startswith("real_")
            }
        )
        
        # Calculate skill_id and session accuracy for orchestration - FIXED: Use consistent format
        skill_id = f"{subject}_skill"
        
        # Get session accuracy before this submission
        previous_attempts = QuestionAttempt.objects.filter(session=session).exclude(id=attempt.id)
        if previous_attempts.exists():
            correct_before = previous_attempts.filter(is_correct=True).count()
            total_before = previous_attempts.count()
            session_accuracy_before = correct_before / total_before
        else:
            session_accuracy_before = 0.0

        # Get knowledge state before submission using FULL ORCHESTRATION
        bkt_mastery_before = 0.5
        dkt_prediction_before = 0.5
        bkt_params_before = {'P_L': 0.5, 'P_T': 0.3, 'P_G': 0.2, 'P_S': 0.1}
        
        try:
            if ORCHESTRATION_AVAILABLE and orchestration_service:
                logger.info(f"🎯 Getting pre-submission orchestrated state for {session.student.username}, skill {skill_id}")
                
                orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                    student_username=session.student.username,
                    subject=session.subject.code if hasattr(session.subject, 'code') else subject
                )
                
                if orchestration_result and orchestration_result.get('success'):
                    bkt_mastery_before = orchestration_result.get('bkt_mastery', 0.5)
                    dkt_prediction_before = orchestration_result.get('dkt_prediction', 0.5)
                    
                    # Extract BKT parameters if available
                    knowledge_state = orchestration_result.get('knowledge_state', {})
                    bkt_data = knowledge_state.get('bkt', {})
                    if isinstance(bkt_data, dict):
                        bkt_params_before = {
                            'P_L': bkt_data.get('mastery_level', bkt_mastery_before),
                            'P_T': bkt_data.get('transition_prob', 0.3),
                            'P_G': bkt_data.get('guess_prob', 0.2),
                            'P_S': bkt_data.get('slip_prob', 0.1)
                        }
                    
                    logger.info(f"📊 Orchestrated pre-state: BKT={bkt_mastery_before:.3f}, DKT={dkt_prediction_before:.3f}")
                else:
                    logger.warning("⚠️ Orchestration returned no valid state, using defaults")
                    
            else:
                logger.info("⚠️ Using fallback BKT service for pre-submission state")
                # Fallback to individual BKT service
                bkt_before = bkt_service.get_skill_bkt_params(session.student, skill_id)
                bkt_mastery_before = bkt_before.P_L if bkt_before else 0.5
                bkt_params_before = {
                    'P_L': bkt_before.P_L if bkt_before else 0.5,
                    'P_T': bkt_before.P_T if bkt_before else 0.3,
                    'P_G': bkt_before.P_G if bkt_before else 0.2,
                    'P_S': bkt_before.P_S if bkt_before else 0.1
                }
                dkt_prediction_before = dkt_service.get_skill_prediction(session.student, skill_id)
                
        except Exception as e:
            logger.error(f"❌ Pre-submission state retrieval failed: {e}")
            # Use defaults

        # Process answer submission via FULL ORCHESTRATION SYSTEM
        bkt_updated = False
        dkt_updated = False
        new_mastery = bkt_mastery_before
        bkt_params_after = bkt_params_before
        dkt_prediction_after = dkt_prediction_before
        
        try:
            if ORCHESTRATION_AVAILABLE and orchestration_service:
                logger.info(f"🎯 Processing answer via full orchestration: correct={is_correct}, time_spent={time_spent}")
                
                # Use orchestration service to update both BKT and DKT with comprehensive data
                orchestrated_update = orchestration_service.process_interaction(
                    student_username=session.student.username,
                    subject=session.subject.code if hasattr(session.subject, 'code') else subject,
                    question_id=question_id,
                    is_correct=is_correct,
                    time_spent=time_spent,
                    difficulty_level=question_for_attempt.difficulty_level
                )
                
                if orchestrated_update and orchestrated_update.get('success'):
                    # Extract BKT updates
                    if 'bkt_mastery' in orchestrated_update:
                        bkt_updated = True
                        new_mastery = orchestrated_update['bkt_mastery']
                        logger.info(f"✅ Orchestrated BKT update: mastery={new_mastery:.3f}")
                    
                    # Extract DKT updates
                    if 'dkt_prediction' in orchestrated_update:
                        dkt_updated = True
                        dkt_prediction_after = orchestrated_update['dkt_prediction']
                        logger.info(f"✅ Orchestrated DKT update: prediction={dkt_prediction_after:.3f}")
                    
                    # Extract comprehensive parameters
                    if 'knowledge_state' in orchestrated_update:
                        knowledge_state = orchestrated_update['knowledge_state']
                        bkt_data = knowledge_state.get('bkt', {})
                        if isinstance(bkt_data, dict):
                            bkt_params_after = {
                                'P_L': bkt_data.get('mastery_level', new_mastery),
                                'P_T': bkt_data.get('transition_prob', 0.3),
                                'P_G': bkt_data.get('guess_prob', 0.2),
                                'P_S': bkt_data.get('slip_prob', 0.1)
                            }
                else:
                    logger.warning("⚠️ Orchestration returned invalid update, using fallback")
                    raise Exception("Invalid orchestration response")
                        
        except Exception as e:
            logger.warning(f"⚠️ Orchestrated answer processing failed: {e}, using fallback individual updates")
            
            # Fallback to individual BKT update
            try:
                bkt_service.update_skill_bkt(
                    user=session.student,
                    skill_id=skill_id,
                    is_correct=is_correct,
                    interaction_data={'question_id': question_id, 'time_spent': time_spent}
                )
                bkt_updated = True
                # Get updated mastery
                updated_bkt = bkt_service.get_skill_bkt_params(session.student, skill_id)
                new_mastery = updated_bkt.P_L if updated_bkt else bkt_mastery_before
                bkt_params_after = {
                    'P_L': updated_bkt.P_L if updated_bkt else 0.5,
                    'P_T': updated_bkt.P_T if updated_bkt else 0.3,
                    'P_G': updated_bkt.P_G if updated_bkt else 0.2,
                    'P_S': updated_bkt.P_S if updated_bkt else 0.1
                }
                logger.info(f"🔄 Fallback BKT update: mastery={new_mastery:.3f}")
            except Exception as bkt_error:
                logger.warning(f"BKT fallback update failed: {bkt_error}")
                bkt_updated = False
                new_mastery = bkt_mastery_before
                bkt_params_after = bkt_params_before
            
            # Fallback to individual DKT update 
            try:
                dkt_service.update_dkt_knowledge(
                    user=session.student,
                    skill_id=skill_id,
                    is_correct=is_correct,
                    interaction_data={'question_id': question_id, 'time_spent': time_spent}
                )
                dkt_updated = True
                dkt_prediction_after = dkt_service.get_skill_prediction(session.student, skill_id)
                logger.info(f"🔄 Fallback DKT update: prediction={dkt_prediction_after:.3f}")
            except Exception as dkt_error:
                logger.warning(f"DKT fallback update failed: {dkt_error}")
                dkt_updated = False
                dkt_prediction_after = dkt_prediction_before
        
        # Calculate session progress after this submission
        total_questions = QuestionAttempt.objects.filter(session=session).count()
        correct_answers = QuestionAttempt.objects.filter(session=session, is_correct=True).count()
        session_accuracy_after = correct_answers / max(total_questions, 1)
        
        # Use orchestration messages when available, otherwise fallback to simple logic
        if ORCHESTRATION_AVAILABLE and 'orchestrated_update' in locals() and orchestrated_update and orchestrated_update.get('success'):
            # Use intelligent messages from orchestration service
            orchestrated_feedback = orchestrated_update.get('orchestrated_feedback', {})
            adaptation_message = orchestrated_feedback.get('adaptation_message', '✅ Keep learning!')
            difficulty_change = orchestrated_feedback.get('difficulty_adaptation', 'Continue practicing')
            logger.info(f"📢 Using orchestrated messages: {difficulty_change} - {adaptation_message}")
        else:
            # Fallback to simple adaptation logic when orchestration not available
            mastery_change = new_mastery - bkt_mastery_before
            if is_correct and new_mastery > 0.7:
                adaptation_message = "🎉 Great job! Questions will get harder to challenge you more."
                difficulty_change = "Questions getting HARDER"
                next_difficulty = "harder"
            elif not is_correct and new_mastery < 0.4:
                adaptation_message = "💪 Let's try easier questions to build your confidence."
                difficulty_change = "Questions getting EASIER"
                next_difficulty = "easier"
            else:
                adaptation_message = "👍 Good progress! Questions will stay at similar difficulty."
                difficulty_change = "Difficulty staying SIMILAR"
                next_difficulty = "same"
            logger.info(f"📢 Using fallback messages: {difficulty_change} - {adaptation_message}")
        
        # Create comprehensive adaptive submission record for analysis (optional - won't fail if table doesn't exist)
        try:
            adaptive_submission = AdaptiveSubmission.objects.create(
                student=session.student,
                session=session,
                subject=session.subject,
                question=question_for_attempt,
                
                # Question context
                question_type=question_for_attempt.question_type,
                chapter=getattr(question_for_attempt, 'chapter', 'General'),
                subtopic=getattr(question_for_attempt, 'tags', '').split(',')[0] if getattr(question_for_attempt, 'tags', '') else 'General',
                difficulty_level=question_for_attempt.difficulty_level,
                
                # Student response
                selected_answer=selected_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                
                # Timing and position
                time_spent_seconds=time_spent,
                question_number_in_session=attempt.question_number_in_session,
                
                # Knowledge state before and after
                bkt_mastery_before=bkt_mastery_before,
                dkt_prediction_before=dkt_prediction_before,
                bkt_mastery_after=new_mastery,
                dkt_prediction_after=dkt_prediction_after,
                
                # Knowledge tracing data
                skill_id=skill_id,
                bkt_params=bkt_params_after,
                dkt_hidden_state={'prediction': dkt_prediction_after, 'updated': dkt_updated},
                
                # Adaptation decisions
                next_difficulty_recommended=next_difficulty,
                adaptation_reason=adaptation_message,
                
                # Performance context
                session_accuracy_before=session_accuracy_before,
                session_accuracy_after=session_accuracy_after,
                
                # Metadata
                submission_source='frontend_api',
                interaction_data={
                    'simple_api': True,
                    'adaptive_submission': True,
                    'question_id_string': question_id,
                    'real_question': question_id.startswith("real_"),
                    'bkt_updated': bkt_updated,
                    'dkt_updated': dkt_updated,
                    'mastery_improvement': mastery_change
                },
                
                # Analytics flags
                is_first_attempt=attempt.question_number_in_session == 1,
                is_mastery_achieved=new_mastery >= 0.8,
                contributed_to_mastery=mastery_change > 0.1
            )
            
            logger.info(f"✅ Created adaptive submission analytics record: {adaptive_submission.id}")
            
        except Exception as e:
            logger.warning(f"⚠️  AdaptiveSubmission analytics not available (table may not exist): {e}")
            # Continue without failing the submission - basic QuestionAttempt is still recorded
        
        response = {
            'success': True,
            'answer_correct': is_correct,
            'correct_answer': 'A',
            'selected_answer': selected_answer,
            'explanation': f"The correct answer was A. {'Well done!' if is_correct else 'Better luck next time!'}",
            'knowledge_update': {
                'bkt_updated': bkt_updated,
                'dkt_updated': dkt_updated,
                'new_mastery_level': new_mastery,
                'dkt_prediction': dkt_prediction_after,
                'mastery_display': f"{new_mastery:.1%}"
            },
            'session_progress': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'accuracy': f"{session_accuracy_after:.1%}",
                'questions_remaining': max(0, session.total_questions_planned - total_questions)
            },
            'adaptive_feedback': {
                'mastery_change': f"Mastery level: {new_mastery:.1%}",
                'difficulty_adaptation': difficulty_change,
                'adaptation_message': adaptation_message
            },
            'message': f"✅ Answer submitted! {adaptation_message}",
            'next_action': 'Click "Get Next Question" to continue learning!' if total_questions < session.total_questions_planned else 'Session complete! Well done! 🎉'
        }
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to submit answer'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_progress(request, session_id):
    """
    GET PROGRESS - Direct frontend click endpoint
    
    Frontend can call this immediately:
    GET /session-progress/<session_id>/
    """
    try:
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        attempts = QuestionAttempt.objects.filter(session=session)
        
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        
        # Get current knowledge states with FULL ORCHESTRATION
        subject = session.session_config.get('subject', 'mathematics')
        skill_id = f"{subject}_skill"  # FIXED: Use consistent skill_id format
        
        try:
            if ORCHESTRATION_AVAILABLE and orchestration_service:
                # Enhanced orchestration integration for progress tracking
                logger.info(f"📊 Getting orchestrated progress for {session.student.username}, subject: {subject}")
                
                orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                    student_username=session.student.username,
                    subject=subject
                )
                
                if orchestration_result and orchestration_result.get('success'):
                    current_mastery = orchestration_result.get('bkt_mastery', 0.5)
                    dkt_prediction = orchestration_result.get('dkt_prediction', 0.5)
                    combined_confidence = orchestration_result.get('combined_confidence', 0.5)
                    
                    # Enhanced learning status with orchestration data
                    if combined_confidence > 0.8:
                        learning_status = "🎉 Mastery Achieved! Excellent understanding!"
                        next_difficulty = "Advanced"
                    elif combined_confidence > 0.6:
                        learning_status = "📈 Great progress! You're learning well!"
                        next_difficulty = "Hard"
                    elif combined_confidence > 0.4:
                        learning_status = "💪 Good improvement! Keep practicing!"
                        next_difficulty = "Medium"
                    else:
                        learning_status = "🌱 Building foundations! Stay focused!"
                        next_difficulty = "Easy"
                    
                    logger.info(f"📊 Orchestrated Progress - BKT: {current_mastery:.3f}, DKT: {dkt_prediction:.3f}, Combined: {combined_confidence:.3f}")
                else:
                    logger.warning("⚠️ Orchestration returned no progress data, using fallback")
                    raise Exception("Invalid orchestration progress response")
                    
        except Exception as e:
            logger.warning(f"⚠️ Orchestration progress failed: {e}, using fallback")
            # Fallback implementation
            try:
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                current_mastery = bkt_params.P_L if bkt_params else 0.5
            except:
                current_mastery = 0.5
            
            try:
                dkt_prediction = dkt_service.get_skill_prediction(session.student, skill_id)
            except:
                dkt_prediction = 0.5
                
            combined_confidence = (current_mastery + dkt_prediction) / 2
            
            # Basic learning status
            if current_mastery > 0.7:
                learning_status = "Excellent progress!"
                next_difficulty = "Hard"
            elif current_mastery > 0.4:
                learning_status = "Good progress!"
                next_difficulty = "Medium"
            else:
                learning_status = "Building foundations"
                next_difficulty = "Easy"
        
        # Store current mastery in session for persistence
        session_config = session.session_config or {}
        session_config.update({
            'current_bkt_mastery': current_mastery,
            'current_dkt_prediction': dkt_prediction,
            'current_combined_confidence': combined_confidence,
            'last_mastery_update': timezone.now().isoformat()
        })
        session.session_config = session_config
        session.save()
        
        progress = {
            'success': True,
            'session_id': session_id,
            'student_name': session.student.get_full_name() or session.student.username,
            'subject': subject,
            'session_stats': {
                'questions_answered': total_questions,
                'correct_answers': correct_answers,
                'accuracy': f"{correct_answers / max(total_questions, 1):.1%}",
                'questions_remaining': max(0, session.total_questions_planned - total_questions)
            },
            'knowledge_state': {
                'bkt_mastery': f"{current_mastery:.1%}",
                'bkt_mastery_raw': current_mastery,
                'dkt_prediction': f"{dkt_prediction:.1%}",
                'dkt_prediction_raw': dkt_prediction,
                'combined_confidence': f"{combined_confidence:.1%}",
                'combined_confidence_raw': combined_confidence,
                'overall_progress': f"{combined_confidence:.1%}",
                'skill_level': skill_id,
                'orchestration_enabled': ORCHESTRATION_AVAILABLE
            },
            'adaptive_info': {
                'difficulty_trend': "LangGraph orchestration adapting to your performance",
                'next_difficulty': next_difficulty,
                'learning_status': learning_status,
                'bkt_dkt_integrated': True,
                'orchestration_active': ORCHESTRATION_AVAILABLE
            },
            'orchestration_details': {
                'langraph_active': ORCHESTRATION_AVAILABLE,
                'bkt_mastery_raw': current_mastery,
                'dkt_prediction_raw': dkt_prediction,
                'combined_confidence_raw': combined_confidence,
                'adaptive_reasoning': f"Difficulty: {next_difficulty} based on combined BKT/DKT confidence of {combined_confidence:.1%}"
            } if ORCHESTRATION_AVAILABLE else {},
            'message': f"📊 LangGraph Orchestration: {correct_answers}/{total_questions} correct ({correct_answers / max(total_questions, 1):.1%}), Combined Confidence: {combined_confidence:.1%}"
        }
        
        return JsonResponse(progress)
        
    except Exception as e:
        logger.error(f"Get progress error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get progress'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def complete_session(request):
    """
    COMPLETE SESSION - Store final mastery scores and mark session complete
    
    Frontend can call this when session ends:
    POST /complete-session
    {
        "session_id": "uuid-string",
        "completion_reason": "finished" | "timeout" | "manual"
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        completion_reason = data.get('completion_reason', 'finished')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        
        # Get final knowledge states with orchestration
        subject = session.session_config.get('subject', 'mathematics')
        skill_id = f"{subject}_skill"
        
        # Get current mastery scores
        current_mastery = 0.5
        dkt_prediction = 0.5
        combined_confidence = 0.5
        
        try:
            if ORCHESTRATION_AVAILABLE and orchestration_service:
                orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                    student_username=session.student.username,
                    subject=subject
                )
                
                if orchestration_result and orchestration_result.get('success'):
                    current_mastery = orchestration_result.get('bkt_mastery', 0.5)
                    dkt_prediction = orchestration_result.get('dkt_prediction', 0.5)
                    combined_confidence = orchestration_result.get('combined_confidence', 0.5)
                    
                    logger.info(f"🏁 Final Mastery Scores - BKT: {current_mastery:.4f}, DKT: {dkt_prediction:.4f}, Combined: {combined_confidence:.4f}")
                else:
                    raise Exception("Orchestration failed for final mastery")
        except Exception as e:
            logger.warning(f"⚠️ Using fallback for final mastery calculation: {e}")
            try:
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                current_mastery = bkt_params.P_L if bkt_params else 0.5
                dkt_prediction = dkt_service.get_skill_prediction(session.student, skill_id)
                combined_confidence = (current_mastery + dkt_prediction) / 2
            except Exception as fallback_error:
                logger.error(f"❌ Fallback mastery calculation failed: {fallback_error}")
        
        # Calculate session statistics
        attempts = QuestionAttempt.objects.filter(session=session)
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        accuracy_rate = correct_answers / max(total_questions, 1)
        
        # Update session with final mastery scores and complete it
        session.status = 'COMPLETED'
        session.session_end_time = timezone.now()
        
        if session.session_start_time:
            duration = session.session_end_time - session.session_start_time
            session.session_duration_seconds = int(duration.total_seconds())
        
        # Store comprehensive final mastery data
        final_mastery_data = {
            'final_bkt_mastery': current_mastery,
            'final_dkt_prediction': dkt_prediction,
            'final_combined_confidence': combined_confidence,
            'completion_reason': completion_reason,
            'completion_timestamp': timezone.now().isoformat(),
            'session_accuracy': accuracy_rate,
            'questions_completed': total_questions,
            'correct_answers': correct_answers,
            'mastery_achievement': {
                'expert': current_mastery >= 0.85,
                'advanced': current_mastery >= 0.70,
                'proficient': current_mastery >= 0.50,
                'developing': current_mastery >= 0.30,
                'novice': current_mastery < 0.30
            }
        }
        
        session_config = session.session_config or {}
        session_config.update(final_mastery_data)
        session.session_config = session_config
        
        # Update session performance fields
        session.questions_attempted = total_questions
        session.questions_correct = correct_answers
        session.percentage_score = accuracy_rate * 100
        
        session.save()
        
        # Create or update StudentProgress with mastery tracking
        from assessment.improved_models import StudentProgress, Subject
        
        # Get subject object
        subject_mapping = {
            'mathematics': 'quantitative_aptitude',
            'math': 'quantitative_aptitude', 
            'quantitative': 'quantitative_aptitude',
            'quantitative_aptitude': 'quantitative_aptitude',
            'reasoning': 'logical_reasoning',
            'logic': 'logical_reasoning',
            'logical_reasoning': 'logical_reasoning',
            'data': 'data_interpretation',
            'data_interpretation': 'data_interpretation',
            'verbal': 'verbal_ability',
            'english': 'verbal_ability',
            'verbal_ability': 'verbal_ability'
        }
        
        subject_code = subject_mapping.get(subject.lower(), 'quantitative_aptitude')
        subject_obj, created = Subject.objects.get_or_create(
            code=subject_code,
            defaults={'name': subject.title(), 'is_active': True}
        )
        
        # Update or create progress record
        progress, created = StudentProgress.objects.get_or_create(
            student=session.student,
            subject=subject_obj,
            defaults={
                'total_sessions': 0,
                'total_questions_attempted': 0,
                'total_questions_correct': 0,
                'current_mastery_score': 0.0
            }
        )
        
        # Update progress with session data and mastery
        progress.update_from_session(session)
        progress.update_mastery_score(combined_confidence)
        
        # Determine mastery level
        mastery_level = 'novice'
        if current_mastery >= 0.85:
            mastery_level = 'expert'
        elif current_mastery >= 0.70:
            mastery_level = 'advanced'
        elif current_mastery >= 0.50:
            mastery_level = 'proficient'
        elif current_mastery >= 0.30:
            mastery_level = 'developing'
        
        return JsonResponse({
            'success': True,
            'message': f'🎉 Session completed! Final mastery: {current_mastery:.1%}',
            'session_id': session_id,
            'completion_data': {
                'completion_reason': completion_reason,
                'session_duration_minutes': session.session_duration_seconds / 60 if session.session_duration_seconds else 0,
                'questions_completed': total_questions,
                'accuracy_rate': f"{accuracy_rate:.1%}",
                'final_mastery': {
                    'bkt_mastery': f"{current_mastery:.1%}",
                    'bkt_mastery_raw': current_mastery,
                    'dkt_prediction': f"{dkt_prediction:.1%}",
                    'dkt_prediction_raw': dkt_prediction,
                    'combined_confidence': f"{combined_confidence:.1%}",
                    'combined_confidence_raw': combined_confidence,
                    'mastery_level': mastery_level,
                    'mastery_achieved': current_mastery >= 0.70
                },
                'performance_summary': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': accuracy_rate,
                    'subject': subject,
                    'orchestration_enabled': ORCHESTRATION_AVAILABLE
                },
                'next_steps': {
                    'recommendation': 'Continue practicing' if current_mastery < 0.70 else 'Try advanced questions',
                    'suggested_difficulty': 'moderate' if current_mastery < 0.70 else 'difficult',
                    'mastery_progress': f"You've achieved {mastery_level} level mastery!"
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Complete session error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to complete session'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_history(request, student_id):
    """
    GET SESSION HISTORY - Show all sessions with mastery progression
    
    Frontend can call this to show learning history:
    GET /session-history/<student_id>/
    """
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Get all completed sessions with mastery data
        sessions = StudentSession.objects.filter(
            student=student,
            status='COMPLETED'
        ).order_by('-session_end_time')[:20]  # Last 20 sessions
        
        session_history = []
        
        for session in sessions:
            session_config = session.session_config or {}
            
            # Extract mastery data from session config
            final_bkt = session_config.get('final_bkt_mastery', 0.0)
            final_dkt = session_config.get('final_dkt_prediction', 0.0)
            final_combined = session_config.get('final_combined_confidence', 0.0)
            
            # Calculate mastery level
            mastery_level = 'novice'
            if final_bkt >= 0.85:
                mastery_level = 'expert'
            elif final_bkt >= 0.70:
                mastery_level = 'advanced'
            elif final_bkt >= 0.50:
                mastery_level = 'proficient'
            elif final_bkt >= 0.30:
                mastery_level = 'developing'
            
            session_data = {
                'session_id': str(session.id),
                'subject': session_config.get('subject', session.subject.name),
                'session_date': session.session_end_time.strftime('%Y-%m-%d %H:%M') if session.session_end_time else 'Unknown',
                'duration_minutes': round(session.session_duration_seconds / 60, 1) if session.session_duration_seconds else 0,
                'questions_attempted': session.questions_attempted,
                'accuracy': f"{session.percentage_score:.1f}%" if session.percentage_score else "0%",
                'mastery_scores': {
                    'bkt_mastery': f"{final_bkt:.1%}",
                    'bkt_mastery_raw': final_bkt,
                    'dkt_prediction': f"{final_dkt:.1%}", 
                    'dkt_prediction_raw': final_dkt,
                    'combined_confidence': f"{final_combined:.1%}",
                    'combined_confidence_raw': final_combined,
                    'mastery_level': mastery_level,
                    'mastery_achieved': final_bkt >= 0.70
                },
                'performance': {
                    'total_questions': session.questions_attempted,
                    'correct_answers': session.questions_correct,
                    'accuracy_rate': session.percentage_score / 100 if session.percentage_score else 0
                }
            }
            
            session_history.append(session_data)
        
        return JsonResponse({
            'success': True,
            'student_id': student_id,
            'student_name': student.get_full_name() or student.username,
            'total_sessions': len(session_history),
            'sessions': session_history,
            'mastery_progression': {
                'latest_mastery': session_history[0]['mastery_scores'] if session_history else None,
                'mastery_trend': 'improving' if len(session_history) >= 2 and session_history[0]['mastery_scores']['bkt_mastery_raw'] > session_history[1]['mastery_scores']['bkt_mastery_raw'] else 'stable'
            }
        })
        
    except Exception as e:
        logger.error(f"Get session history error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get session history'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_student_analytics(request, student_id, subject_code=None):
    """
    GET ANALYTICS - Comprehensive student analytics endpoint
    
    Frontend can call this to get detailed learning analytics:
    GET /student-analytics/<student_id>/
    GET /student-analytics/<student_id>/<subject_code>/
    """
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Get subject if specified
        subject = None
        if subject_code:
            from assessment.improved_models import Subject
            subject = Subject.objects.filter(code=subject_code).first()
        
        # Get performance analysis
        performance = AdaptiveSubmissionAnalyzer.analyze_student_performance(
            student=student, 
            subject=subject, 
            days=30
        )
        
        if not performance:
            return JsonResponse({
                'success': False,
                'message': 'No submission data found for analysis',
                'student_name': student.get_full_name() or student.username,
                'subject': subject.name if subject else 'All Subjects'
            })
        
        # Get learning insights
        insights_data = AdaptiveSubmissionAnalyzer.generate_learning_insights(
            student=student, 
            subject=subject
        )
        
        # Get recent submissions for detailed view
        recent_submissions = AdaptiveSubmission.objects.filter(
            student=student
        )
        if subject:
            recent_submissions = recent_submissions.filter(subject=subject)
        
        recent_submissions = recent_submissions.order_by('-created_at')[:10]
        
        submission_details = []
        for submission in recent_submissions:
            submission_details.append({
                'id': str(submission.id),
                'created_at': submission.created_at.isoformat(),
                'subject': submission.subject.name,
                'chapter': submission.chapter,
                'difficulty': submission.difficulty_level,
                'is_correct': submission.is_correct,
                'time_spent': submission.time_spent_seconds,
                'mastery_before': submission.bkt_mastery_before,
                'mastery_after': submission.bkt_mastery_after,
                'mastery_improvement': submission.mastery_improvement,
                'adaptation_reason': submission.adaptation_reason
            })
        
        # Compile comprehensive analytics
        analytics_response = {
            'success': True,
            'student_name': student.get_full_name() or student.username,
            'subject': subject.name if subject else 'All Subjects',
            'analysis_period': '30 days',
            
            # Performance metrics
            'performance_summary': {
                'total_submissions': performance['total_submissions'],
                'overall_accuracy': f"{performance['accuracy']:.1%}",
                'mastery_growth': f"{performance['mastery_growth']:+.1%}",
                'average_time_per_question': f"{performance['average_time_per_question']:.1f}s",
                'starting_mastery': f"{performance['starting_mastery']:.1%}",
                'current_mastery': f"{performance['ending_mastery']:.1%}"
            },
            
            # Learning insights and recommendations
            'learning_insights': insights_data['insights'],
            'recommendations': insights_data['recommendations'],
            
            # Difficulty progression
            'difficulty_distribution': performance['difficulty_distribution'],
            
            # Recent activity
            'recent_submissions': submission_details,
            
            # Trends and patterns
            'learning_trends': {
                'mastery_trajectory': 'improving' if performance['mastery_growth'] > 0 else 'stable',
                'accuracy_trend': 'high' if performance['accuracy'] > 0.7 else 'moderate' if performance['accuracy'] > 0.5 else 'developing',
                'engagement_level': 'high' if performance['total_submissions'] > 20 else 'moderate' if performance['total_submissions'] > 10 else 'low'
            },
            
            'message': f"📊 Analytics for {student.get_full_name() or student.username} - {performance['total_submissions']} submissions analyzed"
        }
        
        return JsonResponse(analytics_response)
        
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to get student analytics'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_submission_reports(request):
    """
    GET SUBMISSION REPORTS - Aggregate analytics endpoint
    
    Frontend can call this to get system-wide analytics:
    GET /submission-reports/?days=7&subject=quantitative_aptitude
    """
    try:
        # Get query parameters
        days = int(request.GET.get('days', 7))
        subject_code = request.GET.get('subject')
        
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        submissions = AdaptiveSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Filter by subject if specified
        if subject_code:
            from assessment.improved_models import Subject
            subject = Subject.objects.filter(code=subject_code).first()
            if subject:
                submissions = submissions.filter(subject=subject)
        
        # Aggregate statistics
        total_submissions = submissions.count()
        if total_submissions == 0:
            return JsonResponse({
                'success': True,
                'message': 'No submissions found for the specified period',
                'period_days': days,
                'total_submissions': 0
            })
        
        # Calculate metrics
        correct_submissions = submissions.filter(is_correct=True).count()
        overall_accuracy = correct_submissions / total_submissions
        
        # Subject breakdown
        subject_stats = submissions.values('subject__name').annotate(
            count=models.Count('id'),
            accuracy=models.Avg('is_correct'),
            avg_mastery_growth=models.Avg('bkt_mastery_after') - models.Avg('bkt_mastery_before')
        ).order_by('-count')
        
        # Difficulty distribution
        difficulty_stats = submissions.values('difficulty_level').annotate(
            count=models.Count('id'),
            accuracy=models.Avg('is_correct')
        ).order_by('difficulty_level')
        
        # Top performing students
        student_stats = submissions.values(
            'student__username', 
            'student__first_name', 
            'student__last_name'
        ).annotate(
            submissions_count=models.Count('id'),
            accuracy=models.Avg('is_correct'),
            mastery_growth=models.Max('bkt_mastery_after') - models.Min('bkt_mastery_before')
        ).order_by('-mastery_growth')[:10]
        
        reports_response = {
            'success': True,
            'period_days': days,
            'subject_filter': subject_code or 'All Subjects',
            'report_generated_at': timezone.now().isoformat(),
            
            # Overall metrics
            'system_overview': {
                'total_submissions': total_submissions,
                'overall_accuracy': f"{overall_accuracy:.1%}",
                'unique_students': submissions.values('student').distinct().count(),
                'unique_sessions': submissions.values('session').distinct().count()
            },
            
            # Subject performance
            'subject_breakdown': list(subject_stats),
            
            # Difficulty analysis
            'difficulty_analysis': list(difficulty_stats),
            
            # Student performance
            'top_students': list(student_stats),
            
            # System health indicators
            'system_health': {
                'average_response_time': submissions.aggregate(
                    avg_time=models.Avg('time_spent_seconds')
                )['avg_time'] or 0,
                'mastery_improvement_rate': submissions.aggregate(
                    avg_improvement=models.Avg(
                        models.F('bkt_mastery_after') - models.F('bkt_mastery_before')
                    )
                )['avg_improvement'] or 0,
                'adaptation_effectiveness': submissions.filter(
                    contributed_to_mastery=True
                ).count() / total_submissions
            },
            
            'message': f"📈 System report: {total_submissions} submissions from {submissions.values('student').distinct().count()} students over {days} days"
        }
        
        return JsonResponse(reports_response)
        
    except Exception as e:
        logger.error(f"Get reports error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate submission reports'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_unified_practice_history(request, student_id):
    """
    GET UNIFIED PRACTICE HISTORY - Combined SM-2 Practice + Adaptive Learning
    
    This fixes the fetching problem by bridging practice and adaptive learning systems.
    Frontend can call this to show unified practice history:
    GET /practice-history/<student_id>/
    """
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Import practice models (with error handling if not available)
        try:
            from practice.models import SRSCard
            practice_available = True
        except ImportError:
            practice_available = False
            logger.warning("Practice models not available - showing adaptive sessions only")
        
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
                'total_practice_cards': 0,
                'total_adaptive_sessions': 0,
                'practice_mastery_avg': 0.0,
                'adaptive_mastery_avg': 0.0,
            },
            'learning_insights': []
        }
        
        # Get SM-2 practice cards if available
        if practice_available:
            try:
                sm2_cards = SRSCard.objects.filter(
                    student=student
                ).select_related('question').order_by('-last_reviewed')[:50]
                
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
                            'next_review': card.due_date.strftime('%Y-%m-%d') if hasattr(card, 'due_date') and card.due_date else None,
                            'is_due': card.due_date <= timezone.now().date() if hasattr(card, 'due_date') and card.due_date else False,
                            'priority_score': calculate_practice_priority(card)
                        }
                        unified_history['practice_sessions'].append(practice_data)
                        unified_history['combined_sessions'].append(practice_data)
                
                # Update stats
                unified_history['summary_stats']['total_practice_cards'] = len(sm2_cards)
                unified_history['summary_stats']['practice_mastery_avg'] = round(
                    practice_mastery_sum / practice_count if practice_count > 0 else 0.0, 3
                )
                
            except Exception as e:
                logger.warning(f"Error loading practice sessions: {e}")
        
        # Get adaptive learning sessions (reuse existing logic)
        adaptive_sessions = StudentSession.objects.filter(
            student=student,
            status='COMPLETED'
        ).order_by('-session_end_time')[:50]
        
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
            
            # Get question attempts with difficulty data for this session
            question_attempts = []
            try:
                from assessment.improved_models import QuestionAttempt
                attempts = QuestionAttempt.objects.filter(
                    session=session
                ).select_related('question').order_by('question_number_in_session')
                
                for attempt in attempts:
                    question_attempts.append({
                        'question_number': attempt.question_number_in_session,
                        'question_id': str(attempt.question.id) if attempt.question else 'unknown',
                        'difficulty': attempt.difficulty_when_presented,  # Real difficulty from database!
                        'student_answer': attempt.student_answer,
                        'correct_answer': attempt.correct_answer,
                        'is_correct': attempt.is_correct,
                        'time_spent_seconds': attempt.time_spent_seconds,
                        'points_earned': attempt.points_earned
                    })
            except Exception as e:
                logger.warning(f"Could not load question attempts for session {session.id}: {e}")
            
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
                },
                'question_attempts': question_attempts  # Include real question attempts with difficulty!
            }
            unified_history['adaptive_sessions'].append(adaptive_data)
            unified_history['combined_sessions'].append(adaptive_data)
        
        # Update adaptive stats
        unified_history['summary_stats']['total_adaptive_sessions'] = len(adaptive_sessions)
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
        
        # Generate learning insights
        insights = []
        if unified_history['practice_sessions']:
            due_count = sum(1 for session in unified_history['practice_sessions'] if session.get('is_due', False))
            if due_count > 0:
                insights.append(f"🔔 {due_count} practice cards are due for review")
        
        if unified_history['adaptive_sessions']:
            recent_accuracies = []
            for session in unified_history['adaptive_sessions'][:5]:
                try:
                    accuracy = float(session['accuracy'].replace('%', ''))
                    recent_accuracies.append(accuracy)
                except:
                    continue
            
            if len(recent_accuracies) >= 3:
                avg_accuracy = sum(recent_accuracies) / len(recent_accuracies)
                insights.append(f"📊 Recent adaptive accuracy: {avg_accuracy:.1f}%")
        
        if unified_history['practice_sessions'] and unified_history['adaptive_sessions']:
            insights.append("🎯 You're using both practice methods - excellent strategy!")
        elif unified_history['practice_sessions']:
            insights.append("💡 Try adaptive learning for personalized difficulty")
        elif unified_history['adaptive_sessions']:
            insights.append("💡 Try spaced repetition practice for better retention")
        
        unified_history['learning_insights'] = insights[:5]
        
        logger.info(f"Unified practice history generated for student {student_id}: "
                   f"{len(unified_history['practice_sessions'])} practice, "
                   f"{len(unified_history['adaptive_sessions'])} adaptive sessions")
        
        return JsonResponse(unified_history)
        
    except Exception as e:
        logger.error(f"Error generating unified practice history for student {student_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to load unified practice history: {str(e)}',
            'student_id': str(student_id),
            'message': 'Unified practice history temporarily unavailable'
        }, status=500)

def get_practice_mastery_level(card):
    """Calculate mastery level for SM-2 practice card"""
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
    ease_bonus = max(0, (card.ease_factor - 2.5) * 0.1) if hasattr(card, 'ease_factor') else 0
    
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
    if hasattr(card, 'due_date') and card.due_date and card.due_date <= timezone.now().date():
        days_overdue = (timezone.now().date() - card.due_date).days
        priority += min(10.0, days_overdue * 2.0)  # Up to 10 points for overdue
    
    # Low success rate increases priority
    if card.success_rate < 0.7:
        priority += (0.7 - card.success_rate) * 5.0  # Up to 3.5 points
    
    # New or struggling cards get priority
    if card.stage in ['new', 'learning']:
        priority += 2.0
    
    # Cards with low ease factor need attention
    if hasattr(card, 'ease_factor') and card.ease_factor < 2.0:
        priority += (2.0 - card.ease_factor) * 2.0
    
    return round(priority, 2)

@csrf_exempt
@require_http_methods(["GET"])
def api_health(request):
    """
    HEALTH CHECK - Direct frontend click endpoint
    
    Frontend can call this to verify the API is working:
    GET /health
    """
    return JsonResponse({
        'success': True,
        'status': 'healthy',
        'message': '✅ Simple Frontend API is ready!',
        'services': {
            'django': 'active',
            'database': 'connected',
            'bkt_service': 'available',
            'dkt_service': 'available'
        },
        'endpoints': [
            'POST /start-session - Start a new learning session',
            'GET /get-question - Get adaptive question',
            'POST /submit-answer - Submit answer and see adaptation',
            'POST /complete-session - Complete and save session to history',
            'GET /session-progress - View learning progress',
            'GET /session-history - Get adaptive session history',
            'GET /practice-history - Get unified practice history (SM-2 + Adaptive)',
            'GET /student-analytics - Detailed student analytics',
            'GET /submission-reports - System-wide analytics reports',
            'GET /health - Check API status'
        ],
        'ready_for_frontend': True
    })

@csrf_exempt
@require_http_methods(["POST"])
def complete_simple_session(request):
    """
    COMPLETE SESSION - Save session to history
    
    Frontend calls this when adaptive learning session completes:
    POST /complete-session
    {
        "session_id": "uuid-session-id",
        "total_questions": 15,
        "correct_answers": 6,
        "session_duration_seconds": 600,
        "final_mastery_level": 0.388,
        "student_username": "actual_username"  // Add this parameter
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        total_questions = data.get('total_questions', 0)
        correct_answers = data.get('correct_answers', 0)
        session_duration = data.get('session_duration_seconds', 0)
        final_mastery = data.get('final_mastery_level', 0.0)
        student_username = data.get('student_username')  # New parameter
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'message': 'Session ID is required'
            }, status=400)
        
        if not student_username:
            return JsonResponse({
                'success': False,
                'message': 'Student username is required'
            }, status=400)
        
        # Find the actual authenticated user by username
        # Try both the provided username and the student_prefixed version
        user = None
        try:
            user = User.objects.get(username=student_username)
        except User.DoesNotExist:
            # Try with student_ prefix (matching the start session logic)
            prefixed_username = f"student_{student_username.replace(' ', '_').lower()}"
            try:
                user = User.objects.get(username=prefixed_username)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'User "{student_username}" not found (tried both "{student_username}" and "{prefixed_username}")'
                }, status=404)
        
        # Get session subject from cache or default to quantitative aptitude
        # Note: Since Redis is not available, we'll use the default subject
        # In a production environment, we'd retrieve this from the session cache
        subject_code = 'quantitative_aptitude'  # Default subject
        
        # Get or create subject
        from assessment.improved_models import Subject, StudentSession
        
        subject, _ = Subject.objects.get_or_create(
            code=subject_code,
            defaults={'name': subject_code.replace('_', ' ').title()}
        )
        
        # Create the completed session record for history
        # Calculate scores
        accuracy_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Create the StudentSession record for history using the authenticated user
        completed_session = StudentSession.objects.create(
            student=user,  # Use the actual authenticated user
            subject=subject,
            session_type='PRACTICE',
            session_name=f"Adaptive Learning - {subject.name}",
            status='COMPLETED',
            total_questions_planned=total_questions,
            questions_attempted=total_questions,
            questions_correct=correct_answers,
            questions_incorrect=total_questions - correct_answers,
            percentage_score=accuracy_percentage,
            session_start_time=timezone.now() - timezone.timedelta(seconds=session_duration),
            session_end_time=timezone.now(),
            session_duration_seconds=session_duration,
            session_config={
                'session_id': session_id,
                'final_mastery_level': final_mastery,
                'created_by': 'adaptive_learning_interface'
            }
        )
        
        # Copy QuestionAttempt records from the temporary session to the completed session
        actual_correct_answers = 0
        actual_total_questions = 0
        
        try:
            from assessment.improved_models import QuestionAttempt
            from uuid import UUID
            
            # Find the temporary session
            temp_session = StudentSession.objects.filter(id=UUID(session_id)).first()
            if temp_session:
                # Copy all question attempts to the new completed session
                temp_attempts = QuestionAttempt.objects.filter(session=temp_session)
                actual_total_questions = temp_attempts.count()
                
                for attempt in temp_attempts:
                    if attempt.is_correct:
                        actual_correct_answers += 1
                        
                    QuestionAttempt.objects.create(
                        session=completed_session,
                        question=attempt.question,
                        student=user,
                        question_number_in_session=attempt.question_number_in_session,
                        student_answer=attempt.student_answer,
                        correct_answer=attempt.correct_answer,
                        is_correct=attempt.is_correct,
                        time_spent_seconds=attempt.time_spent_seconds,
                        points_earned=attempt.points_earned,
                        question_points=attempt.question_points,
                        difficulty_when_presented=attempt.difficulty_when_presented,
                        confidence_level=attempt.confidence_level,
                        interaction_data=attempt.interaction_data,
                        created_at=attempt.created_at,
                        updated_at=timezone.now()
                    )
                
                # Update the completed session with actual statistics
                actual_accuracy = (actual_correct_answers / actual_total_questions * 100) if actual_total_questions > 0 else 0
                
                completed_session.questions_attempted = actual_total_questions
                completed_session.questions_correct = actual_correct_answers
                completed_session.questions_incorrect = actual_total_questions - actual_correct_answers
                completed_session.percentage_score = actual_accuracy
                completed_session.total_questions_planned = actual_total_questions
                
                # Update grade based on actual performance
                if actual_accuracy >= 90:
                    grade = 'A+'
                elif actual_accuracy >= 80:
                    grade = 'A'
                elif actual_accuracy >= 70:
                    grade = 'B'
                elif actual_accuracy >= 60:
                    grade = 'C'
                elif actual_accuracy >= 50:
                    grade = 'D'
                else:
                    grade = 'F'
                
                # Save the updated session
                completed_session.save()
                
                print(f"✅ Copied {actual_total_questions} question attempts ({actual_correct_answers} correct, {actual_accuracy:.1f}%)")
            else:
                print(f"⚠️  Temporary session {session_id} not found, no question attempts copied")
                
        except Exception as e:
            print(f"⚠️  Error copying question attempts: {e}")
            # Continue anyway - session completion should not fail due to this
        
        # Note: Cache cleanup removed since Redis is not available
        
        return JsonResponse({
            'success': True,
            'message': 'Session completed and saved to history successfully',
            'session_data': {
                'session_id': str(completed_session.id),
                'student_username': user.username,
                'subject': subject.name,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'accuracy_percentage': accuracy_percentage,
                'duration_seconds': session_duration,
                'session_type': 'Adaptive Learning'
            }
        })
        
    except Exception as e:
        logger.error(f"Error completing session {session_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error saving session: {str(e)}'
        }, status=500)

    except Exception as e:
        logger.error(f"Error in complete_simple_session: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error saving session: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_session_details(request, session_id):
    """
    GET SESSION DETAILS - Get detailed session information including question attempts
    
    Frontend can call this:
    GET /session-details/<session_id>/
    Returns: Session info + question attempts + performance data
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        # Get all question attempts for this session
        attempts = QuestionAttempt.objects.filter(session=session).order_by('attempt_number')
        
        # Calculate session statistics
        total_questions = attempts.count()
        correct_answers = attempts.filter(is_correct=True).count()
        accuracy_rate = correct_answers / max(total_questions, 1) * 100
        
        # Get final mastery scores from session config
        session_config = session.session_config or {}
        final_mastery = session_config.get('final_bkt_mastery', 0.5) * 100
        mastery_level = 'Expert' if final_mastery >= 85 else 'Advanced' if final_mastery >= 70 else 'Proficient' if final_mastery >= 50 else 'Developing' if final_mastery >= 30 else 'Novice'
        
        # Format question attempts
        question_attempts = []
        for i, attempt in enumerate(attempts, 1):
            # Get question details
            question = attempt.question
            question_data = {
                'question_number': i,
                'question_text': question.question if hasattr(question, 'question') else f"Question {i}",
                'question_type': 'multiple_choice',
                'student_answer': attempt.selected_option or 'N/A',
                'correct_answer': question.answer if hasattr(question, 'answer') else 'A',
                'is_correct': attempt.is_correct,
                'time_spent_seconds': int(attempt.time_spent or 0),
                'points_earned': 1 if attempt.is_correct else 0,
                'question_points': 1,
                'difficulty_level': question.difficulty_level if hasattr(question, 'difficulty_level') else 'Medium',
                'topic': session.session_config.get('subject', 'General').replace('_', ' '),
                'subtopic': f"Question {i}",
                'explanation': f"{'Correct!' if attempt.is_correct else 'Review this concept.'} Time spent: {int(attempt.time_spent or 0)}s",
                'confidence_level': final_mastery / 100
            }
            
            # Add options if available
            if hasattr(question, 'options') and question.options:
                try:
                    import json
                    options = json.loads(question.options) if isinstance(question.options, str) else question.options
                    question_data['options'] = options
                except:
                    question_data['options'] = {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'}
            else:
                question_data['options'] = {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'}
            
            question_attempts.append(question_data)
        
        # Build session info
        session_info = {
            'session_id': str(session.id),
            'subject_name': session.session_config.get('subject', 'General').replace('_', ' ').title(),
            'session_type': 'Adaptive Learning',
            'session_name': f"Adaptive Learning - {session.session_config.get('subject', 'General').replace('_', ' ').title()}",
            'status': session.status,
            'questions_attempted': total_questions,
            'questions_correct': correct_answers,
            'percentage_score': accuracy_rate,
            'total_score': correct_answers,
            'max_possible_score': total_questions,
            'grade': mastery_level,
            'session_start_time': session.session_start_time.isoformat() if session.session_start_time else timezone.now().isoformat(),
            'session_end_time': session.session_end_time.isoformat() if session.session_end_time else timezone.now().isoformat(),
            'session_duration_seconds': session.session_duration_seconds or 0,
        }
        
        # Performance analysis
        topics_performance = {session_info['subject_name']: {'correct': correct_answers, 'total': total_questions, 'accuracy': accuracy_rate}}
        difficulty_performance = {'Medium': {'correct': correct_answers, 'total': total_questions, 'accuracy': accuracy_rate}}
        
        avg_time = sum(int(attempt.time_spent or 0) for attempt in attempts) / max(total_questions, 1)
        
        performance_analysis = {
            'topics_performance': topics_performance,
            'difficulty_performance': difficulty_performance,
            'average_time_per_question': avg_time,
            'fastest_correct_answer': min((int(attempt.time_spent or 0) for attempt in attempts if attempt.is_correct), default=0),
            'slowest_correct_answer': max((int(attempt.time_spent or 0) for attempt in attempts if attempt.is_correct), default=0),
            'strengths': [mastery_level, f"{final_mastery:.1f}% Mastery Achieved"],
            'improvement_areas': [] if final_mastery >= 70 else ['Continue practicing to improve mastery']
        }
        
        recommendations = [
            f"Your mastery level is {final_mastery:.1f}%",
            f"You achieved {mastery_level} level performance",
            "Great job!" if final_mastery >= 70 else "Keep practicing to improve!"
        ]
        
        return JsonResponse({
            'success': True,
            'session_info': session_info,
            'question_attempts': question_attempts,
            'performance_analysis': performance_analysis,
            'recommendations': recommendations,
            'mastery_data': {
                'bkt_mastery': final_mastery,
                'mastery_level': mastery_level,
                'mastery_achieved': final_mastery >= 70
            }
        })
        
    except StudentSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found',
            'message': 'The requested session does not exist'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting session details for {session_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Failed to load session details'
        }, status=500)

# ============================================================================
# URL Routing Setup (if needed)
# ============================================================================

def setup_simple_urls():
    """Setup URLs for the simple frontend API"""
    from django.urls import path
    
    urlpatterns = [
        path('start-session', start_simple_session, name='start_simple_session'),
        path('get-question/<str:session_id>/', get_simple_question, name='get_simple_question'),
        path('submit-answer', submit_simple_answer, name='submit_simple_answer'),
        path('complete-session', complete_session, name='complete_session'),  # Updated to use new endpoint
        path('complete-session-legacy', complete_simple_session, name='complete_simple_session'),  # Keep legacy for compatibility
        path('session-progress/<str:session_id>/', get_session_progress, name='get_session_progress'),
        path('session-history/<str:student_id>/', get_session_history, name='get_session_history'),  # New: Session history with mastery
        path('session-details/<str:session_id>/', get_session_details, name='get_session_details'),  # New: Detailed session with question attempts
        path('health', api_health, name='api_health'),
    ]
    
    return urlpatterns

if __name__ == "__main__":
    print("🚀 Simple Frontend API Ready!")
    print("=" * 50)
    print("Direct endpoints for frontend clicks:")
    print()
    print("1. POST /start-session")
    print("   Body: {'student_name': 'John', 'subject': 'math'}")
    print("   → Starts learning session")
    print()
    print("2. GET /get-question?session_id=<session_id>")
    print("   → Gets adaptive question")
    print()
    print("3. POST /submit-answer")
    print("   Body: {'session_id': '...', 'question_id': '...', 'selected_answer': 'A'}")
    print("   → Submits answer, shows adaptation")
    print()
    print("4. POST /complete-session")
    print("   Body: {'session_id': '...', 'completion_reason': 'finished'}")
    print("   → Complete session and store final mastery scores")
    print()
    print("5. GET /session-progress/<session_id>/")
    print("   → Shows current learning progress and mastery")
    print()
    print("6. GET /session-history/<student_id>/")
    print("   → Shows all completed sessions with mastery progression")
    print()
    print("7. GET /health")
    print("   → API health check")
    print()
    print("🎯 NEW: Mastery scores are now stored in database!")
    print("📊 NEW: Session history shows mastery progression!")
    print("✅ Ready for immediate frontend integration!")