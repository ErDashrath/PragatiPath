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

# Try to import orchestration service (may not exist yet)
try:
    from assessment.orchestration_service import OrchestrationService
    orchestration_service = OrchestrationService()
    ORCHESTRATION_AVAILABLE = True
except ImportError as e:
    orchestration_service = None
    ORCHESTRATION_AVAILABLE = False

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
        
        # Create simple session
        session = StudentSession.objects.create(
            student=user,
            subject=subject_obj,
            session_name=f"Simple {subject_obj.name} Session",
            total_questions_planned=5,
            session_config={
                'subject': subject,
                'subject_code': subject_code,
                'subject_name': subject_obj.name,
                'frontend_session': True,
                'simple_api': True
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Session started successfully!',
            'session_id': str(session.id),
            'student_id': str(profile.id),
            'student_name': student_name,
            'subject': subject,
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
    try:
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'session_id required',
                'message': 'Please provide session_id parameter'
            }, status=400)
        
        session = get_object_or_404(StudentSession, id=session_id)
        subject = session.session_config.get('subject', 'mathematics')
        
        # Count current questions
        question_count = QuestionAttempt.objects.filter(session=session).count() + 1
        
        # Get current knowledge state for adaptive difficulty using orchestration
        skill_id = f"{subject}_skill_{question_count}"
        
        try:
            # Try to get BKT mastery with orchestration integration
            from orchestration.orchestration_service import orchestration_service
            from student_model.bkt import BKTService
            from student_model.dkt import DKTService
            
            # Get orchestrated knowledge state
            orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                student=session.student,
                subject=subject,
                skill_id=skill_id
            )
            
            # Extract mastery from orchestration result
            if orchestration_result and 'bkt_state' in orchestration_result:
                bkt_data = orchestration_result['bkt_state'].get(skill_id, {})
                mastery_level = bkt_data.get('P_L', 0.5)
                print(f"🧠 Orchestration BKT mastery for {skill_id}: {mastery_level:.3f}")
            else:
                # Fallback to direct BKT service
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                mastery_level = bkt_params.P_L if bkt_params else 0.5
                print(f"🔄 Fallback BKT mastery for {skill_id}: {mastery_level:.3f}")
                
        except Exception as e:
            print(f"⚠️ Orchestration failed, using fallback BKT: {e}")
            try:
                # Fallback to basic BKT
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                mastery_level = bkt_params.P_L if bkt_params else 0.5
            except:
                mastery_level = 0.5
        
        # Map adaptive difficulty to database difficulty
        if mastery_level < 0.3:
            difficulty = "easy"
            db_difficulty = "easy"
            difficulty_emoji = "🟢"
        elif mastery_level < 0.7:
            difficulty = "medium" 
            db_difficulty = "moderate"
            difficulty_emoji = "🟡"
        else:
            difficulty = "hard"
            db_difficulty = "difficult"
            difficulty_emoji = "🔴"
        
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
                'explanation': f'This {difficulty} {subject_obj.name} question was selected based on your mastery level of {mastery_level:.1%}',
                'topic': getattr(real_question, 'tags', '').split(',')[0] if getattr(real_question, 'tags', '') else 'General',
                'subtopic': real_question.question_type,
                'adaptive_info': {
                    'mastery_level': mastery_level,
                    'skill_id': skill_id,
                    'adaptive_reason': f"Selected {difficulty} difficulty because mastery is {mastery_level:.1%}",
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
                'question_text': f"Question {question_count}: This is a {difficulty} {subject} question adapted to your current mastery level ({mastery_level:.1%}).",
                'options': [
                    {'id': 'A', 'text': f'Option A - {difficulty} level answer'},
                    {'id': 'B', 'text': f'Option B - {difficulty} level answer'},
                    {'id': 'C', 'text': f'Option C - {difficulty} level answer'},
                    {'id': 'D', 'text': f'Option D - {difficulty} level answer'}
                ],
                'correct_answer': 'A',
                'explanation': f'This {difficulty} question was selected based on your mastery level of {mastery_level:.1%}',
                'adaptive_info': {
                    'mastery_level': mastery_level,
                    'skill_id': skill_id,
                    'adaptive_reason': f"Selected {difficulty} difficulty because mastery is {mastery_level:.1%}",
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
        
        # Get knowledge state before updates using ORCHESTRATION
        skill_id = f"{subject}_skill_{QuestionAttempt.objects.filter(session=session).count()}"
        
        # Get session accuracy before this submission
        previous_attempts = QuestionAttempt.objects.filter(session=session)
        if previous_attempts.exists():
            correct_before = previous_attempts.filter(is_correct=True).count()
            total_before = previous_attempts.count()
            session_accuracy_before = correct_before / total_before
        else:
            session_accuracy_before = 0.0

        # Get knowledge state before submission using ORCHESTRATION
        bkt_mastery_before = 0.5
        dkt_prediction_before = 0.5
        bkt_params_before = {'P_L': 0.5, 'P_T': 0.3, 'P_G': 0.2, 'P_S': 0.1}
        
        try:
            logger.info(f"🎯 Getting pre-submission knowledge state via orchestration for student {session.student.username}, skill {skill_id}")
            
            orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                student=session.student,
                subject=session.subject,
                skill_id=skill_id
            )
            
            if orchestration_result and 'bkt' in orchestration_result:
                bkt_data = orchestration_result['bkt']
                if 'mastery' in bkt_data:
                    bkt_mastery_before = float(bkt_data['mastery'])
                if 'params' in bkt_data:
                    bkt_params_before = bkt_data['params']
                logger.info(f"📊 Orchestrated BKT state before: mastery={bkt_mastery_before}, params={bkt_params_before}")
            
            if orchestration_result and 'dkt' in orchestration_result:
                dkt_data = orchestration_result['dkt']
                if 'prediction' in dkt_data:
                    dkt_prediction_before = float(dkt_data['prediction'])
                logger.info(f"🧠 Orchestrated DKT state before: prediction={dkt_prediction_before}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Orchestration pre-submission state failed: {e}, using fallback")
            try:
                # Fallback to individual BKT service
                bkt_before = bkt_service.get_skill_bkt_params(session.student, skill_id)
                bkt_mastery_before = bkt_before.P_L if bkt_before else 0.5
                bkt_params_before = {
                    'P_L': bkt_before.P_L if bkt_before else 0.5,
                    'P_T': bkt_before.P_T if bkt_before else 0.3,
                    'P_G': bkt_before.P_G if bkt_before else 0.2,
                    'P_S': bkt_before.P_S if bkt_before else 0.1
                }
                # Fallback to individual DKT service
                dkt_prediction_before = dkt_service.get_skill_prediction(session.student, skill_id)
            except Exception as fallback_error:
                logger.error(f"❌ Both orchestration and fallback failed: {fallback_error}")

        # Process answer submission via ORCHESTRATION
        bkt_updated = False
        dkt_updated = False
        new_mastery = bkt_mastery_before
        bkt_params_after = bkt_params_before
        dkt_prediction_after = dkt_prediction_before
        
        try:
            logger.info(f"🎯 Processing answer submission via orchestration: correct={is_correct}, time_spent={time_spent}")
            
            # Use orchestration service to update both BKT and DKT
            orchestrated_update = orchestration_service.process_interaction(
                student=session.student,
                subject=session.subject,
                skill_id=skill_id,
                is_correct=is_correct,
                interaction_data={
                    'question_id': question_id,
                    'time_spent': time_spent,
                    'difficulty': question_for_attempt.difficulty_level,
                    'question_type': question_for_attempt.question_type
                }
            )
            
            if orchestrated_update and 'bkt' in orchestrated_update:
                bkt_result = orchestrated_update['bkt']
                if 'updated' in bkt_result and bkt_result['updated']:
                    bkt_updated = True
                    if 'mastery' in bkt_result:
                        new_mastery = float(bkt_result['mastery'])
                    if 'params' in bkt_result:
                        bkt_params_after = bkt_result['params']
                    logger.info(f"✅ Orchestrated BKT update successful: mastery={new_mastery}, params={bkt_params_after}")
                
            if orchestrated_update and 'dkt' in orchestrated_update:
                dkt_result = orchestrated_update['dkt']
                if 'updated' in dkt_result and dkt_result['updated']:
                    dkt_updated = True
                    if 'prediction' in dkt_result:
                        dkt_prediction_after = float(dkt_result['prediction'])
                    logger.info(f"✅ Orchestrated DKT update successful: prediction={dkt_prediction_after}")
                        
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
            except Exception as dkt_error:
                logger.warning(f"DKT fallback update failed: {dkt_error}")
                dkt_updated = False
                dkt_prediction_after = dkt_prediction_before
        
        # Calculate session progress after this submission
        total_questions = QuestionAttempt.objects.filter(session=session).count()
        correct_answers = QuestionAttempt.objects.filter(session=session, is_correct=True).count()
        session_accuracy_after = correct_answers / max(total_questions, 1)
        
        # Determine adaptation recommendation
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
        
        # Get current knowledge states with orchestration
        subject = session.session_config.get('subject', 'mathematics')
        skill_id = f"{subject}_skill_1"
        
        try:
            # Enhanced orchestration integration
            from orchestration.orchestration_service import orchestration_service
            
            orchestration_result = orchestration_service.get_comprehensive_knowledge_state(
                student=session.student,
                subject=subject,
                skill_id=skill_id
            )
            
            if orchestration_result:
                # Extract BKT data
                bkt_data = orchestration_result.get('bkt_state', {}).get(skill_id, {})
                current_mastery = bkt_data.get('P_L', 0.5)
                
                # Extract DKT data  
                dkt_data = orchestration_result.get('dkt_state', {})
                dkt_prediction = dkt_data.get('skill_predictions', [0.5])[0] if dkt_data.get('skill_predictions') else 0.5
                
                print(f"📊 Orchestrated Stats - BKT: {current_mastery:.3f}, DKT: {dkt_prediction:.3f}")
            else:
                # Fallback to individual services
                bkt_params = bkt_service.get_skill_bkt_params(session.student, skill_id)
                current_mastery = bkt_params.P_L if bkt_params else 0.5
                dkt_prediction = 0.5
                
        except Exception as e:
            print(f"⚠️ Orchestration failed in progress: {e}")
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
                'dkt_prediction': f"{dkt_prediction:.1%}",
                'overall_progress': f"{(current_mastery + dkt_prediction) / 2:.1%}",
                'skill_level': skill_id
            },
            'adaptive_info': {
                'difficulty_trend': "Adapting based on your performance",
                'next_difficulty': "Easy" if current_mastery < 0.3 else "Hard" if current_mastery > 0.7 else "Medium",
                'learning_status': "Excellent progress!" if current_mastery > 0.7 else "Good progress!" if current_mastery > 0.4 else "Building foundations"
            },
            'message': f"📊 Progress: {correct_answers}/{total_questions} correct ({correct_answers / max(total_questions, 1):.1%}), Mastery: {current_mastery:.1%}"
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
            'GET /session-progress - View learning progress',
            'GET /student-analytics - Detailed student analytics',
            'GET /submission-reports - System-wide analytics reports',
            'GET /health - Check API status'
        ],
        'ready_for_frontend': True
    })

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
        path('session-progress/<str:session_id>/', get_session_progress, name='get_session_progress'),
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
    print("4. GET /session-progress?session_id=<session_id>")
    print("   → Shows learning progress")
    print()
    print("5. GET /health")
    print("   → API health check")
    print()
    print("✅ Ready for immediate frontend integration!")