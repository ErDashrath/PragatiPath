import requests
import json

# Test registration endpoint
r = requests.post('http://localhost:8000/api/core/register', 
    json={
        'username': 'quicktest123', 
        'password': 'password123', 
        'confirm_password': 'password123', 
        'email': 'quicktest123@example.com', 
        'full_name': 'Quick Test User'
    }
)

print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("content-type")}')
print(f'Response: {r.text[:500]}')

if r.status_code != 200:
    print("ERROR DETECTED - Full response:")
    print(r.text)