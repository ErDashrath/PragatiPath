from ninja import Router
from ninja import Schema
from typing import List, Optional
from datetime import datetime

router = Router()

# Pydantic schemas for request/response validation
class StudentSchema(Schema):
    id: Optional[int] = None
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
@router.get("/students", response=List[StudentSchema])
def list_students(request):
    """Get all students"""
    # TODO: Implement actual database query
    return [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "created_at": datetime.now()
        }
    ]

@router.get("/students/{student_id}", response=StudentSchema)
def get_student(request, student_id: int):
    """Get a specific student by ID"""
    # TODO: Implement actual database query
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