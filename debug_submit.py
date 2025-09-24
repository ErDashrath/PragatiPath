"""
Debug script to test specific API call
"""
import requests
import json

def debug_submit_answer():
    student_id = "48703c5a-1840-4607-99fc-a3d98bc94753"
    
    # Start an assessment first
    print("Starting assessment...")
    start_payload = {
        "student_id": student_id,
        "subject": "quantitative_aptitude",
        "preferred_difficulty": "very_easy"
    }
    
    response = requests.post(
        "http://localhost:8000/api/assessment/v1/assessment/start-subject",
        json=start_payload
    )
    print(f"Start response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        assessment_id = data['assessment_id']
        question_id = data['next_question']['id']
        
        # Now submit answer
        print("Submitting answer...")
        answer_payload = {
            "student_id": student_id,
            "assessment_id": assessment_id,
            "question_id": question_id,
            "answer": "A",
            "response_time": 30.5,
            "subject": "quantitative_aptitude",
            "current_difficulty": "very_easy"
        }
        
        print(f"Payload: {json.dumps(answer_payload, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/api/assessment/v1/assessment/submit-answer",
            json=answer_payload
        )
        print(f"Submit response: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    debug_submit_answer()