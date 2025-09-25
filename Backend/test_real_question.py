#!/usr/bin/env python3
"""
Test with the actual question from database - we found one!
"""

import requests
import json

def test_with_real_question():
    url = "http://localhost:8000/simple/submit-answer/"
    
    # We found this question exists in the database:
    # ID: 74d59a91-9c73-4cca-87e2-c5ad40e72a69
    # Subject: quantitative_aptitude  
    # Answer: d
    
    data = {
        "session_id": "81225db3-6d4d-489c-980d-b4aa7d93b3f6",
        "question_id": "74d59a91-9c73-4cca-87e2-c5ad40e72a69",
        "selected_answer": "d",  # Correct answer
        "time_spent": 25.5
    }
    
    print("=" * 60)
    print(f"🧪 Testing with REAL question from database")
    print(f"Session: {data['session_id']}")
    print(f"Question: {data['question_id']}")
    print(f"Subject: quantitative_aptitude")
    print(f"Answer: {data['selected_answer']} (should be correct)")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if our AdaptiveSubmission analytics worked
            if result.get('analytics_saved'):
                print("\n🎯 Analytics Integration:")
                print(f"   Submission saved to database: ✅")
            else:
                print("\n⚠️ Analytics Integration:")
                print(f"   Submission may not be saved to analytics table")
                
        else:
            print("❌ FAILED!")
            print(f"Response: {response.text}")
            try:
                error_details = response.json()
                print(f"Error details: {json.dumps(error_details, indent=2)}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_real_question()