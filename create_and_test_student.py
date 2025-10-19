#!/usr/bin/env python3
"""
Register a new test student, log in, and fetch available exams to validate backend+auth.
"""
import requests
import time

BASE = "http://localhost:8000"

def main():
    session = requests.Session()
    username = f"auto_student_{int(time.time())}"
    password = "TestPass123!"
    register_url = f"{BASE}/api/core/register"
    login_url = f"{BASE}/api/core/login"
    exams_url = f"{BASE}/api/enhanced-exam/student/exams/available"

    payload = {
        "username": username,
        "password": password,
        "confirm_password": password,
        "email": f"{username}@example.com",
        "full_name": "Auto Test Student",
        "user_type": "student"
    }

    print("Registering:", payload)
    try:
        r = session.post(register_url, json=payload, timeout=10)
    except Exception as e:
        print("Register request failed:", e)
        return

    print("Register status:", r.status_code, r.text)
    if r.status_code not in (200, 201):
        print("Registration did not succeed; aborting further tests.")
        return

    # Login
    login_payload = {"username": username, "password": password}
    try:
        r = session.post(login_url, json=login_payload, timeout=10)
    except Exception as e:
        print("Login request failed:", e)
        return

    print("Login status:", r.status_code, r.text)
    if r.status_code != 200:
        print("Login failed; aborting.")
        return

    # Fetch exams
    try:
        r = session.get(exams_url, timeout=10)
    except Exception as e:
        print("Exams request failed:", e)
        return

    print("Exams status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

if __name__ == '__main__':
    main()
