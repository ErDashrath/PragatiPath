"""
Adaptive Question Selector with BKT/DKT Integration

This module provides intelligent question selection based on student's knowledge state
using Bayesian Knowledge Tracing (BKT) and Deep Knowledge Tracing (DKT) algorithms.
"""

import logging
import random
from typing import List, Dict, Optional, Tuple, Any
from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import AdaptiveQuestion, StudentSession, QuestionAttempt
from student_model.bkt import BKTService, BKTParameters
from student_model.dkt import DKTService
from core.models import StudentProfile

logger = logging.getLogger(__name__)


class AdaptiveQuestionSelector:
    """
    Intelligent question selection system that uses BKT/DKT to select optimal questions
    for each student based on their current knowledge state and learning progress.
    """
    
    def __init__(self):
        self.dkt_service = DKTService()
        self.mastery_threshold = 0.95
        self.confidence_threshold = 0.7
        
    def select_questions(
        self, 
        user: User, 
        subject_code: str, 
        chapter_id: Optional[str] = None,
        question_count: int = 10,
        assessment_type: str = 'ADAPTIVE',
        session: Optional[StudentSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Select adaptive questions based on BKT/DKT analysis of student's knowledge state.
        
        Args:
            user: Student user object
            subject_code: Subject code for filtering questions
            chapter_id: Optional chapter ID for chapter-specific assessments
            question_count: Number of questions to select
            assessment_type: Type of assessment (ADAPTIVE, PRACTICE, etc.)
            session: Current assessment session
            
        Returns:
            List of selected questions with adaptive metadata
        """
        try:
            logger.info(f"Starting adaptive question selection for user {user.id}, subject {subject_code}")
            
            # Get student's knowledge state using BKT/DKT
            knowledge_state = self._get_student_knowledge_state(user, subject_code)
            
            # Get available questions
            available_questions = self._get_available_questions(
                user, subject_code, chapter_id, session
            )
            
            if not available_questions.exists():
                logger.warning(f"No available questions found for subject {subject_code}")
                return []
            
            # Select questions using adaptive algorithm
            selected_questions = self._adaptive_question_selection(
                available_questions, 
                knowledge_state, 
                question_count,
                assessment_type
            )
            
            logger.info(f"Selected {len(selected_questions)} questions using adaptive selection")
            return selected_questions
            
        except Exception as e:
            logger.error(f"Error in adaptive question selection: {e}")
            # Fallback to random selection
            return self._fallback_random_selection(
                subject_code, chapter_id, question_count, user, session
            )
    
    def _get_student_knowledge_state(self, user: User, subject_code: str) -> Dict[str, Any]:
        """
        Get comprehensive knowledge state using both BKT and DKT algorithms.
        
        Returns:
            Dictionary containing BKT parameters, DKT predictions, and recommendation
        """
        try:
            # Get BKT knowledge state for subject skills
            bkt_state = self._get_bkt_knowledge_state(user, subject_code)
            
            # Get DKT knowledge state 
            dkt_state = self._get_dkt_knowledge_state(user)
            
            # Determine recommended algorithm
            recommended_algo = self._choose_algorithm(bkt_state, dkt_state, user)
            
            return {
                'bkt_state': bkt_state,
                'dkt_state': dkt_state,
                'recommended_algorithm': recommended_algo,
                'subject_code': subject_code,
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge state: {e}")
            return {
                'bkt_state': {},
                'dkt_state': {},
                'recommended_algorithm': 'random',
                'error': str(e)
            }
    
    def _get_bkt_knowledge_state(self, user: User, subject_code: str) -> Dict[str, BKTParameters]:
        """Get BKT parameters for all skills in the subject."""
        bkt_state = {}
        
        # Define subject-specific skills (get from predefined list + dynamically from CSV)
        subject_skills = self._get_subject_skills(subject_code)
        
        # Also get skills dynamically from questions in database
        dynamic_skills = self._extract_skills_from_questions(subject_code)
        subject_skills.extend([skill for skill in dynamic_skills if skill not in subject_skills])
        
        for skill in subject_skills:
            try:
                bkt_params = BKTService.get_skill_bkt_params(user, skill)
                bkt_state[skill] = bkt_params
            except Exception as e:
                logger.debug(f"No BKT data for skill {skill}: {e}")
                # Initialize new skill with default parameters
                bkt_state[skill] = BKTParameters(
                    P_L0=0.1, P_T=0.3, P_G=0.2, P_S=0.1, P_L=0.1
                )
        
        return bkt_state
    
    def _get_dkt_knowledge_state(self, user: User) -> Dict[str, Any]:
        """Get DKT predictions for the student."""
        try:
            student_profile = StudentProfile.objects.get(user=user)
            
            # Get DKT predictions using integrated service
            dkt_predictions = self.dkt_service.get_all_predictions(user)
            dkt_state = self.dkt_service.get_dkt_state(user)
            
            return {
                'available': True,
                'skill_predictions': list(dkt_predictions.values()),
                'confidence': dkt_state.confidence,
                'sequence_length': len(dkt_state.interaction_sequence)
            }
                
        except Exception as e:
            logger.error(f"Error getting DKT state: {e}")
            return {'available': False, 'error': str(e)}
    
    def _build_interaction_sequence(self, user: User) -> List[Dict[str, Any]]:
        """Build interaction sequence for DKT from recent question attempts."""
        try:
            # Get recent question attempts (last 100 for efficiency)
            attempts = QuestionAttempt.objects.filter(
                session__student=user
            ).order_by('-created_at')[:100]
            
            sequence = []
            for attempt in attempts:
                sequence.append({
                    'skill_id': self._map_question_to_skill_id(attempt.question),
                    'is_correct': attempt.is_correct,
                    'response_time': attempt.response_time
                })
            
            return list(reversed(sequence))  # Chronological order
            
        except Exception as e:
            logger.error(f"Error building interaction sequence: {e}")
            return []
    
    def _map_question_to_skill_id(self, question: AdaptiveQuestion) -> int:
        """
        Map question to DKT skill ID (0-49) using CSV data structure.
        Uses subject, tags, and difficulty from your sample data.
        """
        # Subject-based skill mapping for your competitive exam data
        subject_mapping = {
            'data_interpretation': 0,
            'logical_reasoning': 10, 
            'quantitative_aptitude': 20,
            'verbal_ability': 30
        }
        
        # Difficulty refinement
        difficulty_offset = {
            'very_easy': 0,
            'easy': 2,
            'moderate': 4,
            'difficult': 6
        }
        
        # Get base skill from subject
        base_skill = subject_mapping.get(question.subject, 0)
        
        # Add difficulty offset
        difficulty_bonus = difficulty_offset.get(question.difficulty_level, 2)
        
        # Add variation based on tags (for granular skill tracking)
        if hasattr(question, 'tags') and question.tags:
            # Use first tag to create skill variations
            tag_hash = hash(question.tags.split(',')[0].strip()) % 4
            return min(49, base_skill + difficulty_bonus + tag_hash)
        
        return min(49, base_skill + difficulty_bonus)
    
    def _choose_algorithm(self, bkt_state: Dict, dkt_state: Dict, user: User) -> str:
        """
        Choose the best algorithm based on available data and confidence.
        
        Algorithm Selection Logic:
        1. If insufficient data (< 5 attempts): Use BKT (better for cold start)
        2. If DKT unavailable: Use BKT 
        3. If high disagreement between BKT/DKT: Use ensemble
        4. If sufficient data and DKT available: Use DKT
        5. Otherwise: Use BKT as fallback
        """
        try:
            # Count total interactions
            total_attempts = QuestionAttempt.objects.filter(session__student=user).count()
            
            if total_attempts < 5:
                return 'bkt'  # Cold start scenario
            
            if not dkt_state.get('available', False):
                return 'bkt'  # DKT unavailable
                
            # If both available, compare predictions
            if total_attempts >= 10 and dkt_state.get('confidence', 0) > self.confidence_threshold:
                return 'dkt'  # Sufficient data for DKT
            
            return 'ensemble'  # Use both when uncertain
            
        except Exception as e:
            logger.error(f"Error choosing algorithm: {e}")
            return 'bkt'  # Safe fallback
    
    def _get_subject_skills(self, subject_code: str) -> List[str]:
        """
        Define skills for each competitive exam subject based on your CSV data structure.
        Maps subjects to granular skills from tags in your sample data.
        """
        subject_skills_map = {
            # Data Interpretation skills from your CSV tags
            'data_interpretation': [
                'table_chart', 'bar_graph', 'pie_chart', 'line_graph',
                'percentage_calculation', 'ratio_analysis', 'trend_analysis',
                'comparative_analysis', 'data_extraction', 'statistical_interpretation'
            ],
            'DATA_INTERPRETATION': [
                'table_chart', 'bar_graph', 'pie_chart', 'line_graph',
                'percentage_calculation', 'ratio_analysis', 'trend_analysis'
            ],
            
            # Logical Reasoning skills from your CSV tags  
            'logical_reasoning': [
                'number_series', 'coding_decoding', 'blood_relations', 'direction_sense',
                'syllogism', 'classification', 'logical_sequence', 'puzzles',
                'seating_arrangement', 'ranking_order', 'pattern_recognition'
            ],
            'LOGICAL_REASONING': [
                'number_series', 'coding_decoding', 'blood_relations', 'direction_sense',
                'syllogism', 'classification', 'logical_sequence'
            ],
            
            # Quantitative Aptitude skills
            'quantitative_aptitude': [
                'arithmetic_basics', 'percentage_profit_loss', 'time_work_distance', 
                'algebra_equations', 'geometry_mensuration', 'probability_statistics',
                'number_systems', 'simplification', 'ratio_proportion', 'interest_calculations'
            ],
            'QUANTITATIVE_APTITUDE': [
                'arithmetic_basics', 'percentage_profit_loss', 'time_work_distance',
                'algebra_equations', 'geometry_mensuration', 'probability_statistics'
            ],
            
            # Verbal Ability skills
            'verbal_ability': [
                'reading_comprehension', 'vocabulary', 'grammar_usage', 'sentence_correction',
                'para_jumbles', 'fill_blanks', 'synonyms_antonyms', 'idioms_phrases',
                'error_detection', 'cloze_test', 'critical_reasoning'
            ],
            'VERBAL_ABILITY': [
                'reading_comprehension', 'vocabulary', 'grammar_usage', 'sentence_correction',
                'para_jumbles', 'fill_blanks', 'synonyms_antonyms'
            ],
            
            # Legacy support for old format
            'MATH': ['arithmetic_basics', 'algebra_equations', 'geometry_mensuration'],
        }
        
        return subject_skills_map.get(subject_code, ['general_knowledge'])
    
    def _extract_skills_from_questions(self, subject_code: str) -> List[str]:
        """
        Dynamically extract skills from your CSV data tags.
        This analyzes the 'tags' field from your questions to create granular skills.
        """
        try:
            # Get all unique tags for the subject from your CSV data
            questions = AdaptiveQuestion.objects.filter(subject=subject_code.lower())
            
            skills = set()
            for question in questions:
                if hasattr(question, 'tags') and question.tags:
                    # Extract skills from CSV tags field
                    tags = question.tags.split(',')
                    for tag in tags:
                        # Clean and normalize tag to skill format
                        skill = f"{subject_code.lower()}_{tag.strip().lower().replace(' ', '_')}"
                        skills.add(skill)
            
            return list(skills)
            
        except Exception as e:
            logger.warning(f"Error extracting skills from questions: {e}")
            return []
    
    def _adaptive_question_selection(
        self, 
        questions: QuerySet, 
        knowledge_state: Dict, 
        count: int,
        assessment_type: str
    ) -> List[Dict[str, Any]]:
        """
        Select questions using adaptive algorithm based on knowledge state.
        """
        selected_questions = []
        algorithm = knowledge_state.get('recommended_algorithm', 'random')
        
        if algorithm == 'bkt':
            selected_questions = self._bkt_based_selection(questions, knowledge_state, count)
        elif algorithm == 'dkt':
            selected_questions = self._dkt_based_selection(questions, knowledge_state, count)
        elif algorithm == 'ensemble':
            selected_questions = self._ensemble_selection(questions, knowledge_state, count)
        else:
            selected_questions = self._random_selection(questions, count)
        
        # Add adaptive metadata
        for i, question in enumerate(selected_questions):
            question.update({
                'selection_algorithm': algorithm,
                'selection_order': i + 1,
                'adaptive_metadata': {
                    'knowledge_state_snapshot': knowledge_state.get('bkt_state', {}),
                    'recommendation_confidence': knowledge_state.get('dkt_state', {}).get('confidence', 0.5),
                    'selection_timestamp': timezone.now().isoformat()
                }
            })
        
        return selected_questions
    
    def _bkt_based_selection(self, questions: QuerySet, knowledge_state: Dict, count: int) -> List[Dict]:
        """Select questions based on BKT mastery probabilities."""
        bkt_state = knowledge_state.get('bkt_state', {})
        
        # Find skills that need more practice (low mastery probability)
        weak_skills = []
        strong_skills = []
        
        for skill, params in bkt_state.items():
            if params.P_L < 0.6:  # Low mastery
                weak_skills.append(skill)
            elif params.P_L < self.mastery_threshold:  # Medium mastery
                weak_skills.append(skill)
            else:  # High mastery
                strong_skills.append(skill)
        
        selected = []
        
        # Prioritize questions for weak skills (70% of questions)
        weak_count = int(count * 0.7)
        if weak_skills and weak_count > 0:
            weak_questions = self._select_questions_for_skills(
                questions, weak_skills, weak_count, 'practice'
            )
            selected.extend(weak_questions)
        
        # Add some questions for reinforcement (30% of questions)
        remaining_count = count - len(selected)
        if remaining_count > 0:
            all_skills = weak_skills + strong_skills
            reinforcement_questions = self._select_questions_for_skills(
                questions, all_skills, remaining_count, 'reinforcement'
            )
            selected.extend(reinforcement_questions)
        
        return selected[:count]
    
    def _dkt_based_selection(self, questions: QuerySet, knowledge_state: Dict, count: int) -> List[Dict]:
        """Select questions based on DKT predictions."""
        dkt_state = knowledge_state.get('dkt_state', {})
        skill_predictions = dkt_state.get('skill_predictions', [])
        
        if not skill_predictions:
            return self._random_selection(questions, count)
        
        # Find skills with low prediction scores
        weak_skill_indices = [
            i for i, pred in enumerate(skill_predictions) 
            if pred < 0.7  # Low predicted mastery
        ]
        
        selected = []
        questions_list = list(questions.order_by('?'))
        
        for question in questions_list[:count * 2]:  # Get more questions to filter from
            skill_id = self._map_question_to_skill_id(question)
            
            # Prioritize questions for weak skills
            if skill_id in weak_skill_indices or len(selected) < count // 2:
                selected.append({
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'options': question.formatted_options,
                    'difficulty': question.difficulty_level,
                    'estimated_time': question.estimated_time_seconds,
                    'skill_id': skill_id,
                    'predicted_mastery': skill_predictions[skill_id] if skill_id < len(skill_predictions) else 0.5
                })
                
                if len(selected) >= count:
                    break
        
        return selected[:count]
    
    def _ensemble_selection(self, questions: QuerySet, knowledge_state: Dict, count: int) -> List[Dict]:
        """Combine BKT and DKT recommendations."""
        # Get recommendations from both algorithms
        bkt_questions = self._bkt_based_selection(questions, knowledge_state, count // 2)
        dkt_questions = self._dkt_based_selection(questions, knowledge_state, count - len(bkt_questions))
        
        # Merge and deduplicate
        selected_ids = set()
        ensemble_questions = []
        
        # Add BKT questions first
        for q in bkt_questions:
            if q['id'] not in selected_ids:
                q['selection_method'] = 'bkt_ensemble'
                ensemble_questions.append(q)
                selected_ids.add(q['id'])
        
        # Add DKT questions that weren't already selected
        for q in dkt_questions:
            if q['id'] not in selected_ids and len(ensemble_questions) < count:
                q['selection_method'] = 'dkt_ensemble'
                ensemble_questions.append(q)
                selected_ids.add(q['id'])
        
        return ensemble_questions[:count]
    
    def _select_questions_for_skills(
        self, 
        questions: QuerySet, 
        target_skills: List[str], 
        count: int, 
        purpose: str
    ) -> List[Dict]:
        """
        Select questions that target specific skills using your CSV data structure.
        Matches questions based on subject + tags from your competitive exam data.
        """
        selected = []
        
        # Map skills to question difficulties from your CSV structure
        skill_difficulty_map = {
            'practice': ['very_easy', 'easy'],  # For weak skills
            'reinforcement': ['moderate', 'difficult']  # For challenging skills
        }
        
        target_difficulties = skill_difficulty_map.get(purpose, ['moderate'])
        
        # For each target skill, find matching questions
        for skill in target_skills:
            # Extract subject and tag from skill format (e.g., "data_interpretation_table_chart")
            skill_parts = skill.split('_')
            if len(skill_parts) >= 2:
                subject = skill_parts[0]
                tag_pattern = '_'.join(skill_parts[1:])
                
                # Find questions matching subject and tag pattern
                skill_questions = questions.filter(
                    subject=subject,
                    tags__icontains=tag_pattern.replace('_', ' '),
                    difficulty_level__in=target_difficulties
                ).order_by('?')[:count // len(target_skills) + 1]
                
            else:
                # Fallback: just filter by difficulty
                skill_questions = questions.filter(
                    difficulty_level__in=target_difficulties
                ).order_by('?')[:count // len(target_skills) + 1]
            
            # Convert to dict format
            for question in skill_questions:
                if len(selected) >= count:
                    break
                    
                selected.append({
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'options': self._format_question_options(question),
                    'difficulty': question.difficulty_level,
                    'subject': question.subject,
                    'tags': question.tags,
                    'estimated_time': getattr(question, 'estimated_time_seconds', 60),
                    'target_skills': [skill],
                    'selection_purpose': purpose
                })
            
            if len(selected) >= count:
                break
        
        return selected[:count]
    
    def _format_question_options(self, question) -> List[Dict]:
        """Format question options from your CSV structure (option_a, option_b, etc.)"""
        return [
            {'key': 'a', 'text': getattr(question, 'option_a', '')},
            {'key': 'b', 'text': getattr(question, 'option_b', '')}, 
            {'key': 'c', 'text': getattr(question, 'option_c', '')},
            {'key': 'd', 'text': getattr(question, 'option_d', '')}
        ]
    
    def _random_selection(self, questions: QuerySet, count: int) -> List[Dict]:
        """Fallback random selection."""
        selected = []
        
        for question in questions.order_by('?')[:count]:
            selected.append({
                'id': str(question.id),
                'question_text': question.question_text,
                'options': question.formatted_options,
                'difficulty': question.difficulty_level,
                'estimated_time': question.estimated_time_seconds,
                'selection_method': 'random_fallback'
            })
        
        return selected
    
    def _get_available_questions(
        self, 
        user: User, 
        subject_code: str, 
        chapter_id: Optional[str],
        session: Optional[StudentSession]
    ) -> QuerySet:
        """Get available questions filtering out recently attempted ones."""
        
        # Base filter
        question_filter = Q(subject=subject_code, is_active=True)
        
        # Add chapter filter if specified
        if chapter_id:
            question_filter &= Q(chapter_id=chapter_id)
        
        # Get questions attempted in recent sessions (last 5 sessions)
        recent_sessions = StudentSession.objects.filter(
            student=user
        ).order_by('-created_at')[:5]
        
        attempted_question_ids = []
        for recent_session in recent_sessions:
            attempts = QuestionAttempt.objects.filter(session=recent_session)
            attempted_question_ids.extend([attempt.question.id for attempt in attempts])
        
        # Exclude recently attempted questions
        if attempted_question_ids:
            question_filter &= ~Q(id__in=attempted_question_ids)
        
        return AdaptiveQuestion.objects.filter(question_filter)
    
    def _fallback_random_selection(
        self, 
        subject_code: str, 
        chapter_id: Optional[str], 
        count: int,
        user: User,
        session: Optional[StudentSession]
    ) -> List[Dict]:
        """Fallback to simple random selection when adaptive algorithms fail."""
        
        logger.warning("Using fallback random selection")
        
        question_filter = Q(subject=subject_code, is_active=True)
        if chapter_id:
            question_filter &= Q(chapter_id=chapter_id)
        
        questions = AdaptiveQuestion.objects.filter(question_filter).order_by('?')[:count]
        
        return [
            {
                'id': str(q.id),
                'question_text': q.question_text,
                'options': q.formatted_options,
                'difficulty': q.difficulty_level,
                'estimated_time': q.estimated_time_seconds,
                'selection_method': 'random_fallback',
                'fallback_reason': 'adaptive_algorithm_error'
            }
            for q in questions
        ]

    def get_next_adaptive_question(
        self, 
        user: User, 
        session: StudentSession,
        previous_answers: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next question during an ongoing assessment based on previous answers.
        
        This method provides real-time adaptation during assessment.
        """
        try:
            # Update knowledge state based on recent answers
            self._update_knowledge_state_realtime(user, previous_answers)
            
            # Get updated knowledge state
            knowledge_state = self._get_student_knowledge_state(user, session.subject_code)
            
            # Get available questions (excluding already attempted)
            attempted_ids = [
                attempt.question.id 
                for attempt in QuestionAttempt.objects.filter(session=session)
            ]
            
            available_questions = AdaptiveQuestion.objects.filter(
                subject=session.subject_code,
                is_active=True
            ).exclude(id__in=attempted_ids)
            
            if not available_questions.exists():
                return None
            
            # Select next question based on current state
            next_questions = self._adaptive_question_selection(
                available_questions, 
                knowledge_state, 
                1,  # Just one question
                session.assessment_type
            )
            
            return next_questions[0] if next_questions else None
            
        except Exception as e:
            logger.error(f"Error getting next adaptive question: {e}")
            # Return random question as fallback
            random_question = available_questions.order_by('?').first()
            if random_question:
                return {
                    'id': str(random_question.id),
                    'question_text': random_question.question_text,
                    'options': random_question.formatted_options,
                    'difficulty': random_question.difficulty_level,
                    'estimated_time': random_question.estimated_time_seconds,
                    'selection_method': 'fallback_random'
                }
            return None
    
    def _update_knowledge_state_realtime(self, user: User, recent_answers: List[Dict[str, Any]]):
        """Update BKT parameters in real-time based on recent answers."""
        try:
            for answer_data in recent_answers[-5:]:  # Last 5 answers
                skill_id = answer_data.get('skill_id')
                is_correct = answer_data.get('is_correct')
                
                if skill_id and is_correct is not None:
                    BKTService.update_skill_bkt(
                        user=user,
                        skill_id=skill_id,
                        is_correct=is_correct,
                        interaction_data=answer_data
                    )
                    
        except Exception as e:
            logger.error(f"Error updating real-time knowledge state: {e}")


# Singleton instance for easy access
adaptive_selector = AdaptiveQuestionSelector()