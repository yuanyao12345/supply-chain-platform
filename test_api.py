import requests

response = requests.get('http://127.0.0.1:5002/api/news/1')
print('Status:', response.status_code)
data = response.json()
print('News count:', len(data))
for i, item in enumerate(data):
    print(f'{i+1}. {item["title"]} - {item["source"]}')
    print(f'   Link: {item["link"]}')
