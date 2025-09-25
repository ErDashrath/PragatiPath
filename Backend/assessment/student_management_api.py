"""
Student Management API - Create and manage students for testing
"""
from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List, Optional
from django.contrib.auth.models import User
from django.db import transaction
from core.models import StudentProfile
import uuid
import logging

logger = logging.getLogger(__name__)
student_router = Router()

class CreateStudentSchema(Schema):
    username: str
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class StudentResponseSchema(Schema):
    student_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    created_at: str
    last_activity: str

@student_router.post("/create", response=StudentResponseSchema, tags=["Student Management"])
def create_student(request, payload: CreateStudentSchema):
    """
    Create a new student for testing purposes
    """
    try:
        with transaction.atomic():
            # Check if username already exists
            if User.objects.filter(username=payload.username).exists():
                raise HttpError(400, f"Student with username '{payload.username}' already exists")
            
            # Create user
            user = User.objects.create_user(
                username=payload.username,
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                password="student123"  # Default password for testing
            )
            
            # Create student profile
            student_profile = StudentProfile.objects.create(user=user)
            
            logger.info(f"Created student: {payload.username} with ID: {student_profile.id}")
            
            return StudentResponseSchema(
                student_id=str(student_profile.id),
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=student_profile.created_at.isoformat(),
                last_activity=student_profile.last_activity.isoformat()
            )
            
    except Exception as e:
        logger.error(f"Error creating student: {str(e)}")
        raise HttpError(500, f"Error creating student: {str(e)}")

@student_router.get("/list", response=List[StudentResponseSchema], tags=["Student Management"])
def list_students(request):
    """
    List all students
    """
    try:
        students = StudentProfile.objects.select_related('user').all()
        
        return [
            StudentResponseSchema(
                student_id=str(student.id),
                username=student.user.username,
                email=student.user.email,
                first_name=student.user.first_name,
                last_name=student.user.last_name,
                created_at=student.created_at.isoformat(),
                last_activity=student.last_activity.isoformat()
            )
            for student in students
        ]
        
    except Exception as e:
        logger.error(f"Error listing students: {str(e)}")
        raise HttpError(500, f"Error listing students: {str(e)}")

@student_router.get("/{student_id}", response=StudentResponseSchema, tags=["Student Management"])
def get_student(request, student_id: str):
    """
    Get a specific student by ID
    """
    try:
        student = StudentProfile.objects.select_related('user').get(id=student_id)
        
        return StudentResponseSchema(
            student_id=str(student.id),
            username=student.user.username,
            email=student.user.email,
            first_name=student.user.first_name,
            last_name=student.user.last_name,
            created_at=student.created_at.isoformat(),
            last_activity=student.last_activity.isoformat()
        )
        
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error getting student {student_id}: {str(e)}")
        raise HttpError(500, f"Error getting student: {str(e)}")

@student_router.delete("/{student_id}", tags=["Student Management"])
def delete_student(request, student_id: str):
    """
    Delete a student (for testing cleanup)
    """
    try:
        with transaction.atomic():
            student = StudentProfile.objects.get(id=student_id)
            username = student.user.username
            
            # Delete user (will cascade to student profile)
            student.user.delete()
            
            logger.info(f"Deleted student: {username} with ID: {student_id}")
            
            return {"success": True, "message": f"Student {username} deleted successfully"}
            
    except StudentProfile.DoesNotExist:
        raise HttpError(404, f"Student with ID {student_id} not found")
    except Exception as e:
        logger.error(f"Error deleting student {student_id}: {str(e)}")
        raise HttpError(500, f"Error deleting student: {str(e)}")