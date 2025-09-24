"""
LangGraph + Gemini AI Integration for Post-Exam Analysis
Provides comprehensive analysis, explanations, and personalized recommendations
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid
import logging

from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import MessageGraph
from pydantic import BaseModel, Field
import asyncio

# Django imports
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models for AI Analysis
# ============================================================================

@dataclass
class QuestionAnalysis:
    """Analysis for a single question"""
    question_id: str
    question_text: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    difficulty: str
    subject: str
    explanation: str
    concepts_tested: List[str]
    why_wrong: Optional[str] = None
    improvement_tips: List[str] = None

@dataclass
class SubjectAnalysis:
    """Analysis for a subject area"""
    subject: str
    questions_attempted: int
    correct_count: int
    accuracy_rate: float
    mastery_score: float
    weak_concepts: List[str]
    strong_concepts: List[str]
    improvement_strategies: List[str]
    recommended_topics: List[str]

@dataclass
class ExamSession:
    """Complete exam session data"""
    session_id: str
    student_id: str
    subject: str
    start_time: datetime
    end_time: datetime
    questions: List[QuestionAnalysis]
    overall_score: float
    time_spent: float
    assessment_mode: str  # 'EXAM' or 'PRACTICE'

class AIAnalysisState(BaseModel):
    """State for LangGraph workflow"""
    exam_session: Dict[str, Any]
    question_analyses: List[Dict[str, Any]] = []
    subject_analysis: Dict[str, Any] = {}
    personalized_recommendations: List[str] = []
    study_plan: List[Dict[str, Any]] = []
    bkt_integration: Dict[str, Any] = {}
    final_report: Dict[str, Any] = {}

# ============================================================================
# Gemini AI Service
# ============================================================================

class GeminiAIService:
    """Service for Gemini AI interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3,
            max_tokens=1000
        )
    
    def analyze_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single question and provide detailed explanation"""
        
        prompt = f"""
        As an expert educator, analyze this question and student response:

        QUESTION: {question_data['question_text']}
        OPTIONS: {json.dumps(question_data['options'], indent=2)}
        STUDENT ANSWER: {question_data['student_answer']}
        CORRECT ANSWER: {question_data['correct_answer']}
        SUBJECT: {question_data['subject']}
        DIFFICULTY: {question_data['difficulty']}
        
        Provide a comprehensive analysis in JSON format:
        {{
            "explanation": "Clear explanation of why the correct answer is right",
            "concepts_tested": ["concept1", "concept2"],
            "why_wrong": "If incorrect, explain the student's mistake",
            "improvement_tips": ["tip1", "tip2", "tip3"],
            "similar_concepts": ["related concept1", "related concept2"]
        }}
        
        Focus on educational value and helping the student understand the underlying concepts.
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                return {
                    "explanation": "The correct answer demonstrates key concepts in this subject area.",
                    "concepts_tested": [question_data['subject']],
                    "why_wrong": "Review the fundamental concepts" if not question_data['is_correct'] else None,
                    "improvement_tips": ["Practice more questions of this type", "Review related concepts"],
                    "similar_concepts": [question_data['subject']]
                }
        except Exception as e:
            logger.error(f"Error analyzing question: {e}")
            return {
                "explanation": "Analysis temporarily unavailable",
                "concepts_tested": [question_data['subject']],
                "why_wrong": None,
                "improvement_tips": ["Continue practicing"],
                "similar_concepts": []
            }
    
    async def generate_subject_analysis(self, subject_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive subject-level analysis"""
        
        prompt = f"""
        As an expert educator, analyze this student's performance in {subject_data['subject']}:

        PERFORMANCE DATA:
        - Questions Attempted: {subject_data['questions_attempted']}
        - Correct Answers: {subject_data['correct_count']}
        - Accuracy Rate: {subject_data['accuracy_rate']:.1%}
        - BKT Mastery Score: {subject_data['mastery_score']:.1%}
        - Subject: {subject_data['subject']}
        
        QUESTION BREAKDOWN:
        {json.dumps(subject_data.get('question_breakdown', {}), indent=2)}

        Provide analysis in JSON format:
        {{
            "strength_areas": ["area1", "area2"],
            "weakness_areas": ["area1", "area2"],
            "improvement_strategies": ["strategy1", "strategy2", "strategy3"],
            "recommended_topics": ["topic1", "topic2"],
            "study_time_allocation": "recommended weekly hours",
            "next_steps": ["step1", "step2", "step3"],
            "mastery_assessment": "current mastery level description"
        }}
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "strength_areas": ["Basic concepts"],
                    "weakness_areas": ["Advanced applications"],
                    "improvement_strategies": ["Regular practice", "Concept review"],
                    "recommended_topics": [subject_data['subject']],
                    "study_time_allocation": "2-3 hours per week",
                    "next_steps": ["Continue practicing", "Focus on weak areas"],
                    "mastery_assessment": f"Current mastery at {subject_data['mastery_score']:.1%}"
                }
        except Exception as e:
            logger.error(f"Error generating subject analysis: {e}")
            return {
                "strength_areas": [],
                "weakness_areas": [],
                "improvement_strategies": ["Continue regular practice"],
                "recommended_topics": [],
                "study_time_allocation": "2-3 hours per week",
                "next_steps": ["Keep practicing"],
                "mastery_assessment": "Analysis in progress"
            }
    
    async def generate_personalized_study_plan(self, complete_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized study plan based on comprehensive analysis"""
        
        prompt = f"""
        As an expert learning advisor, create a personalized study plan for this student:

        OVERALL PERFORMANCE:
        - Total Questions: {complete_data.get('total_questions', 0)}
        - Overall Accuracy: {complete_data.get('overall_accuracy', 0):.1%}
        - Time Spent: {complete_data.get('total_time', 0)} minutes
        - Subjects Covered: {complete_data.get('subjects', [])}

        SUBJECT-WISE ANALYSIS:
        {json.dumps(complete_data.get('subject_analyses', {}), indent=2)}

        BKT MASTERY DATA:
        {json.dumps(complete_data.get('bkt_data', {}), indent=2)}

        Create a comprehensive study plan in JSON format:
        {{
            "immediate_actions": ["action1", "action2"],
            "weekly_schedule": {{
                "monday": "activity",
                "tuesday": "activity",
                "wednesday": "activity",
                "thursday": "activity",
                "friday": "activity",
                "weekend": "review and practice"
            }},
            "priority_subjects": ["subject1", "subject2"],
            "skill_development_focus": ["skill1", "skill2"],
            "milestone_targets": [
                {{"week": 1, "target": "goal1"}},
                {{"week": 2, "target": "goal2"}}
            ],
            "resources_recommended": ["resource1", "resource2"],
            "practice_frequency": "recommended frequency",
            "review_schedule": "when to review concepts"
        }}
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "immediate_actions": ["Review incorrect answers", "Practice similar questions"],
                    "weekly_schedule": {
                        "daily": "30 minutes practice",
                        "weekend": "comprehensive review"
                    },
                    "priority_subjects": complete_data.get('subjects', []),
                    "skill_development_focus": ["Problem solving", "Concept understanding"],
                    "milestone_targets": [{"week": 1, "target": "Improve accuracy by 10%"}],
                    "resources_recommended": ["Practice tests", "Concept guides"],
                    "practice_frequency": "Daily practice recommended",
                    "review_schedule": "Weekly concept review"
                }
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            return {"error": "Study plan generation temporarily unavailable"}

