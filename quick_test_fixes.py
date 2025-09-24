import requests
import time

print('🧪 Quick UUID Fix Verification Test')
print('=' * 50)

time.sleep(2)

tests = [
    ('Core API UUID', 'http://localhost:8000/api/core/students/9bbcc9f4-bfe8-450f-b2fa-95f567625681'),
    ('Analytics UUID', 'http://localhost:8000/api/analytics/students/9bbcc9f4-bfe8-450f-b2fa-95f567625681/performance'),
    ('Student Model UUID', 'http://localhost:8000/api/student-model/student/9bbcc9f4-bfe8-450f-b2fa-95f567625681/bkt/states/all'),
    ('Competitive API', 'http://localhost:8000/api/competitive/v1/subjects'),
    ('Practice Stats', 'http://localhost:8000/api/practice/api/v1/practice/9bbcc9f4-bfe8-450f-b2fa-95f567625681/stats'),
    ('Health Check', 'http://localhost:8000/api/health'),
    ('Frontend Dashboard', 'http://localhost:8000/api/frontend/dashboard/student/9bbcc9f4-bfe8-450f-b2fa-95f567625681'),
]

success_count = 0
total_tests = len(tests)

for test_name, url in tests:
    try:
        response = requests.get(url, headers={'Origin': 'http://localhost:5000'}, timeout=10)
        if response.status_code == 200:
            print(f'✅ {test_name}: SUCCESS ({response.status_code})')
            success_count += 1
        else:
            print(f'⚠️  {test_name}: {response.status_code}')
    except Exception as e:
        print(f'❌ {test_name}: ERROR - {str(e)[:50]}...')

print('=' * 50)
print(f'🎯 Results: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}% success)')

if success_count == total_tests:
    print('🎉 ALL TESTS PASSED! 100% SUCCESS!')
elif success_count >= total_tests * 0.8:
    print('✅ Great improvement! Most APIs are working!')
else:
    print('⚠️  Still some issues to resolve.')