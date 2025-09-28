import requests

response = requests.get("http://localhost:8000/history/session-details/dc684f75-c850-4495-b17d-7f12c4b4b31f/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Existing session details endpoint works!")
    data = response.json()
    print(f"Response keys: {list(data.keys())}")
else:
    print(f"❌ Response: {response.text[:200]}")