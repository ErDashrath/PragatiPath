#!/usr/bin/env python3
"""
Direct UUID test to understand the issue
"""

import uuid
import re

def test_uuid_conversion():
    # This is the problematic string from the error
    problem_string = "real_00a3ccb2-3391-4ebc-8c79-a0e17d72da60"
    
    print(f"Original string: '{problem_string}'")
    print(f"String length: {len(problem_string)}")
    print(f"String bytes: {problem_string.encode('utf-8')}")
    
    # Extract the UUID part
    uuid_part = problem_string.replace("real_", "")
    print(f"UUID part: '{uuid_part}'")
    print(f"UUID part length: {len(uuid_part)}")
    print(f"UUID part bytes: {uuid_part.encode('utf-8')}")
    
    # Clean the string
    cleaned = re.sub(r'[^\w\-]', '', uuid_part.strip())
    print(f"Cleaned: '{cleaned}'")
    print(f"Cleaned length: {len(cleaned)}")
    
    # Test UUID conversion
    try:
        test_uuid = uuid.UUID(cleaned)
        print(f"✅ UUID created successfully: {test_uuid}")
        return True
    except Exception as e:
        print(f"❌ UUID creation failed: {e}")
        return False

def test_direct_question_lookup():
    """Test direct database lookup"""
    import os
    import sys
    import django

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
    django.setup()
    
    from assessment.models import AdaptiveQuestion
    
    # Test with the specific UUID
    test_uuid = "00a3ccb2-3391-4ebc-8c79-a0e17d72da60"
    print(f"\n🔍 Testing database lookup for UUID: {test_uuid}")
    
    try:
        question = AdaptiveQuestion.objects.get(id=test_uuid)
        print(f"✅ Question found: {question.id}")
        print(f"   Subject: {question.subject_fk}")
        print(f"   Answer: {question.answer}")
        print(f"   Difficulty: {question.difficulty_level}")
        return True
    except AdaptiveQuestion.DoesNotExist:
        print(f"❌ Question not found in database")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing UUID Conversion Issue")
    print("=" * 40)
    
    uuid_ok = test_uuid_conversion()
    if uuid_ok:
        db_ok = test_direct_question_lookup()
        if db_ok:
            print("\n🎉 Both UUID conversion and DB lookup work!")
            print("The issue must be in the Django API code.")
        else:
            print("\n❌ UUID works but question not in database")
    else:
        print("\n❌ UUID conversion itself is failing")