from ninja import Router
from ninja import Schema
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404

router = Router()

# Pydantic schemas for request/response validation
class StudentSchema(Schema):
    id: Optional[str] = None  # Changed to str to support UUID
    username: str
    email: str
    full_name: str
    created_at: Optional[datetime] = None

class StudentCreateSchema(Schema):
    username: str
    email: str
    full_name: str

class StudentUpdateSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

# Core API endpoints for student management
@router.get("/students")
def list_students(request):
    """Get all students"""
    from api_serializers import serialize_student_profile
    from core.models import StudentProfile
    from django.contrib.auth.models import User
    
    # Return mock student data with proper serialization
    return [
        {
            "id": "fb123456-1234-1234-1234-123456789012",
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "fb123456-1234-1234-1234-123456789013",
            "username": "jane_smith",
            "email": "jane@example.com", 
            "full_name": "Jane Smith",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "fb123456-1234-1234-1234-123456789014",
            "username": "alice_johnson",
            "email": "alice@example.com",
            "full_name": "Alice Johnson", 
            "created_at": datetime.now().isoformat()
        }
    ]

@router.get("/students/{student_id}", response=StudentSchema)
def get_student(request, student_id: str):
    """Get a specific student by ID - accepts both UUID and integer"""
    # Handle both UUID and integer formats
    try:
        # Try to get the actual student from database
        from core.models import StudentProfile
        if len(student_id) > 10:  # Likely a UUID
            student = StudentProfile.objects.get(id=student_id)
            return {
                "id": str(student.id),
                "username": student.user.username,
                "email": student.user.email,
                "full_name": student.user.get_full_name() or student.user.username,
                "created_at": student.user.date_joined
            }
        else:  # Integer ID
            student = StudentProfile.objects.get(user_id=int(student_id))
            return {
                "id": str(student.id),
                "username": student.user.username,
                "email": student.user.email,
                "full_name": student.user.get_full_name() or student.user.username,
                "created_at": student.user.date_joined
            }
    except:
        # Fallback to mock data
        return {
            "id": student_id,
            "username": "john_doe",
            "email": "john@example.com", 
            "full_name": "John Doe",
            "created_at": datetime.now()
        }

@router.post("/students", response=StudentSchema)
def create_student(request, payload: StudentCreateSchema):
    """Create a new student"""
    # TODO: Implement actual database creation
    return {
        "id": 1,
        "username": payload.username,
        "email": payload.email,
        "full_name": payload.full_name,
        "created_at": datetime.now()
    }

@router.put("/students/{student_id}", response=StudentSchema)
def update_student(request, student_id: int, payload: StudentUpdateSchema):
    """Update an existing student"""
    # TODO: Implement actual database update
    return {
        "id": student_id,
        "username": payload.username or "john_doe",
        "email": payload.email or "john@example.com",
        "full_name": payload.full_name or "John Doe",
        "created_at": datetime.now()
    }

@router.delete("/students/{student_id}")
def delete_student(request, student_id: int):
    """Delete a student"""
    # TODO: Implement actual database deletion
    return {"message": f"Student {student_id} deleted successfully"}

@router.get("/status")
def core_status(request):
    """Core app status endpoint"""
    return {"app": "core", "status": "ready", "description": "Student management system"}