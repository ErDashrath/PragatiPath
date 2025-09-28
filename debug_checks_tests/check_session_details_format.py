import requests
import json

response = requests.get("http://localhost:8000/history/session-details/dc684f75-c850-4495-b17d-7f12c4b4b31f/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("✅ Session details response:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Error: {response.text[:500]}")