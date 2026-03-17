import requests
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

# 搜索今日新闻
url = 'https://api.duckduckgo.com/'
params = {'q': f'{today} news headlines', 'format': 'json'}

r = requests.get(url, params=params, timeout=10)
data = r.json()

print(f'📅 Today: {today}')
print('='*50)
print(f'📰 Heading: {data.get("Heading", "N/A")}')
print(f'📌 Abstract: {data.get("AbstractText", "No abstract available")}')
print(f'🔗 URL: {data.get("AbstractURL", "N/A")}')

if data.get('RelatedTopics'):
    print('\n📚 Related Topics:')
    for i, t in enumerate(data['RelatedTopics'][:6], 1):
        if isinstance(t, dict) and t.get('Text'):
            text = t['Text'][:100]
            print(f'  {i}. {text}')