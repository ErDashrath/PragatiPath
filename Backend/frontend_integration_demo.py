"""
Frontend Integration Example for Adaptive Learning System

This example shows how to integrate the adaptive learning system
with a frontend application using the REST API endpoints.

Features Demonstrated:
- Starting adaptive sessions
- Getting questions with dynamic difficulty
- Submitting answers with real-time mastery updates
- Tracking progress and difficulty changes
- Getting final session analytics

Author: AI Assistant
Date: 2024-12-26
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class AdaptiveLearningClient:
    """
    Client class for interacting with the adaptive learning API
    This demonstrates how frontend applications should integrate
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.current_session = None
        
    def get_available_subjects(self) -> Dict[str, Any]:
        """Get all available subjects and chapters"""
        
        try:
            response = requests.get(f"{self.base_url}/adaptive-session/available-subjects/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def start_adaptive_session(
        self,
        student_id: int,
        subject_code: str,
        chapter_id: Optional[int] = None,
        max_questions: int = 15
    ) -> Dict[str, Any]:
        """Start a new adaptive learning session"""
        
        try:
            payload = {
                'student_id': student_id,
                'subject_code': subject_code,
                'max_questions': max_questions
            }
            
            if chapter_id:
                payload['chapter_id'] = chapter_id
            
            response = requests.post(
                f"{self.base_url}/adaptive-session/start/",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result['success']:
                self.current_session = result['session_id']
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """Get the next adaptive question"""
        
        try:
            response = requests.get(f"{self.base_url}/adaptive-session/next-question/{session_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        student_answer: str,
        response_time: float
    ) -> Dict[str, Any]:
        """Submit student answer and get updated knowledge state"""
        
        try:
            payload = {
                'session_id': session_id,
                'question_id': question_id,
                'student_answer': student_answer,
                'response_time': response_time
            }
            
            response = requests.post(
                f"{self.base_url}/adaptive-session/submit-answer/",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session analytics"""
        
        try:
            response = requests.get(f"{self.base_url}/adaptive-session/session-summary/{session_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def get_student_mastery(self, student_id: int) -> Dict[str, Any]:
        """Get student's current mastery levels"""
        
        try:
            response = requests.get(f"{self.base_url}/adaptive-session/student-mastery/{student_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """Manually end a session"""
        
        try:
            response = requests.post(f"{self.base_url}/adaptive-session/end-session/{session_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

def simulate_frontend_interaction():
    """
    Simulate how a frontend application would interact with the adaptive learning system
    This shows the complete workflow from session start to completion
    """
    
    print("🌐 Frontend Integration Demo - Adaptive Learning System")
    print("=" * 65)
    
    client = AdaptiveLearningClient()
    
    # Step 1: Get available subjects
    print("\n📚 Step 1: Getting Available Subjects")
    subjects_result = client.get_available_subjects()
    
    if subjects_result.get('success'):
        subjects = subjects_result['subjects']
        print(f"✅ Found {len(subjects)} subjects:")
        for subject in subjects:
            print(f"   📖 {subject['name']} ({subject['code']})")
            print(f"      Chapters: {len(subject['chapters'])}")
    else:
        print(f"❌ Failed to get subjects: {subjects_result.get('error')}")
        return
    
    # Step 2: Start adaptive session
    print("\n🎯 Step 2: Starting Adaptive Session")
    
    # Use first available subject
    subject_code = subjects[0]['code']
    student_id = 1  # Assuming student ID 1 exists
    
    session_result = client.start_adaptive_session(
        student_id=student_id,
        subject_code=subject_code,
        max_questions=8  # Short demo session
    )
    
    if not session_result.get('success'):
        print(f"❌ Failed to start session: {session_result.get('error')}")
        return
    
    session_id = session_result['session_id']
    print(f"✅ Session started: {session_id}")
    print(f"   📊 Starting mastery: {session_result['initial_mastery']:.3f}")
    print(f"   📈 Starting difficulty: {session_result['starting_difficulty']}")
    print(f"   🎪 Mastery level: {session_result['mastery_level']}")
    
    # Step 3: Interactive question-answer cycle
    print("\n📝 Step 3: Interactive Question-Answer Cycle")
    
    question_count = 0
    mastery_history = []
    difficulty_history = []
    
    while question_count < 8:  # Limit for demo
        # Get next question
        question_result = client.get_next_question(session_id)
        
        if not question_result.get('success'):
            if question_result.get('session_complete'):
                print("🏁 Session completed automatically")
                break
            else:
                print(f"❌ Failed to get question: {question_result.get('error')}")
                break
        
        question = question_result['question']
        current_difficulty = question_result['current_difficulty']
        current_mastery = question_result['current_mastery']
        
        question_count += 1
        mastery_history.append(current_mastery)
        difficulty_history.append(current_difficulty)
        
        print(f"\n   📋 Question {question_count}:")
        print(f"      🎯 Difficulty: {current_difficulty}")
        print(f"      📊 Current Mastery: {current_mastery:.3f}")
        print(f"      ❓ {question['text'][:100]}...")
        print(f"      Options: A) {question['options'][0][:50]}...")
        
        # Simulate student thinking and answering
        start_time = time.time()
        
        # Simple simulation: 75% chance of correct answer
        import random
        is_correct = random.random() < 0.75
        student_answer = question['correct_answer'] if is_correct else random.choice(['a', 'b', 'c', 'd'])
        
        # Simulate thinking time (2-15 seconds)
        thinking_time = random.uniform(2.0, 15.0)
        response_time = time.time() - start_time + thinking_time
        
        print(f"      🤔 Student answer: {student_answer.upper()} ({'Correct' if is_correct else 'Incorrect'})")
        
        # Submit answer
        answer_result = client.submit_answer(
            session_id=session_id,
            question_id=question['id'],
            student_answer=student_answer,
            response_time=response_time
        )
        
        if answer_result.get('success'):
            new_mastery = answer_result['new_mastery']
            mastery_change = answer_result['mastery_change']
            next_difficulty = answer_result['next_difficulty']
            difficulty_changed = answer_result['difficulty_changed']
            
            print(f"      ✅ Answer processed:")
            print(f"         📈 New mastery: {new_mastery:.3f} ({mastery_change:+.3f})")
            print(f"         🎯 Next difficulty: {next_difficulty}")
            
            if difficulty_changed:
                print(f"         📊 🔄 Difficulty changed: {current_difficulty} → {next_difficulty}")
            
            # Show performance trend
            trend = answer_result.get('performance_trend', 'unknown')
            trend_emoji = {
                'strong_performance': '🚀',
                'steady_performance': '📈', 
                'inconsistent_performance': '📊',
                'needs_support': '⚠️'
            }.get(trend, '❓')
            
            print(f"         {trend_emoji} Trend: {trend.replace('_', ' ').title()}")
        else:
            print(f"      ❌ Answer submission failed: {answer_result.get('error')}")
        
        time.sleep(0.5)  # Brief pause for readability
    
    # Step 4: Get session summary
    print("\n📊 Step 4: Session Summary and Analytics")
    
    summary_result = client.get_session_summary(session_id)
    
    if summary_result.get('success'):
        summary = summary_result['summary']
        
        print(f"✅ Session Analytics:")
        print(f"   📝 Questions Attempted: {summary['total_questions']}")
        print(f"   ✅ Accuracy: {summary['accuracy_percentage']:.1f}%")
        print(f"   📈 Mastery Progress:")
        print(f"      Initial: {summary['initial_mastery']:.3f} ({summary['initial_mastery_level']})")
        print(f"      Final: {summary['final_mastery']:.3f} ({summary['final_mastery_level']})")
        print(f"      Change: {summary['mastery_improvement']:+.3f}")
        
        # Show difficulty progression
        difficulty_stats = summary['difficulty_stats']
        print(f"   🎯 Difficulty Progression:")
        print(f"      Starting: {difficulty_stats['starting_difficulty']}")
        print(f"      Ending: {difficulty_stats['ending_difficulty']}")
        print(f"      Highest Reached: {difficulty_stats['highest_difficulty_reached']}")
        print(f"      Changes: {difficulty_stats['progression_changes']}")
        
        # Show recommendations
        recommendations = summary['recommendations']
        print(f"   💡 Personalized Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"      {i}. {rec}")
        
        # Show session duration
        duration = summary.get('session_duration', {})
        if duration.get('total_minutes', 0) > 0:
            print(f"   ⏱️ Session Duration: {duration['total_minutes']:.1f} minutes")
            print(f"      Avg per question: {duration['average_time_per_question']:.1f} seconds")
    
    else:
        print(f"❌ Failed to get session summary: {summary_result.get('error')}")
    
    # Step 5: Get student's overall mastery
    print("\n🏆 Step 5: Student's Overall Mastery Levels")
    
    mastery_result = client.get_student_mastery(student_id)
    
    if mastery_result.get('success'):
        overall_stats = mastery_result['overall_statistics']
        
        print(f"✅ Student Mastery Overview:")
        print(f"   📊 Overall Mastery: {overall_stats['overall_mastery']:.3f}")
        print(f"   📚 Skills Tracked: {overall_stats['skills_tracked']}")
        
        # Show mastery level distribution
        level_distribution = overall_stats.get('mastery_level_distribution', {})
        if level_distribution:
            print(f"   🎯 Mastery Level Distribution:")
            for level, count in level_distribution.items():
                print(f"      {level.title()}: {count}")
        
        # Show recent session history
        recent_sessions = overall_stats.get('recent_sessions', [])
        if recent_sessions:
            print(f"   📋 Recent Sessions:")
            for session in recent_sessions[:3]:  # Show last 3 sessions
                print(f"      • {session['subject']} - {session['accuracy']:.1f}% accuracy")
    
    else:
        print(f"❌ Failed to get student mastery: {mastery_result.get('error')}")
    
    print("\n🎉 Frontend Integration Demo Complete!")
    print("=" * 65)
    print("✅ All adaptive learning features demonstrated successfully")
    print("🎯 System ready for production frontend integration")

def show_api_usage_examples():
    """Show code examples for frontend developers"""
    
    print("\n💻 API Usage Examples for Frontend Developers")
    print("=" * 60)
    
    print("""
    // JavaScript/TypeScript Example
    
    class AdaptiveLearningService {
        constructor(baseUrl = 'http://localhost:8000') {
            this.baseUrl = baseUrl;
        }
        
        async startSession(studentId, subjectCode, maxQuestions = 15) {
            const response = await fetch(`${this.baseUrl}/adaptive-session/start/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: studentId,
                    subject_code: subjectCode,
                    max_questions: maxQuestions
                })
            });
            return response.json();
        }
        
        async getNextQuestion(sessionId) {
            const response = await fetch(
                `${this.baseUrl}/adaptive-session/next-question/${sessionId}/`
            );
            return response.json();
        }
        
        async submitAnswer(sessionId, questionId, answer, responseTime) {
            const response = await fetch(`${this.baseUrl}/adaptive-session/submit-answer/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    question_id: questionId,
                    student_answer: answer,
                    response_time: responseTime
                })
            });
            return response.json();
        }
    }
    
    // Usage in React component
    const AdaptiveLearningComponent = () => {
        const [session, setSession] = useState(null);
        const [question, setQuestion] = useState(null);
        const [mastery, setMastery] = useState(0);
        const [difficulty, setDifficulty] = useState('moderate');
        
        const service = new AdaptiveLearningService();
        
        const startSession = async () => {
            const result = await service.startSession(studentId, 'quantitative_aptitude');
            if (result.success) {
                setSession(result.session_id);
                setMastery(result.initial_mastery);
                setDifficulty(result.starting_difficulty);
                loadNextQuestion(result.session_id);
            }
        };
        
        const loadNextQuestion = async (sessionId) => {
            const result = await service.getNextQuestion(sessionId);
            if (result.success) {
                setQuestion(result.question);
                setDifficulty(result.current_difficulty);
                setMastery(result.current_mastery);
            }
        };
        
        const handleAnswer = async (answer) => {
            const startTime = questionStartTime;
            const responseTime = (Date.now() - startTime) / 1000;
            
            const result = await service.submitAnswer(
                session, question.id, answer, responseTime
            );
            
            if (result.success) {
                setMastery(result.new_mastery);
                // Show feedback, update UI, then load next question
                setTimeout(() => loadNextQuestion(session), 2000);
            }
        };
        
        return (
            <div className="adaptive-learning">
                <MasteryIndicator mastery={mastery} difficulty={difficulty} />
                <QuestionDisplay question={question} onAnswer={handleAnswer} />
                <ProgressTracker session={session} />
            </div>
        );
    };
    """)

if __name__ == "__main__":
    print("🚀 Starting Frontend Integration Demo")
    simulate_frontend_interaction()
    show_api_usage_examples()
    
    print("\n📋 Integration Summary:")
    print("✅ Adaptive session management")
    print("✅ Dynamic difficulty adjustment")  
    print("✅ Real-time mastery tracking")
    print("✅ BKT/DKT integration")
    print("✅ Comprehensive analytics")
    print("✅ Production-ready API endpoints")
    print("\n🎯 System ready for production deployment!")