# ============================================================================
# LangGraph Workflow for Post-Exam Analysis
# ============================================================================

class PostExamAnalysisWorkflow:
    """LangGraph workflow for comprehensive post-exam analysis"""
    
    def __init__(self):
        self.gemini_service = GeminiAIService()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AIAnalysisState)
        
        # Add nodes
        workflow.add_node("analyze_questions", self._analyze_questions)
        workflow.add_node("analyze_subject", self._analyze_subject)
        workflow.add_node("integrate_bkt", self._integrate_bkt_data)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("create_study_plan", self._create_study_plan)
        workflow.add_node("finalize_report", self._finalize_report)
        
        # Add edges
        workflow.add_edge("analyze_questions", "analyze_subject")
        workflow.add_edge("analyze_subject", "integrate_bkt")
        workflow.add_edge("integrate_bkt", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "create_study_plan")
        workflow.add_edge("create_study_plan", "finalize_report")
        workflow.add_edge("finalize_report", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_questions")
        
        return workflow.compile()
    
    async def _analyze_questions(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Analyze each question in detail"""
        logger.info("Starting question analysis...")
        
        question_analyses = []
        exam_session = state.exam_session
        
        for question_data in exam_session.get('questions', []):
            try:
                analysis = await self.gemini_service.analyze_question(question_data)
                question_analyses.append({
                    'question_id': question_data['question_id'],
                    'analysis': analysis,
                    'metadata': {
                        'subject': question_data['subject'],
                        'difficulty': question_data['difficulty'],
                        'is_correct': question_data['is_correct']
                    }
                })
            except Exception as e:
                logger.error(f"Error analyzing question {question_data.get('question_id')}: {e}")
        
        return {"question_analyses": question_analyses}
    
    async def _analyze_subject(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Analyze subject-level performance"""
        logger.info("Starting subject analysis...")
        
        exam_session = state.exam_session
        subject_data = {
            'subject': exam_session.get('subject', 'Unknown'),
            'questions_attempted': len(exam_session.get('questions', [])),
            'correct_count': sum(1 for q in exam_session.get('questions', []) if q.get('is_correct')),
            'accuracy_rate': 0,
            'mastery_score': exam_session.get('mastery_score', 0),
            'question_breakdown': {}
        }
        
        if subject_data['questions_attempted'] > 0:
            subject_data['accuracy_rate'] = subject_data['correct_count'] / subject_data['questions_attempted']
        
        analysis = await self.gemini_service.generate_subject_analysis(subject_data)
        
        return {"subject_analysis": analysis}
    
    async def _integrate_bkt_data(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Integrate BKT mastery data into analysis"""
        logger.info("Integrating BKT data...")
        
        # This would integrate with your existing BKT system
        bkt_integration = {
            'mastery_trends': state.exam_session.get('bkt_data', {}),
            'skill_progression': [],
            'learning_velocity': 'steady',
            'mastery_predictions': {}
        }
        
        return {"bkt_integration": bkt_integration}
    
    async def _generate_recommendations(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        logger.info("Generating personalized recommendations...")
        
        recommendations = []
        
        # Based on question analysis
        wrong_questions = [qa for qa in state.question_analyses if not qa['metadata']['is_correct']]
        if wrong_questions:
            recommendations.append("Focus on reviewing incorrect answers and underlying concepts")
        
        # Based on subject analysis  
        subject_analysis = state.subject_analysis
        if subject_analysis.get('weakness_areas'):
            recommendations.extend([
                f"Strengthen understanding in: {', '.join(subject_analysis['weakness_areas'][:3])}"
            ])
        
        recommendations.extend(subject_analysis.get('improvement_strategies', []))
        
        return {"personalized_recommendations": recommendations[:5]}  # Top 5
    
    async def _create_study_plan(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Create comprehensive study plan"""
        logger.info("Creating study plan...")
        
        complete_data = {
            'total_questions': len(state.exam_session.get('questions', [])),
            'overall_accuracy': state.exam_session.get('overall_score', 0),
            'total_time': state.exam_session.get('time_spent', 0),
            'subjects': [state.exam_session.get('subject', 'Unknown')],
            'subject_analyses': {state.exam_session.get('subject', 'Unknown'): state.subject_analysis},
            'bkt_data': state.bkt_integration
        }
        
        study_plan = await self.gemini_service.generate_personalized_study_plan(complete_data)
        
        return {"study_plan": [study_plan]}
    
    async def _finalize_report(self, state: AIAnalysisState) -> Dict[str, Any]:
        """Create final comprehensive report"""
        logger.info("Finalizing analysis report...")
        
        final_report = {
            'analysis_id': str(uuid.uuid4()),
            'session_id': state.exam_session.get('session_id'),
            'student_id': state.exam_session.get('student_id'),
            'subject': state.exam_session.get('subject'),
            'timestamp': timezone.now().isoformat(),
            'summary': {
                'total_questions': len(state.exam_session.get('questions', [])),
                'correct_answers': sum(1 for q in state.exam_session.get('questions', []) if q.get('is_correct')),
                'accuracy_rate': state.exam_session.get('overall_score', 0),
                'time_spent_minutes': state.exam_session.get('time_spent', 0)
            },
            'detailed_analysis': {
                'question_analyses': state.question_analyses,
                'subject_analysis': state.subject_analysis,
                'bkt_integration': state.bkt_integration
            },
            'recommendations': {
                'immediate_actions': state.personalized_recommendations,
                'study_plan': state.study_plan
            },
            'ai_generated': True,
            'model_version': 'gemini-1.5-flash'
        }
        
        return {"final_report": final_report}
    
    async def analyze_exam_session(self, exam_session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for post-exam analysis"""
        logger.info(f"Starting comprehensive analysis for session: {exam_session_data.get('session_id')}")
        
        initial_state = AIAnalysisState(exam_session=exam_session_data)
        
        try:
            # Run the workflow
            result = await asyncio.to_thread(self.workflow.invoke, initial_state.dict())
            return result.get('final_report', {})
        except Exception as e:
            logger.error(f"Error in analysis workflow: {e}")
            return {
                'error': 'Analysis temporarily unavailable',
                'session_id': exam_session_data.get('session_id'),
                'timestamp': timezone.now().isoformat()
            }

# ============================================================================
# Practice Mode AI Assistant  
# ============================================================================

class PracticeAIAssistant:
    """AI assistant for practice mode - provides hints and explanations"""
    
    def __init__(self):
        self.gemini_service = GeminiAIService()
    
    def get_hint(self, question_data: Dict[str, Any], hint_level: int = 1) -> str:
        """Provide graduated hints for practice mode"""
        
        hint_prompts = {
            1: "Provide a subtle hint about the approach without giving away the answer",
            2: "Provide a more specific hint about the method or concept to use",
            3: "Provide a detailed hint that guides toward the solution step-by-step"
        }
        
        prompt = f"""
        QUESTION: {question_data['question_text']}
        OPTIONS: {json.dumps(question_data['options'], indent=2)}
        SUBJECT: {question_data['subject']}
        DIFFICULTY: {question_data['difficulty']}
        
        {hint_prompts.get(hint_level, hint_prompts[1])}
        
        Provide educational guidance without directly stating the answer.
        Keep the response concise and encouraging.
        """
        
        try:
            # Use sync_to_async to safely call the LLM from async context
            def _get_gemini_response():
                return self.gemini_service.llm.invoke(prompt)
            
            response = _get_gemini_response()
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return "Try reading the question carefully and consider the key concepts involved."
    
    def provide_explanation(self, question_data: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
        """Provide detailed explanation after student answers in practice mode"""
        
        is_correct = student_answer.lower() == question_data['correct_answer'].lower()
        
        prompt = f"""
        QUESTION: {question_data['question_text']}
        OPTIONS: {json.dumps(question_data['options'], indent=2)}
        STUDENT ANSWER: {student_answer}
        CORRECT ANSWER: {question_data['correct_answer']}
        RESULT: {"Correct" if is_correct else "Incorrect"}
        
        Provide a comprehensive explanation in JSON format:
        {{
            "feedback": "Encouraging feedback based on correctness",
            "detailed_explanation": "Complete explanation of the correct solution",
            "key_concepts": ["concept1", "concept2"],
            "common_mistakes": ["mistake1", "mistake2"],
            "practice_suggestions": ["suggestion1", "suggestion2"]
        }}
        
        Be encouraging and educational regardless of correctness.
        """
        
        try:
            # Use sync function call to safely call the LLM from async context
            def _get_gemini_response():
                return self.gemini_service.llm.invoke(prompt)
            
            response = _get_gemini_response()
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "feedback": "Great attempt!" if is_correct else "Good try! Let's learn from this.",
                    "detailed_explanation": "The correct approach involves understanding the key concepts.",
                    "key_concepts": [question_data['subject']],
                    "common_mistakes": ["Rushing through the question"],
                    "practice_suggestions": ["Practice similar questions", "Review related concepts"]
                }
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {
                "feedback": "Keep practicing!",
                "detailed_explanation": "Explanation temporarily unavailable",
                "key_concepts": [],
                "common_mistakes": [],
                "practice_suggestions": ["Continue practicing"]
            }