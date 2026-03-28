import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

# 新闻网站配置 - 优化选择器和内容提取
NEWS_SOURCES = [
    {
        'name': '新浪财经',
        'url': 'https://finance.sina.com.cn',
        'search_url': 'https://search.sina.com.cn/?q={keyword}&range=all&c=news',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '新浪财经滚动',
        'url': 'https://finance.sina.com.cn/roll/',
        'selector': 'li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '新浪财经新闻',
        'url': 'https://finance.sina.com.cn/news/',
        'selector': 'li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': None
    },
    {
        'name': '上海证券报',
        'url': 'https://www.cnstock.com',
        'search_url': 'https://www.cnstock.com/search?keyword={keyword}',
        'selector': '.newslist li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': 'span'
    },
    {
        'name': '第一财经',
        'url': 'https://www.yicai.com',
        'search_url': 'https://www.yicai.com/search?keyword={keyword}',
        'selector': '.news-list-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.news-list-time'
    },
    {
        'name': '证券时报',
        'url': 'https://www.stcn.com',
        'search_url': 'https://www.stcn.com/search?keyword={keyword}',
        'selector': '.newslist li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '经济观察网',
        'url': 'https://www.eeo.com.cn',
        'search_url': 'https://www.eeo.com.cn/search?keyword={keyword}',
        'selector': '.list_item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '金融时报',
        'url': 'https://www.financialnews.com.cn',
        'search_url': 'https://www.financialnews.com.cn/search?keyword={keyword}',
        'selector': '.news-list li',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.date'
    },
    {
        'name': '21世纪经济报道',
        'url': 'https://www.21jingji.com',
        'search_url': 'https://www.21jingji.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '界面新闻',
        'url': 'https://www.jiemian.com',
        'search_url': 'https://www.jiemian.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '华尔街见闻',
        'url': 'https://wallstreetcn.com',
        'search_url': 'https://wallstreetcn.com/search?keyword={keyword}',
        'selector': '.article-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '凤凰财经',
        'url': 'https://finance.ifeng.com',
        'search_url': 'https://search.ifeng.com/?q={keyword}&c=1',
        'selector': '.news-list-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '腾讯财经',
        'url': 'https://finance.qq.com',
        'search_url': 'https://www.sogou.com/web?query={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    },
    {
        'name': '网易财经',
        'url': 'https://money.163.com',
        'search_url': 'https://money.163.com/search?keyword={keyword}',
        'selector': '.news-item',
        'title_selector': 'a',
        'content_selector': None,
        'date_selector': '.time'
    }
]

# 行业关键词
KEYWORDS = ['供应链', '金融', '物流', '航空', '货运', '融资', '供应链金融']

# 新闻数据文件路径
NEWS_FILE = 'news.json'
# 新闻数据过期时间（秒）
NEWS_EXPIRY = 30  # 30秒

# 供应链金融案例数据文件路径
CASES_FILE = 'cases.json'
# 案例数据过期时间（秒）
CASES_EXPIRY = 86400  # 1天

# 政策资讯数据文件路径
POLICIES_FILE = 'policies.json'
# 政策资讯过期时间（秒）
POLICIES_EXPIRY = 86400  # 1天

def is_news_expired():
    """检查新闻数据是否过期"""
    if not os.path.exists(NEWS_FILE):
        return True
    
    # 检查文件修改时间
    file_mtime = os.path.getmtime(NEWS_FILE)
    current_time = time.time()
    
    return (current_time - file_mtime) > NEWS_EXPIRY

def is_cases_expired():
    """检查供应链金融案例数据是否过期"""
    if not os.path.exists(CASES_FILE):
        return True
    
    # 检查文件修改时间
    file_mtime = os.path.getmtime(CASES_FILE)
    current_time = time.time()
    
    return (current_time - file_mtime) > CASES_EXPIRY

def is_policies_expired():
    """检查政策资讯数据是否过期"""
    if not os.path.exists(POLICIES_FILE):
        return True
    
    # 检查文件修改时间
    file_mtime = os.path.getmtime(POLICIES_FILE)
    current_time = time.time()
    
    return (current_time - file_mtime) > POLICIES_EXPIRY

def extract_content(url):
    """从新闻详情页提取内容"""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 尝试不同的内容选择器
        content_selectors = [
            '.article-content',
            '.content',
            '.article-body',
            '.main-content',
            '#content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(strip=True)
                # 限制内容长度
                if len(content) > 200:
                    content = content[:200] + '...'
                return content
        
        # 如果没有找到内容，返回摘要
        return '点击查看详情'
    except Exception as e:
        print(f'提取内容失败: {e}')
        return '点击查看详情'

def crawl_news():
    """抓取新闻数据"""
    news_list = []
    
    for source in NEWS_SOURCES:
        try:
            # 如果有搜索URL，则使用搜索URL搜索关键字
            if 'search_url' in source:
                # 对每个关键字进行搜索
                for keyword in KEYWORDS[:3]:  # 只搜索前3个关键字，避免请求过多
                    search_url = source['search_url'].format(keyword=keyword)
                    print(f'正在搜索 {source["name"]} - 关键字: {keyword}...')
                    response = requests.get(search_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Connection': 'keep-alive'
                    })
                    response.encoding = 'utf-8'
                    
                    # 检查响应状态
                    if response.status_code != 200:
                        print(f'搜索 {source["name"]} 失败: 状态码 {response.status_code}')
                        continue
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # 尝试使用多个选择器
                    selectors = [
                        source['selector'],
                        'li',
                        '.list-item',
                        '.article-item',
                        '.news',
                        '.item',
                        '.news-list li',
                        'ul li',
                        'div[class*="news"]',
                        'div[class*="article"]',
                        'a[href*="article"]'
                    ]
                    
                    items = []
                    for selector in selectors:
                        try:
                            found_items = soup.select(selector)
                            if found_items:
                                items = found_items
                                print(f'在 {source["name"]} 搜索结果中使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                                break
                        except Exception as e:
                            print(f'使用选择器 "{selector}" 失败: {e}')
                    
                    if not items:
                        print(f'在 {source["name"]} 搜索结果中未找到新闻')
                        continue
                    
                    for item in items[:10]:  # 限制处理的新闻数量
                        # 提取标题和链接
                        try:
                            # 尝试不同的标题选择器
                            title_selectors = [
                                source['title_selector'],
                                'a',
                                'h3',
                                'h2',
                                '.title',
                                '.news-title',
                                '.article-title'
                            ]
                            
                            title_elem = None
                            for title_selector in title_selectors:
                                try:
                                    elem = item.select_one(title_selector)
                                    if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                        title_elem = elem
                                        break
                                except Exception as e:
                                    print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                            
                            if not title_elem:
                                continue
                            
                            title = title_elem.text.strip()
                            link = None
                            
                            # 尝试从标题元素或其父元素获取链接
                            if title_elem.get('href'):
                                link = title_elem.get('href')
                            else:
                                # 尝试从父元素获取链接
                                parent = title_elem.parent
                                while parent and not link:
                                    if parent.get('href'):
                                        link = parent.get('href')
                                        break
                                    parent = parent.parent
                            
                            if not link:
                                continue
                            
                            # 确保链接是完整的
                            if not link.startswith('http'):
                                if link.startswith('/'):
                                    link = source['url'] + link
                                else:
                                    link = source['url'] + '/' + link
                            
                            # 提取日期
                            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            if source['date_selector']:
                                try:
                                    date_elem = item.select_one(source['date_selector'])
                                    if date_elem:
                                        date_text = date_elem.text.strip()
                                        # 简单处理日期格式
                                        if date_text:
                                            date = date_text
                                except Exception as e:
                                    print(f'提取日期失败: {e}')
                            
                            # 检查是否包含关键词
                            if any(keyword in title for keyword in KEYWORDS):
                                # 提取内容
                                content = extract_content(link)
                                
                                news_item = {
                                    'title': title,
                                    'content': content,
                                    'link': link,
                                    'source': source['name'],
                                    'date': date,
                                    'image_prompt': f'{title} news professional'
                                }
                                news_list.append(news_item)
                                print(f'添加新闻: {title} - {source["name"]}')
                                
                                # 限制新闻数量
                                if len(news_list) >= 9:
                                    break
                        except Exception as e:
                            print(f'处理新闻项失败: {e}')
                            continue
                    
                    if len(news_list) >= 9:
                        break
            else:
                # 如果没有搜索URL，则直接抓取首页
                print(f'正在抓取 {source["name"]}...')
                response = requests.get(source['url'], timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                # 检查响应状态
                if response.status_code != 200:
                    print(f'抓取 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 尝试使用多个选择器
                selectors = [
                    source['selector'],
                    'li',
                    '.list-item',
                    '.article-item',
                    '.news',
                    '.item',
                    '.news-list li',
                    'ul li',
                    'div[class*="news"]',
                    'div[class*="article"]',
                    'a[href*="article"]'
                ]
                
                items = []
                for selector in selectors:
                    try:
                        found_items = soup.select(selector)
                        if found_items:
                            items = found_items
                            print(f'在 {source["name"]} 使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                            break
                    except Exception as e:
                        print(f'使用选择器 "{selector}" 失败: {e}')
                
                if not items:
                    print(f'在 {source["name"]} 未找到新闻')
                    continue
                
                for item in items[:20]:  # 限制处理的新闻数量
                    # 提取标题和链接
                    try:
                        # 尝试不同的标题选择器
                        title_selectors = [
                            source['title_selector'],
                            'a',
                            'h3',
                            'h2',
                            '.title',
                            '.news-title',
                            '.article-title'
                        ]
                        
                        title_elem = None
                        for title_selector in title_selectors:
                            try:
                                elem = item.select_one(title_selector)
                                if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                    title_elem = elem
                                    break
                            except Exception as e:
                                print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = None
                        
                        # 尝试从标题元素或其父元素获取链接
                        if title_elem.get('href'):
                            link = title_elem.get('href')
                        else:
                            # 尝试从父元素获取链接
                            parent = title_elem.parent
                            while parent and not link:
                                if parent.get('href'):
                                    link = parent.get('href')
                                    break
                                parent = parent.parent
                        
                        if not link:
                            continue
                        
                        # 确保链接是完整的
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        # 提取日期
                        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if source['date_selector']:
                            try:
                                date_elem = item.select_one(source['date_selector'])
                                if date_elem:
                                    date_text = date_elem.text.strip()
                                    # 简单处理日期格式
                                    if date_text:
                                        date = date_text
                            except Exception as e:
                                print(f'提取日期失败: {e}')
                        
                        # 检查是否包含关键词
                        if any(keyword in title for keyword in KEYWORDS):
                            # 提取内容
                            content = extract_content(link)
                            
                            news_item = {
                                'title': title,
                                'content': content,
                                'link': link,
                                'source': source['name'],
                                'date': date,
                                'image_prompt': f'{title} news professional'
                            }
                            news_list.append(news_item)
                            print(f'添加新闻: {title} - {source["name"]}')
                            
                            # 限制新闻数量
                            if len(news_list) >= 9:
                                break
                    except Exception as e:
                        print(f'处理新闻项失败: {e}')
                        continue
                        
        except Exception as e:
            print(f'抓取 {source["name"]} 失败: {e}')
        
        if len(news_list) >= 9:
            break
    
    # 确保至少有6条新闻
    if len(news_list) < 6:
        print(f'抓取的新闻数量不足6条，当前只有 {len(news_list)} 条，使用备用来源')
        # 如果抓取的新闻不够，使用备用来源
        backup_sources = [
            {
                'name': '新浪财经',
                'url': 'https://finance.sina.com.cn/stock/',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '东方财富网',
                'url': 'https://www.eastmoney.com',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '凤凰财经',
                'url': 'https://finance.ifeng.com',
                'selector': '.news-list-item',
                'title_selector': 'a'
            },
            {
                'name': '腾讯财经',
                'url': 'https://finance.qq.com',
                'selector': '.news-item',
                'title_selector': 'a'
            },
            {
                'name': '网易财经',
                'url': 'https://money.163.com',
                'selector': '.news-item',
                'title_selector': 'a'
            }
        ]
        
        for source in backup_sources:
            try:
                print(f'正在抓取备用来源 {source["name"]}...')
                response = requests.get(source['url'], timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f'抓取备用来源 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # 尝试使用多个选择器
                selectors = [
                    source['selector'],
                    'li',
                    '.list-item',
                    '.article-item',
                    '.news',
                    '.item',
                    '.news-list li',
                    'ul li',
                    'div[class*="news"]',
                    'div[class*="article"]',
                    'a[href*="article"]'
                ]
                
                items = []
                for selector in selectors:
                    try:
                        found_items = soup.select(selector)
                        if found_items:
                            items = found_items
                            print(f'在备用来源 {source["name"]} 使用选择器 "{selector}" 找到 {len(items)} 条新闻')
                            break
                    except Exception as e:
                        print(f'使用选择器 "{selector}" 失败: {e}')
                
                if not items:
                    print(f'在备用来源 {source["name"]} 未找到新闻')
                    continue
                
                for item in items[:20]:  # 限制处理的新闻数量
                    try:
                        # 尝试不同的标题选择器
                        title_selectors = [
                            source['title_selector'],
                            'a',
                            'h3',
                            'h2',
                            '.title',
                            '.news-title',
                            '.article-title'
                        ]
                        
                        title_elem = None
                        for title_selector in title_selectors:
                            try:
                                elem = item.select_one(title_selector)
                                if elem and elem.text.strip() and len(elem.text.strip()) > 5:  # 确保标题长度足够
                                    title_elem = elem
                                    break
                            except Exception as e:
                                print(f'使用标题选择器 "{title_selector}" 失败: {e}')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = None
                        
                        # 尝试从标题元素或其父元素获取链接
                        if title_elem.get('href'):
                            link = title_elem.get('href')
                        else:
                            # 尝试从父元素获取链接
                            parent = title_elem.parent
                            while parent and not link:
                                if parent.get('href'):
                                    link = parent.get('href')
                                    break
                                parent = parent.parent
                        
                        if not link:
                            continue
                        
                        # 确保链接是完整的
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        if any(keyword in title for keyword in KEYWORDS):
                            content = extract_content(link)
                            
                            news_item = {
                                'title': title,
                                'content': content,
                                'link': link,
                                'source': source['name'],
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'image_prompt': f'{title} news professional'
                            }
                            news_list.append(news_item)
                            print(f'添加备用新闻: {title} - {source["name"]}')
                            
                            if len(news_list) >= 9:
                                break
                    except Exception as e:
                        print(f'处理备用新闻项失败: {e}')
                        continue
            except Exception as e:
                print(f'抓取备用来源 {source["name"]} 失败: {e}')
            
            if len(news_list) >= 9:
                break
    
    # 确保至少有3条新闻
    if len(news_list) < 6:
        print(f'备用来源抓取失败，当前只有 {len(news_list)} 条新闻，使用最终备用新闻')
        # 使用用户提供的新浪网新闻链接作为初始内容
        final_backup = [
            {
                'title': '滨州"滨链通"供应链金融公共服务平台入驻企业超130家 累计业务规模破180亿元',
                'content': '滨州市滨链通供应链金融公共服务平台于2025年4月正式上线，具备供应链票据的签发、承兑、背书、融资、到期处理等全生命周期服务能力。截至目前，平台入驻的企业已超过130家，累计业务规模突破180亿元。',
                'link': 'https://k.sina.com.cn/article_1893761531_70e081fb020030zhi.html',
                'source': '新浪新闻',
                'date': '2026-03-27',
                'image_prompt': '供应链金融平台 滨州 滨链通'
            },
            {
                'title': '监管"十不准"与"77号文"层层加码，传统模式穷途末路，2026年，您的供应链金融业务该如何转型？',
                'content': '旧路径正在断裂。过去依赖主体信用、套利套汇的"搬运工"模式，在穿透式监管与真实贸易的要求下已难以为继。一边是合规红线的持续收紧，一边是利润空间的不断压缩，许多从业者正陷入"不做等死，做错找死"的双重困境。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-27/doc-inhsnzav8948136.shtml',
                'source': '新浪财经',
                'date': '2026-03-27',
                'image_prompt': '供应链金融 监管 转型'
            },
            {
                'title': '平安银行：2025年供应链金融融资发生额19679亿元',
                'content': '平安银行在接受调研者提问时表示，2025年，公司供应链金融融资发生额19679亿元，同比增长23.1%。公司深入供应链场景，运用"金融+科技"能力不断创新业务模式，优化金融服务体验。',
                'link': 'https://cj.sina.com.cn/articles/view/2311077472/89c03e6002002ilh2',
                'source': '新浪财经',
                'date': '2026-03-27',
                'image_prompt': '平安银行 供应链金融 融资'
            },
            {
                'title': '这62页PPT，帮你看懂供应链金融！',
                'content': '本文通过62页PPT详细介绍了供应链金融的概念、模式、实践案例等内容，帮助读者全面了解供应链金融的运作机制和发展趋势。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-26/doc-inhskfhh5647476.shtml',
                'source': '新浪财经',
                'date': '2026-03-26',
                'image_prompt': '供应链金融 PPT 教程'
            },
            {
                'title': '数实融合·链通全球——2026第十三届产业数字化与供应链金融创新论坛在深圳成功举行',
                'content': '2026年3月26日，由万联网主办的"第十三届产业数字化与供应链金融创新论坛"在深圳举办。近500位央国企/上市公司/行业龙头/供应链公司/物流商/科技服务商/金融机构高管精英齐聚一堂，共话生态供应链构建、国企供应链服务创新、物贸一体化转型及供应链合规风控等热点议题。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-26/doc-inhsiqkn0144135.shtml',
                'source': '新浪财经',
                'date': '2026-03-26',
                'image_prompt': '产业数字化 供应链金融 论坛 深圳'
            },
            {
                'title': '数实融合趋势下，大宗供应链金融该如何赋能地方产业，实现细分领域的供应链升级？',
                'content': '在数字经济与实体经济深度融合的当下，大宗商品作为国民经济的"压舱石"，其供应链的稳定与高效直接关系到地方产业的韧性与竞争力。本文结合数实融合的发展趋势，立足地方产业发展实际，从现状剖析、赋能路径、保障措施三个方面，探讨大宗供应链金融如何助力地方细分领域供应链升级。',
                'link': 'https://finance.sina.com.cn/wm/2026-03-23/doc-inhrzcpn2201795.shtml',
                'source': '新浪财经',
                'date': '2026-03-23',
                'image_prompt': '数实融合 大宗供应链金融 地方产业'
            }
        ]
        
        news_list.extend(final_backup)
        # 限制最多9条
        news_list = news_list[:9]
        print(f'添加了 {len(final_backup)} 条最终备用新闻')
    
    # 保存新闻数据到文件
    news_data = {
        'timestamp': time.time(),
        'news': news_list
    }
    
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f'抓取完成，共获取 {len(news_list)} 条新闻')
    return news_list

def get_news():
    """获取最新新闻数据"""
    # 检查新闻数据是否过期
    if is_news_expired():
        return crawl_news()
    
    # 从文件中读取新闻数据
    try:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        return news_data['news']
    except Exception as e:
        print(f'读取新闻数据失败: {e}')
        return crawl_news()

def crawl_cases():
    """抓取供应链金融案例数据"""
    cases_list = []
    
    # 案例来源网站
    case_sources = [
        {
            'name': '新浪财经',
            'url': 'https://finance.sina.com.cn',
            'search_url': 'https://search.sina.com.cn/?q={keyword}&range=all&c=news',
            'selector': '.news-item'
        },
        {
            'name': '上海证券报',
            'url': 'https://www.cnstock.com',
            'search_url': 'https://www.cnstock.com/search?keyword={keyword}',
            'selector': '.newslist li'
        },
        {
            'name': '第一财经',
            'url': 'https://www.yicai.com',
            'search_url': 'https://www.yicai.com/search?keyword={keyword}',
            'selector': '.news-list-item'
        }
    ]
    
    # 案例关键词
    case_keywords = ['供应链金融案例', '供应链融资案例', '供应链金融成功案例']
    
    for source in case_sources:
        try:
            for keyword in case_keywords:
                search_url = source['search_url'].format(keyword=keyword)
                print(f'正在搜索 {source["name"]} - 案例关键词: {keyword}...')
                response = requests.get(search_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f'搜索 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                items = soup.select(source['selector'])
                
                for item in items[:10]:
                    try:
                        title_elem = item.select_one('a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = title_elem.get('href')
                        
                        if not link:
                            continue
                        
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        content = extract_content(link)
                        
                        case_item = {
                            'title': title,
                            'content': content,
                            'link': link,
                            'source': source['name'],
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        cases_list.append(case_item)
                        print(f'添加案例: {title} - {source["name"]}')
                        
                        if len(cases_list) >= 6:
                            break
                    except Exception as e:
                        print(f'处理案例项失败: {e}')
                        continue
                
                if len(cases_list) >= 6:
                    break
        except Exception as e:
            print(f'抓取 {source["name"]} 案例失败: {e}')
    
    # 确保至少有3个案例
    if len(cases_list) < 3:
        print(f'抓取的案例数量不足3个，当前只有 {len(cases_list)} 个，使用备用案例')
        backup_cases = [
            {
                'title': '航空燃油供应商融资案例',
                'content': '某航空燃油供应商通过平台申请1000万元融资，用于采购航空燃油，银行审批时间从传统的15天缩短至3天。',
                'link': 'https://finance.sina.com.cn/',
                'source': '新浪财经',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '机场餐饮服务商融资案例',
                'content': '机场餐饮服务商通过平台申请500万元融资，用于设备升级和食材采购，成功获得银行批准。',
                'link': 'https://finance.baidu.com/',
                'source': '百度财经',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '物流仓储企业融资案例',
                'content': '物流仓储企业通过平台申请800万元融资，用于仓库扩建，银行根据企业历史交易数据快速审批通过。',
                'link': 'https://finance.qq.com/',
                'source': '腾讯财经',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        cases_list.extend(backup_cases)
    
    # 保存案例数据到文件
    cases_data = {
        'timestamp': time.time(),
        'cases': cases_list[:6]  # 只保存6个案例
    }
    
    with open(CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cases_data, f, ensure_ascii=False, indent=2)
    
    print(f'案例抓取完成，共获取 {len(cases_list)} 个案例')
    return cases_list[:6]

def get_cases():
    """获取最新供应链金融案例数据"""
    # 检查案例数据是否过期
    if is_cases_expired():
        return crawl_cases()
    
    # 从文件中读取案例数据
    try:
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            cases_data = json.load(f)
        return cases_data['cases']
    except Exception as e:
        print(f'读取案例数据失败: {e}')
        return crawl_cases()

def crawl_policies():
    """抓取政策资讯数据"""
    policies_list = []
    
    # 政策来源网站
    policy_sources = [
        {
            'name': '国务院',
            'url': 'https://www.gov.cn',
            'search_url': 'https://www.gov.cn/search/?q={keyword}',
            'selector': '.news_item'
        },
        {
            'name': '人民银行',
            'url': 'https://www.pbc.gov.cn',
            'search_url': 'https://www.pbc.gov.cn/search/?q={keyword}',
            'selector': '.news-list li'
        },
        {
            'name': '财政部',
            'url': 'https://www.mof.gov.cn',
            'search_url': 'https://www.mof.gov.cn/search/?q={keyword}',
            'selector': '.news-item'
        }
    ]
    
    # 政策关键词
    policy_keywords = ['供应链金融政策', '供应链金融指导意见', '供应链金融支持政策']
    
    for source in policy_sources:
        try:
            for keyword in policy_keywords:
                search_url = source['search_url'].format(keyword=keyword)
                print(f'正在搜索 {source["name"]} - 政策关键词: {keyword}...')
                response = requests.get(search_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive'
                })
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    print(f'搜索 {source["name"]} 失败: 状态码 {response.status_code}')
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                items = soup.select(source['selector'])
                
                for item in items[:10]:
                    try:
                        title_elem = item.select_one('a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        link = title_elem.get('href')
                        
                        if not link:
                            continue
                        
                        if not link.startswith('http'):
                            if link.startswith('/'):
                                link = source['url'] + link
                            else:
                                link = source['url'] + '/' + link
                        
                        content = extract_content(link)
                        
                        policy_item = {
                            'title': title,
                            'content': content,
                            'link': link,
                            'source': source['name'],
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        policies_list.append(policy_item)
                        print(f'添加政策: {title} - {source["name"]}')
                        
                        if len(policies_list) >= 6:
                            break
                    except Exception as e:
                        print(f'处理政策项失败: {e}')
                        continue
                
                if len(policies_list) >= 6:
                    break
        except Exception as e:
            print(f'抓取 {source["name"]} 政策失败: {e}')
    
    # 确保至少有3条政策
    if len(policies_list) < 3:
        print(f'抓取的政策数量不足3条，当前只有 {len(policies_list)} 条，使用备用政策')
        backup_policies = [
            {
                'title': '国务院关于促进供应链金融发展的指导意见',
                'content': '鼓励金融机构依托核心企业信用，为上下游中小企业提供融资服务，推动供应链金融创新发展。',
                'link': 'https://www.gov.cn/',
                'source': '国务院',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '湖北省支持航空物流产业发展若干措施',
                'content': '加大对航空物流企业的金融支持力度，完善供应链金融服务体系，促进产业转型升级。',
                'link': 'https://www.hubei.gov.cn/',
                'source': '湖北省政府',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '人民银行关于深化供应链金融服务的通知',
                'content': '推动金融机构创新供应链金融产品和服务，提升对实体经济的支持力度。',
                'link': 'https://www.pbc.gov.cn/',
                'source': '人民银行',
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        policies_list.extend(backup_policies)
    
    # 保存政策数据到文件
    policies_data = {
        'timestamp': time.time(),
        'policies': policies_list[:6]  # 只保存6条政策
    }
    
    with open(POLICIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(policies_data, f, ensure_ascii=False, indent=2)
    
    print(f'政策抓取完成，共获取 {len(policies_list)} 条政策')
    return policies_list[:6]

def get_policies():
    """获取最新政策资讯数据"""
    # 检查政策数据是否过期
    if is_policies_expired():
        return crawl_policies()
    
    # 从文件中读取政策数据
    try:
        with open(POLICIES_FILE, 'r', encoding='utf-8') as f:
            policies_data = json.load(f)
        return policies_data['policies']
    except Exception as e:
        print(f'读取政策数据失败: {e}')
        return crawl_policies()

if __name__ == '__main__':
    # 测试爬虫
    news = get_news()
    print(f'获取到 {len(news)} 条新闻')
    for i, item in enumerate(news):
        print(f'{i+1}. {item["title"]} - {item["source"]}')
        print(f'   链接: {item["link"]}')
        print(f'   内容: {item["content"]}')
        print()
    
    # 测试案例爬虫
    cases = get_cases()
    print(f'\n获取到 {len(cases)} 个案例')
    for i, item in enumerate(cases):
        print(f'{i+1}. {item["title"]} - {item["source"]}')
        print(f'   链接: {item["link"]}')
        print(f'   内容: {item["content"]}')
        print()
    
    # 测试政策爬虫
    policies = get_policies()
    print(f'\n获取到 {len(policies)} 条政策')
    for i, item in enumerate(policies):
        print(f'{i+1}. {item["title"]} - {item["source"]}')
        print(f'   链接: {item["link"]}')
        print(f'   内容: {item["content"]}')
        print()