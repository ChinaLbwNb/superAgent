import requests
import xml.etree.ElementTree as ET
from datetime import datetime

url = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

r = requests.get(url, headers=headers, timeout=15)
r.encoding = 'utf-8'

# 保存原始内容用于调试
with open('news_raw.xml', 'w', encoding='utf-8') as f:
    f.write(r.text[:5000])

print(f'Google News - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
print('='*60)

try:
    root = ET.fromstring(r.content)
    channel = root.find('channel')
    items = channel.findall('item')[:10]
    
    for i, item in enumerate(items, 1):
        title_elem = item.find('title')
        if title_elem is not None:
            title = title_elem.text or ''
            # 清理标题中的来源标记
            if ' - ' in title:
                title = title.rsplit(' - ', 1)[0]
            print(f'{i}. {title[:60]}')
except Exception as e:
    print(f'Parse error: {e}')
    # 直接用正则提取
    import re
    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)[1:11]
    for i, title in enumerate(titles, 1):
        if ' - ' in title:
            title = title.rsplit(' - ', 1)[0]
        print(f'{i}. {title[:60]}')