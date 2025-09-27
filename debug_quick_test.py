#!/usr/bin/env python3
"""
Quick debug test - just 3 questions to trace BKT updates
"""

import requests
import json

BASE_URL = "http://localhost:8000/simple"
TEST_STUDENT = {
    "student_name": "Debug_Test_Student",
    "subject": "quantitative_aptitude", 
    "question_count": 3
}

def main():
    print("🔍 QUICK DEBUG TEST - 3 Questions Only")
    
    # Start session
    response = requests.post(f"{BASE_URL}/start-session/", json=TEST_STUDENT)
    session_data = response.json()
    session_id = session_data['session_id']
    print(f"✅ Session: {session_id}")
    
    for i in range(1, 4):
        print(f"\n--- Question {i} ---")
        
        # Get question
        response = requests.get(f"{BASE_URL}/get-question/{session_id}/")
        question = response.json()
        print(f"Difficulty: {question['difficulty']}")
        print(f"BKT: {question['adaptive_info']['bkt_mastery']}")
        
        # Submit WRONG answer
        wrong_answer = 'A' if question['correct_answer'] != 'A' else 'B'
        submit_data = {
            "session_id": session_id,
            "question_id": question['question_id'],
            "selected_answer": wrong_answer,
            "time_spent": 5.0
        }
        
        response = requests.post(f"{BASE_URL}/submit-answer/", json=submit_data)
        answer_data = response.json()
        print(f"Result: {'CORRECT' if answer_data['answer_correct'] else 'WRONG'}")
        print(f"New Mastery: {answer_data['knowledge_update'].get('new_mastery_level', 'N/A')}")

if __name__ == "__main__":
    main()