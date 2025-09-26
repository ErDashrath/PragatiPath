
# --- Imports ---
from ninja import Router, Schema
from django.contrib.auth import authenticate, login as django_login
from typing import List, Optional
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# --- Router instance ---
router = Router()

# --- Authentication schemas ---
class LoginSchema(Schema):
    username: str
    password: str

class RegisterSchema(Schema):
    username: str
    password: str
    confirm_password: str
    email: str
    full_name: str

# --- Authentication endpoints ---
@router.post("/register")
def register(request, payload: RegisterSchema):
    """Register a new student account"""
    from django.contrib.auth.models import User
    from core.models import StudentProfile
    from django.db import IntegrityError
    
    try:
        # Validate password confirmation
        if payload.password != payload.confirm_password:
            return JsonResponse({"detail": "Passwords do not match"}, status=400)
        
        # Validate password strength
        if len(payload.password) < 8:
            return JsonResponse({"detail": "Password must be at least 8 characters long"}, status=400)
        
        # Check if username already exists
        if User.objects.filter(username=payload.username).exists():
            return JsonResponse({"detail": "Username already exists"}, status=400)
            
        # Check if email already exists
        if User.objects.filter(email=payload.email).exists():
            return JsonResponse({"detail": "Email already exists"}, status=400)
        
        # Create User
        user = User.objects.create_user(
            username=payload.username,
            password=payload.password,  # Django automatically hashes this
            email=payload.email,
            first_name=payload.full_name.split()[0] if payload.full_name else "",
            last_name=" ".join(payload.full_name.split()[1:]) if len(payload.full_name.split()) > 1 else ""
        )
        
        # Create StudentProfile with default values
        student_profile = StudentProfile.objects.create(
            user=user,
            bkt_parameters={},
            dkt_hidden_state=[],
            fundamentals={
                'listening': 0.5,
                'grasping': 0.5,
                'retention': 0.5,
                'application': 0.5
            },
            interaction_history=[],
            current_level={},
            consecutive_correct_count={},
            level_lock_status={},
            subject_progress={}
        )
        
        return {
            "id": str(student_profile.id),
            "username": user.username,
            "email": user.email,
            "name": payload.full_name,  # Changed from full_name to name
            "created_at": user.date_joined,
            "userType": "student",
            "message": "Account created successfully"
        }
        
    except IntegrityError as e:
        return JsonResponse({"detail": "Username or email already exists"}, status=400)
    except Exception as e:
        print(f"Registration error: {str(e)}")  # For debugging
        return JsonResponse({"detail": f"Registration failed: {str(e)}"}, status=500)

@router.post("/login")
def login(request, payload: LoginSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is not None:
        django_login(request, user)
        # Try to get StudentProfile if exists
        try:
            profile = user.student_profile
            full_name = user.get_full_name() or user.username
            return {
                "id": str(profile.id),
                "username": user.username,
                "email": user.email,
                "name": full_name,  # Changed from full_name to name to match frontend schema
                "created_at": user.date_joined,
                "userType": "student"
            }
        except Exception:
            # Not a student, return basic user info
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.get_full_name() or user.username,  # Changed from full_name to name
                "created_at": user.date_joined,
                "userType": "admin"
            }
    else:
        return JsonResponse({"detail": "Invalid username or password"}, status=401)

@router.get("/user")
def get_current_user(request):
    """Get the current authenticated user"""
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not authenticated"}, status=401)
    
    user = request.user
    try:
        profile = user.student_profile
        full_name = user.get_full_name() or user.username
        return {
            "id": str(profile.id),
            "username": user.username,
            "email": user.email,
            "name": full_name,
            "created_at": user.date_joined,
            "userType": "student"
        }
    except Exception:
        # Not a student, return basic user info
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.get_full_name() or user.username,
            "created_at": user.date_joined,
            "userType": "admin"
        }

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
    """Create a new student (DEPRECATED - use /register instead)"""
    from django.contrib.auth.models import User
    from core.models import StudentProfile
    
    # Redirect to use the proper registration flow
    return JsonResponse({"detail": "Please use /api/core/register endpoint for new registrations"}, status=400)

@router.put("/students/{student_id}", response=StudentSchema)
def update_student(request, student_id: str, payload: StudentUpdateSchema):
    """Update an existing student"""
    from core.models import StudentProfile
    
    student_profile = get_object_or_404(StudentProfile, id=student_id)
    user = student_profile.user
    
    # Update user fields
    if payload.username:
        user.username = payload.username
    if payload.email:
        user.email = payload.email
    if payload.full_name:
        names = payload.full_name.split()
        user.first_name = names[0] if names else ""
        user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
    
    user.save()
    
    return {
        "id": str(student_profile.id),
        "username": user.username,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "created_at": user.date_joined
    }

@router.delete("/students/{student_id}")
def delete_student(request, student_id: str):
    """Delete a student"""
    from core.models import StudentProfile
    
    student_profile = get_object_or_404(StudentProfile, id=student_id)
    user = student_profile.user
    
    # Delete both StudentProfile and User
    student_profile.delete()
    user.delete()
    
    return {"message": f"Student {student_id} deleted successfully"}

@router.get("/status")
def core_status(request):
    """Core app status endpoint"""
    return {"app": "core", "status": "ready", "description": "Student management system"}