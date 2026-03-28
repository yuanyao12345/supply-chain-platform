import requests

# 测试案例API
print('Testing cases API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/cases')
    print('Status:', response.status_code)
    data = response.json()
    print('Cases count:', len(data))
    for i, item in enumerate(data):
        print(f'{i+1}. {item["title"]}')
        print(f'   Source: {item["source"]}')
        print(f'   Link: {item["link"]}')
        print()
except Exception as e:
    print(f'Error: {e}')

# 测试政策API
print('\nTesting policies API...')
try:
    response = requests.get('http://127.0.0.1:5002/api/policies')
    print('Status:', response.status_code)
    data = response.json()
    print('Policies count:', len(data))
    for i, item in enumerate(data):
        print(f'{i+1}. {item["title"]}')
        print(f'   Source: {item["source"]}')
        print(f'   Link: {item["link"]}')
        print()
except Exception as e:
    print(f'Error: {e}')
