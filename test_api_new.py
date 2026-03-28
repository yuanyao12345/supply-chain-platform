import requests

# 测试新闻API
print('Testing news API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/news/1')
    print('Status:', response.status_code)
    print('Content:', response.text)
except Exception as e:
    print(f'Error: {e}')

# 测试案例API
print('\nTesting cases API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/cases')
    print('Status:', response.status_code)
    print('Content:', response.text)
except Exception as e:
    print(f'Error: {e}')

# 测试政策API
print('\nTesting policies API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/policies')
    print('Status:', response.status_code)
    print('Content:', response.text)
except Exception as e:
    print(f'Error: {e}')

# 测试测试API
print('\nTesting test API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/test')
    print('Status:', response.status_code)
    print('Content:', response.text)
except Exception as e:
    print(f'Error: {e}')
