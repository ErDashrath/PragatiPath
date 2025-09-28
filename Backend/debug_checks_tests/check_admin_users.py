#!/usr/bin/env python3
"""
Check admin users in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')
django.setup()

from django.contrib.auth.models import User

def check_admin_users():
    print('=== ALL USERS ===')
    for user in User.objects.all():
        user_type = "admin" if user.is_superuser or user.is_staff else "student"
        print(f'Username: {user.username} | Name: {user.first_name or "N/A"} | Type: {user_type} | Staff: {user.is_staff} | Superuser: {user.is_superuser}')
    
    print('\n=== ADMIN USERS ===')
    admin_users = User.objects.filter(is_staff=True)
    if admin_users.exists():
        for user in admin_users:
            print(f'Admin: {user.username} | Name: {user.first_name or "N/A"} | Superuser: {user.is_superuser}')
    else:
        print('No admin users found!')
        
    print('\n=== CREATE TEST ADMIN ===')
    # Create a test admin user if none exists
    if not admin_users.exists():
        try:
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                first_name='Admin User',
                is_staff=True,
                is_superuser=True
            )
            print(f'Created admin user: {admin_user.username}')
        except Exception as e:
            print(f'Error creating admin user: {e}')

if __name__ == "__main__":
    check_admin_users()